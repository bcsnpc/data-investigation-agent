import { test } from "node:test";
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import request from "supertest";
import { parseAction } from "./actions.js";
import { createApp } from "./app.js";
const command = () => ({
  action: "deliver",
  requestId: randomUUID(),
  expectedUpdatedAt: "2026-09-12T00:00:00.000Z",
  reason: "Delivery confirmed",
});
test("action input rejects malformed versions, empty reasons and forged return lines", () => {
  for (const change of [
    { expectedUpdatedAt: "2026-02-30T00:00:00.000Z" },
    { requestId: "bad" },
    { reason: "  " },
    { action: "cancel" },
    { action: "return", lineIds: [] },
    { action: "return", lineIds: ["a", "a"] },
    { action: "return", lineIds: ["'; DROP TABLE app.orders"] },
    { action: "ship", carrier: "UPS", trackingNumber: "bad value" },
  ])
    assert.throws(() => parseAction({ ...command(), ...change }));
  assert.deepEqual(
    parseAction({ ...command(), action: "return", lineIds: ["b", "a"] })
      .lineIds,
    ["a", "b"],
  );
});
test("write route authenticates, rejects cross-site requests, validates and maps conflicts", async () => {
  let calls = 0;
  const app = createApp({
    password: "test",
    secret: "a".repeat(32),
    database: {
      action: async () => {
        calls++;
        throw Object.assign(new Error("Order changed."), { number: 51000 });
      },
    },
  });
  const path = "/api/orders/ORD-000001/actions";
  assert.equal((await request(app).post(path).send(command())).status, 401);
  const agent = request.agent(app);
  await agent.post("/api/login").send({ password: "test" });
  assert.equal((await agent.post(path).send(command())).status, 403);
  assert.equal(
    (
      await agent
        .post(path)
        .set("X-Order-Action", "1")
        .set("Sec-Fetch-Site", "cross-site")
        .send(command())
    ).status,
    403,
  );
  assert.equal(
    (await agent.post(path).set("X-Order-Action", "1").send({})).status,
    400,
  );
  const result = await agent
    .post(path)
    .set("X-Order-Action", "1")
    .send(command());
  assert.equal(result.status, 409);
  assert.equal(result.body.error, "Order changed.");
  assert.equal(calls, 1);
});
