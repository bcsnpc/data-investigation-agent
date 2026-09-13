// Local browser verification against a transaction that is ALWAYS rolled back.
// Not included in deployment ZIP. Exit with Ctrl+C after verification.
import sql from "mssql";
import { fileURLToPath } from "node:url";
import { createApp } from "./app.js";
import { createDatabase } from "./db.js";
import { executeAction } from "./actions.js";
const pool = await new sql.ConnectionPool({
  server: process.env.SQL_SERVER,
  database: process.env.SQL_DATABASE,
  user: process.env.SQL_USER,
  password: process.env.SQL_PASSWORD,
  options: { encrypt: true, trustServerCertificate: false },
  connectionTimeout: 60000,
}).connect();
const tx = new sql.Transaction(pool);
await tx.begin();
const candidate = (
  await tx
    .request()
    .query(
      "SELECT TOP(1) order_id FROM app.orders WHERE status='PAID' ORDER BY order_id;",
    )
).recordset[0];
const source = {
  ...createDatabase(async () => tx),
  action: (id, c) => executeAction(tx, id, c),
};
let queue = Promise.resolve();
const database = Object.fromEntries(
  Object.entries(source).map(([name, fn]) => [
    name,
    (...args) => {
      const result = queue.then(() => fn(...args));
      queue = result.catch(() => {});
      return result;
    },
  ]),
);
const app = createApp({
  database,
  password: "rollback-browser-test",
  secret: "local-rollback-verification-secret-32-characters",
  staticDirectory: fileURLToPath(new URL("../dist", import.meta.url)),
});
const server = app.listen(3001, "127.0.0.1", () =>
  console.log(
    `Rollback browser: http://127.0.0.1:3001/#/orders/${candidate.order_id}`,
  ),
);
let ending = false;
async function stop() {
  if (ending) return;
  ending = true;
  server.close();
  try {
    await tx.rollback();
  } finally {
    await pool.close();
    process.exit(0);
  }
}
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
// Bound the lifetime even if the browser session is abandoned.
setTimeout(stop, 15 * 60 * 1000).unref();
