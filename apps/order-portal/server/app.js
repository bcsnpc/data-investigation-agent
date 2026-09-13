import { parseAction } from "./actions.js";
import express from "express";
import helmet from "helmet";
import { rateLimit } from "express-rate-limit";
import {
  createHmac,
  randomBytes,
  scryptSync,
  timingSafeEqual,
} from "node:crypto";
import { resolve } from "node:path";
import { parseFilters, validOrderId } from "./filters.js";

export function createApp({
  database,
  password,
  secret,
  production = false,
  staticDirectory = resolve("dist"),
}) {
  if (!password || !secret || secret.length < 32)
    throw new Error(
      "Portal password and a session secret of at least 32 characters are required.",
    );
  const app = express();
  app.disable("x-powered-by");
  if (production) app.set("trust proxy", 1);
  app.use(
    helmet({
      contentSecurityPolicy: {
        directives: { "upgrade-insecure-requests": production ? [] : null },
      },
    }),
  );
  app.use(express.json({ limit: "2kb" }));
  const salt = randomBytes(16);
  const expected = scryptSync(password, salt, 32);
  const sign = (value) =>
    createHmac("sha256", secret).update(value).digest("hex");
  const validSession = (req) => {
    const match = (req.headers.cookie || "").match(
      /(?:^|;\s*)order_session=([^;]+)/,
    );
    if (!match) return false;
    const [expires, signature] = match[1].split(".");
    if (!/^\d+$/.test(expires) || !/^[a-f0-9]{64}$/.test(signature || ""))
      return false;
    return (
      Number(expires) > Date.now() &&
      timingSafeEqual(Buffer.from(sign(expires)), Buffer.from(signature))
    );
  };
  app.use("/api", (req, res, next) => {
    res.set("Cache-Control", "no-store");
    next();
  });
  app.get("/healthz", (_req, res) => res.json({ status: "ok" }));
  app.get("/api/session", (req, res) =>
    res.json({ authenticated: validSession(req) }),
  );
  const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    limit: 10,
    standardHeaders: "draft-7",
    legacyHeaders: false,
    message: { error: "Too many login attempts. Try again in 15 minutes." },
  });
  app.post("/api/login", limiter, (req, res) => {
    const candidate = req.body?.password;
    if (
      typeof candidate !== "string" ||
      candidate.length > 256 ||
      !timingSafeEqual(expected, scryptSync(candidate, salt, 32))
    )
      return res.status(401).json({ error: "Incorrect access password." });
    const expires = String(Date.now() + 8 * 60 * 60 * 1000);
    res.cookie("order_session", `${expires}.${sign(expires)}`, {
      httpOnly: true,
      secure: production,
      sameSite: "strict",
      maxAge: 8 * 60 * 60 * 1000,
      path: "/",
    });
    res.json({ authenticated: true });
  });
  app.post("/api/logout", (_req, res) => {
    res.clearCookie("order_session", {
      httpOnly: true,
      secure: production,
      sameSite: "strict",
      path: "/",
    });
    res.json({ authenticated: false });
  });
  app.use("/api", (req, res, next) =>
    validSession(req)
      ? next()
      : res.status(401).json({ error: "Sign in to access orders." }),
  );
  app.get("/api/summary", async (_req, res, next) => {
    try {
      res.json(await database.summary());
    } catch (error) {
      next(error);
    }
  });
  app.get("/api/orders", async (req, res, next) => {
    let filters;
    try {
      filters = parseFilters(req.query);
    } catch (error) {
      return res.status(400).json({ error: error.message });
    }
    try {
      res.json(await database.orders(filters));
    } catch (error) {
      next(error);
    }
  });
  app.get("/api/orders/:id", async (req, res, next) => {
    if (!validOrderId(req.params.id))
      return res.status(400).json({ error: "Invalid order ID." });
    try {
      const result = await database.detail(req.params.id);
      res
        .status(result ? 200 : 404)
        .json(result || { error: "Order not found." });
    } catch (error) {
      next(error);
    }
  });
  app.post("/api/orders/:id/actions", async (req, res, next) => {
    // Non-simple custom header + JSON enforce same-origin browser requests (no CORS enabled).
    if (
      !req.is("application/json") ||
      req.get("X-Order-Action") !== "1" ||
      (req.get("Sec-Fetch-Site") && req.get("Sec-Fetch-Site") !== "same-origin")
    )
      return res
        .status(403)
        .json({ error: "Submit actions from this portal." });
    if (!validOrderId(req.params.id))
      return res.status(400).json({ error: "Invalid order ID." });
    let command;
    try {
      command = parseAction(req.body);
    } catch (error) {
      return res.status(400).json({ error: error.message });
    }
    try {
      res.json(await database.action(req.params.id, command));
    } catch (error) {
      if ([51000, 51001, 2601, 2627, 1205, 1222].includes(error.number))
        return res.status(error.number === 51001 ? 404 : 409).json({
          error: [51000, 51001].includes(error.number)
            ? error.message
            : "Conflicting update or tracking number. Refresh and retry.",
        });
      next(error);
    }
  });
  app.use("/api", (_req, res) =>
    res.status(404).json({ error: "Endpoint not found." }),
  );
  app.use(express.static(staticDirectory));
  app.get("/{*path}", (_req, res) =>
    res.sendFile(resolve(staticDirectory, "index.html")),
  );
  app.use((error, req, res, _next) => {
    const id = randomBytes(6).toString("hex");
    console.error(
      JSON.stringify({
        event: "request_failed",
        requestId: id,
        path: req.path,
        code: error.code || "ERROR",
      }),
    );
    res.status(error.type === "entity.parse.failed" ? 400 : 503).json({
      error: "Unable to complete this request. Please try again.",
      requestId: id,
    });
  });
  return app;
}
