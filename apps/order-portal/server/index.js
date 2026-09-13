import { createApp } from "./app.js";
import { database, closePool } from "./db.js";
for (const key of [
  "SQL_SERVER",
  "SQL_DATABASE",
  "SQL_USER",
  "SQL_PASSWORD",
  "PORTAL_PASSWORD",
  "SESSION_SECRET",
]) {
  if (!process.env[key]) throw new Error(`Missing required setting: ${key}`);
}
const app = createApp({
  database,
  password: process.env.PORTAL_PASSWORD,
  secret: process.env.SESSION_SECRET,
  production: process.env.NODE_ENV === "production",
});
const server = app.listen(Number(process.env.PORT || 3000), "0.0.0.0", () =>
  console.log(
    JSON.stringify({
      event: "portal_started",
      port: Number(process.env.PORT || 3000),
    }),
  ),
);
async function shutdown() {
  server.close();
  await closePool();
  process.exit(0);
}
process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
