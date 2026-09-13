import { createDatabase } from "./db.js";
// Explicit live verification; never part of CI. Every test transaction rolls back.
import sql from "mssql";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import request from "supertest";
import { executeAction } from "./actions.js";
import { createApp } from "./app.js";
const pool = await new sql.ConnectionPool({
  server: process.env.SQL_SERVER,
  database: process.env.SQL_DATABASE,
  user: process.env.SQL_USER,
  password: process.env.SQL_PASSWORD,
  options: { encrypt: true, trustServerCertificate: false },
  connectionTimeout: 60000,
  requestTimeout: 30000,
}).connect();
const candidate = (
  await pool.request()
    .query(`SELECT TOP(1) o.order_id,o.updated_at FROM app.orders o
 WHERE status='PAID' AND (SELECT COUNT(*) FROM app.order_lines l WHERE l.order_id=o.order_id)>1 ORDER BY o.order_id;`)
).recordset[0];
assert.ok(candidate, "Need a paid order with multiple lines");
const id = candidate.order_id;
async function scoped(fn) {
  const tx = new sql.Transaction(pool);
  let rolledBack = false;
  tx.on("rollback", () => {
    rolledBack = true;
  });
  await tx.begin();
  try {
    await fn(tx);
  } finally {
    if (!rolledBack) await tx.rollback();
  }
}
const command = (action, version, extra = {}) => ({
  action,
  requestId: randomUUID(),
  expectedUpdatedAt: new Date(version).toISOString(),
  reason: "Rollback-only integration verification",
  ...extra,
});
const read = async (tx) =>
  (
    await new sql.Request(tx).input("id", sql.NVarChar(40), id)
      .query(`SELECT * FROM app.orders WHERE order_id=@id;
 SELECT * FROM app.order_lines WHERE order_id=@id ORDER BY order_line_id;
 SELECT * FROM app.refunds WHERE order_id=@id; SELECT * FROM app.shipments WHERE order_id=@id;
 SELECT * FROM app.audit_log WHERE entity_type='order' AND entity_id=@id AND operation='ACTION';`)
  ).recordsets;
