import sql from "mssql";
import { readFileSync } from "node:fs";
const statement = readFileSync(
  new URL("./order-action.sql", import.meta.url),
  "utf8",
);

export function parseAction(body) {
  const fail = () => {
    throw new Error(
      "Provide a valid action, request ID, order version and reason (3–500 characters).",
    );
  };
  if (!body || typeof body !== "object" || Array.isArray(body)) fail();
  const { action, requestId, expectedUpdatedAt } = body;
  if (
    !["ship", "deliver", "return"].includes(action) ||
    typeof requestId !== "string" ||
    !/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(
      requestId,
    ) ||
    typeof expectedUpdatedAt !== "string" ||
    !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(expectedUpdatedAt) ||
    !Number.isFinite(Date.parse(expectedUpdatedAt)) ||
    new Date(expectedUpdatedAt).toISOString() !== expectedUpdatedAt ||
    typeof body.reason !== "string" ||
    body.reason.trim().length < 3 ||
    body.reason.trim().length > 500
  )
    fail();
  const result = {
    action,
    requestId: requestId.toLowerCase(),
    expectedUpdatedAt,
    reason: body.reason.trim(),
  };
  if (action === "ship") {
    if (
      typeof body.carrier !== "string" ||
      !body.carrier.trim() ||
      body.carrier.trim().length > 40 ||
      typeof body.trackingNumber !== "string" ||
      !/^[A-Za-z0-9-]{3,60}$/.test(body.trackingNumber)
    )
      throw new Error(
        "Enter a carrier and a tracking number (3–60 letters, numbers or hyphens).",
      );
    result.carrier = body.carrier.trim();
    result.trackingNumber = body.trackingNumber;
  }
  if (action === "return") {
    if (
      !Array.isArray(body.lineIds) ||
      !body.lineIds.length ||
      body.lineIds.length > 100 ||
      body.lineIds.some(
        (x) => typeof x !== "string" || !/^[A-Za-z0-9-]{1,40}$/.test(x),
      ) ||
      new Set(body.lineIds).size !== body.lineIds.length
    )
      throw new Error("Select distinct order lines to return.");
    result.lineIds = [...body.lineIds].sort();
  }
  return result;
}

// Caller owns the transaction. Also used by rollback-only integration verification.
export async function executeAction(transaction, id, command) {
  return (
    await new sql.Request(transaction)
      .input("id", sql.NVarChar(40), id)
      .input("requestId", sql.NVarChar(40), command.requestId)
      .input("payload", sql.NVarChar(sql.MAX), JSON.stringify(command))
      .query(statement)
  ).recordset[0];
}

export async function applyAction(pool, id, command) {
  const transaction = new sql.Transaction(pool);
  let rolledBack = false;
  transaction.on("rollback", () => {
    rolledBack = true;
  });
  await transaction.begin();
  try {
    const result = await executeAction(transaction, id, command);
    await transaction.commit();
    return result;
  } catch (error) {
    if (!rolledBack) await transaction.rollback();
    throw error;
  }
}
