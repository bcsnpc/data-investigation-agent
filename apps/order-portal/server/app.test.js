import { test } from "node:test";
import assert from "node:assert/strict";
import request from "supertest";
import { createApp } from "./app.js";
import { parseFilters } from "./filters.js";
const secret = "test-session-secret-with-at-least-32-characters";
const database = {
  summary: async () => ({ orders: 100000 }),
  orders: async (f) => ({ orders: [], total: 0, page: f.page }),
  detail: async () => null,
};
test("anonymous clients cannot retrieve order data", async () => {
  const app = createApp({ database, password: "test-password", secret });
  assert.equal((await request(app).get("/api/orders")).status, 401);
  assert.equal(
    (await request(app).post("/api/login").send({ password: "wrong" })).status,
    401,
  );
});
test("login, bounded filters, unknown order and logout", async () => {
  const agent = request.agent(
    createApp({ database, password: "test-password", secret }),
  );
  assert.equal(
    (await agent.post("/api/login").send({ password: "test-password" })).status,
    200,
  );
  assert.equal((await agent.get("/api/orders?page=-1")).status, 400);
  assert.equal((await agent.get("/api/orders?status=unknown")).status, 400);
  assert.equal((await agent.get("/api/orders?from=2026-02-30")).status, 400);
  assert.equal((await agent.get("/api/orders/ORD-999999")).status, 404);
  assert.equal((await agent.get("/api/orders")).status, 200);
  await agent.post("/api/logout");
  assert.equal((await agent.get("/api/summary")).status, 401);
});
test("forged cookies are rejected and production cookies are secure", async () => {
  const app = createApp({
    database,
    password: "test-password",
    secret,
    production: true,
  });
  assert.equal(
    (
      await request(app)
        .get("/api/orders")
        .set("Cookie", `order_session=9999999999999.${"a".repeat(64)}`)
    ).status,
    401,
  );
  const response = await request(app)
    .post("/api/login")
    .send({ password: "test-password" });
  assert.match(response.headers["set-cookie"][0], /HttpOnly/);
  assert.match(response.headers["set-cookie"][0], /Secure/);
  assert.match(response.headers["set-cookie"][0], /SameSite=Strict/);
});
test("filter values remain data and pagination stays bounded", () => {
  assert.equal(parseFilters({ search: "' OR 1=1 --" }).search, "' OR 1=1 --");
  assert.throws(() => parseFilters({ page: "1.5" }));
  assert.throws(() => parseFilters({ search: ["a", "b"] }));
  assert.throws(() => parseFilters({ from: "2026-03-01", to: "2026-02-01" }));
});