try {
  await scoped(async (tx) => {
    const agent = request.agent(
      createApp({
        password: "test",
        secret: "a".repeat(32),
        database: { action: (orderId, c) => executeAction(tx, orderId, c) },
      }),
    );
    await agent.post("/api/login").send({ password: "test" });
    async function post(c) {
      const r = await agent
        .post(`/api/orders/${id}/actions`)
        .set("X-Order-Action", "1")
        .send(c);
      assert.equal(r.status, 200, JSON.stringify(r.body));
      return r.body;
    }
    let [orders, lines] = await read(tx);
    const ship = command("ship", orders[0].updated_at, {
      carrier: "TEST",
      trackingNumber: randomUUID(),
    });
    assert.equal((await post(ship)).replayed, false);
    assert.equal((await post(ship)).replayed, true);
    let data = await read(tx);
    assert.equal(data[0][0].status, "SHIPPED");
    assert.equal(data[3].length, 1);
    assert.equal(data[4].length, 1);
    const delivery = command("deliver", data[0][0].updated_at);
    await post(delivery);
    data = await read(tx);
    assert.equal(data[0][0].status, "DELIVERED");
    assert.ok(data[3][0].delivered_at);
    const partial = command("return", data[0][0].updated_at, {
      lineIds: [lines[0].order_line_id],
    });
    await post(partial);
    await post(partial);
    data = await read(tx);
    assert.equal(data[0][0].status, "PARTIALLY_RETURNED");
    assert.equal(data[2].length, 1);
    assert.equal(
      Math.round(data[2][0].refund_amount * 100),
      Math.round((lines[0].line_total + lines[0].tax_amount) * 100),
    );
    await post(
      command("return", data[0][0].updated_at, {
        lineIds: lines.slice(1).map((l) => l.order_line_id),
      }),
    );
    data = await read(tx);
    assert.equal(data[0][0].status, "RETURNED");
    assert.equal(data[4].length, 4);
    assert.equal(
      Math.round(data[2].reduce((n, r) => n + r.refund_amount, 0) * 100),
      Math.round(orders[0].total_amount * 100),
    );
    const audits = (
      await new sql.Request(tx).input("id", sql.NVarChar(40), id)
        .query(`SELECT COUNT(*) n FROM app.audit_log WHERE user_id='portal-operator' AND
      ((entity_type='order' AND entity_id=@id) OR (entity_type='shipment' AND entity_id IN(SELECT shipment_id FROM app.shipments WHERE order_id=@id))
      OR (entity_type='refund' AND entity_id IN(SELECT refund_id FROM app.refunds WHERE order_id=@id)));`)
    ).recordset[0].n;
    assert.equal(audits, 12);
  });
  console.log(
    "PASS: authenticated API -> live SQL ship, delivery, partial/full return; exact totals; 12 audit entries; replay; all rolled back",
  );
  for (const [name, make] of [
    [
      "stale version",
      () =>
        command("ship", "2000-01-01T00:00:00.000Z", {
          carrier: "TEST",
          trackingNumber: randomUUID(),
        }),
    ],
    ["invalid transition", () => command("deliver", candidate.updated_at)],
  ])
    await scoped(async (tx) => {
      await assert.rejects(
        executeAction(tx, id, make()),
        (e) => e.number === 51000,
      );
      console.log("PASS: " + name);
    });
  await scoped(async (tx) => {
    const ship = command("ship", candidate.updated_at, {
      carrier: "TEST",
      trackingNumber: randomUUID(),
    });
    await executeAction(tx, id, ship);
    await assert.rejects(
      executeAction(tx, id, { ...ship, reason: "Changed payload" }),
      (e) => e.number === 51000,
    );
  });
  console.log(
    "PASS: conflicting reuse rejected; preceding writes rolled back with failure",
  );
  await scoped(async (tx) => {
    await executeAction(
      tx,
      id,
      command("ship", candidate.updated_at, {
        carrier: "TEST",
        trackingNumber: randomUUID(),
      }),
    );
    await scoped(async (other) => {
      await new sql.Request(other).query("SET LOCK_TIMEOUT 1000;");
      await assert.rejects(
        executeAction(
          other,
          id,
          command("ship", candidate.updated_at, {
            carrier: "TEST",
            trackingNumber: randomUUID(),
          }),
        ),
        (e) => e.number === 1222,
      );
    });
  });
  console.log("PASS: competing connection cannot mutate locked order");
  const delivered = (
    await pool.request()
      .query(`SELECT TOP(1) o.order_id,o.updated_at,l.order_line_id,l.line_total,l.tax_amount
    FROM app.orders o JOIN app.order_lines l ON l.order_id=o.order_id WHERE o.status='DELIVERED'
    AND l.tax_amount>0 AND (l.discount_amount+l.order_discount_amount)>0 ORDER BY o.order_id;`)
  ).recordset[0];
  assert.ok(delivered);
  await scoped(async (tx) => {
    const c = command("return", delivered.updated_at, {
      lineIds: [delivered.order_line_id],
    });
    await executeAction(tx, delivered.order_id, c);
    const refund = (
      await tx
        .request()
        .input("id", sql.NVarChar(40), delivered.order_id)
        .query("SELECT refund_amount FROM app.refunds WHERE order_id=@id;")
    ).recordset[0];
    assert.equal(
      Math.round(refund.refund_amount * 100),
      Math.round((delivered.line_total + delivered.tax_amount) * 100),
    );
    const updated = (
      await tx
        .request()
        .input("id", sql.NVarChar(40), delivered.order_id)
        .query("SELECT updated_at FROM app.orders WHERE order_id=@id;")
    ).recordset[0];
    await assert.rejects(
      executeAction(
        tx,
        delivered.order_id,
        command("return", updated.updated_at, {
          lineIds: [delivered.order_line_id],
        }),
      ),
      (e) => e.number === 51000,
    );
  });
  console.log(
    "PASS: discounted merchandise plus original tax; repeated return blocked",
  );
  await scoped(async (tx) => {
    await assert.rejects(
      executeAction(
        tx,
        delivered.order_id,
        command("return", delivered.updated_at, { lineIds: ["OUTSIDE-ORDER"] }),
      ),
      (e) => e.number === 51000,
    );
  });
  await scoped(async (tx) => {
    await tx
      .request()
      .input("id", sql.NVarChar(40), id)
      .query(
        "UPDATE app.payments SET amount=amount-1 WHERE order_id=@id AND payment_status='CAPTURED';",
      );
    await assert.rejects(
      executeAction(
        tx,
        id,
        command("ship", candidate.updated_at, {
          carrier: "TEST",
          trackingNumber: randomUUID(),
        }),
      ),
      (e) => e.number === 51000,
    );
  });
  console.log(
    "PASS: unrelated return line and mismatched captured payment rejected",
  );
  const after = (
    await pool
      .request()
      .input("id", sql.NVarChar(40), id)
      .query(
        "SELECT status,updated_at FROM app.orders WHERE order_id=@id; SELECT COUNT(*) n FROM app.shipments WHERE order_id=@id;",
      )
  ).recordsets;
  assert.equal(after[0][0].status, "PAID");
  assert.equal(
    after[0][0].updated_at.toISOString(),
    candidate.updated_at.toISOString(),
  );
  assert.equal(after[1][0].n, 0);
  const detail = await createDatabase(async () => pool).detail(id);
  assert.equal(detail.order.status, "PAID"); assert.equal(detail.shipments.length, 0);
  console.log("PASS: consistent detail read; baseline order unchanged after all tests");
} finally {
  await pool.close();
}
