import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Row = Record<string, string | number | null>;
type ListResult = {
  orders: Row[];
  total: number;
  page: number;
  pageSize: number;
};
type DetailResult = {
  order: Row;
  lines: Row[];
  payments: Row[];
  shipments: Row[];
  refunds: Row[];
  audit: Row[];
  refundLines: Row[];
};
const money = (n: unknown) =>
  new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(
    Number(n),
  );
const count = (n: unknown) => new Intl.NumberFormat("en-US").format(Number(n));
const date = (n: unknown, time = false) =>
  n
    ? new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        ...(time
          ? ({
              hour: "2-digit",
              minute: "2-digit",
              timeZoneName: "short",
            } as const)
          : {}),
        timeZone: "UTC",
      }).format(new Date(String(n)))
    : "—";
const label = (s: unknown) =>
  String(s ?? "")
    .toLowerCase()
    .replaceAll("_", " ")
    .replace(/^./, (c) => c.toUpperCase());
async function api<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal });
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      response.status === 401
        ? "Your session expired. Sign out and sign in again."
        : data.error || "Request failed.",
    );
  return data;
}
function Status({ value }: { value: unknown }) {
  return (
    <span className={`status status-${String(value).toLowerCase()}`}>
      {label(value)}
    </span>
  );
}
function ErrorNotice({ message }: { message: string }) {
  return (
    <div className="error" role="alert">
      {message}
    </div>
  );
}
function Login({ onLogin }: { onLogin: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error);
      setPassword("");
      onLogin();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sign in failed.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="login-page">
      <div className="login-story">
        <a className="brand" href="/">
          <span className="brand-mark">N</span> northline
          <span className="brand-dot">®</span>
        </a>
        <div>
          <p className="eyebrow">ORDER OPERATIONS</p>
          <h1>
            Every order.
            <br />
            The whole story.
          </h1>
          <p>
            One place to follow a purchase from the first item to the final
            delivery.
          </p>
        </div>
        <span className="login-foot">
          Office essentials. Connected operations.
        </span>
      </div>
      <main className="login-panel">
        <form onSubmit={submit}>
          <span className="eyebrow">WELCOME BACK</span>
          <h2>Open your workspace</h2>
          <p className="muted">Sign in to the development operations portal.</p>
          <label htmlFor="password">Access password</label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error ? <ErrorNotice message={error} /> : null}
          <button className="primary" disabled={busy}>
            {busy ? "Signing in…" : "Enter workspace →"}
          </button>
          <p className="fine">Development workspace · Synthetic transactions</p>
        </form>
      </main>
    </div>
  );
}
function OrderList() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [query, setQuery] = useState("page=1");
  const [page, setPage] = useState(1);
  const [result, setResult] = useState<ListResult | null>(null);
  const [summary, setSummary] = useState<Row | null>(null);
  const [summaryError, setSummaryError] = useState(false);
  const [refresh, setRefresh] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const controller = new AbortController();
    api<Row>("/api/summary", controller.signal)
      .then(setSummary)
      .catch((error) => {
        if (error.name !== "AbortError") setSummaryError(true);
      });
    return () => controller.abort();
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError("");
    api<ListResult>(`/api/orders?${query}`, controller.signal)
      .then(setResult)
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [query, refresh]);
  function apply(e?: React.FormEvent) {
    e?.preventDefault();
    setRefresh((value) => value + 1);
    setPage(1);
    setQuery(
      new URLSearchParams({ search, status, from, to, page: "1" }).toString(),
    );
  }
  function turnPage(next: number) {
    const params = new URLSearchParams(query);
    params.set("page", String(next));
    setPage(next);
    setQuery(params.toString());
  }
  function reset() {
    setRefresh((value) => value + 1);
    setSearch("");
    setStatus("");
    setFrom("");
    setTo("");
    setPage(1);
    setQuery("page=1");
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">WORKSPACE / ORDERS</p>
          <h1>Order overview</h1>
          <p className="muted">
            From checkout to delivery, stay close to every order.
          </p>
        </div>
        <span className="workspace-badge">
          <i /> Development data
        </span>
      </div>
      {summaryError ? (
        <ErrorNotice message="Overview counts are unavailable. Refresh the page to retry." />
      ) : null}
      <div className="stats">
        {[
          ["Total orders", summary?.orders, "Across your workspace"],
          ["In progress", summary?.active, "Awaiting payment or delivery"],
          ["Delivered", summary?.delivered, "Completed deliveries"],
          [
            "Orders with returns",
            summary?.returned,
            "Full and partial returns",
          ],
        ].map(([title, value, note]) => (
          <div className="stat" key={String(title)}>
            <p>{title}</p>
            <strong>{value !== undefined ? count(value) : "—"}</strong>
            <span>{note}</span>
          </div>
        ))}
      </div>
      <section className="orders-panel">
        <div className="section-heading">
          <div>
            <h2>All orders</h2>
            <p className="muted">Find a transaction and explore its history.</p>
          </div>
          <span className="count-tag">
            {result ? count(result.total) : "…"} results
          </span>
        </div>
        <form className="filters" onSubmit={apply}>
          <label className="search-field">
            Search orders
            <input
              placeholder="Order ID, customer name or ID"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              maxLength={100}
            />
          </label>
          <label>
            Status
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">All statuses</option>
              {[
                "PENDING_PAYMENT",
                "PAID",
                "SHIPPED",
                "DELIVERED",
                "CANCELLED",
                "PARTIALLY_RETURNED",
                "RETURNED",
              ].map((s) => (
                <option key={s} value={s}>
                  {label(s)}
                </option>
              ))}
            </select>
          </label>
          <label>
            From
            <input
              type="date"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
            />
          </label>
          <label>
            To
            <input
              type="date"
              value={to}
              onChange={(e) => setTo(e.target.value)}
            />
          </label>
          <button className="primary" disabled={loading}>
            Apply
          </button>
          <button type="button" className="text-button" onClick={reset}>
            Reset
          </button>
        </form>
        {error ? <ErrorNotice message={error} /> : null}
        <div className="table-wrap" aria-busy={loading}>
          <table>
            <thead>
              <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Date · UTC</th>
                <th>Status</th>
                <th className="numeric">Order total</th>
                <th>
                  <span className="sr-only">Open order</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {!error &&
                result?.orders.map((order) => (
                  <tr key={String(order.order_id)}>
                    <td>
                      <a
                        className="order-link"
                        href={`#/orders/${order.order_id}`}
                      >
                        {order.order_id}
                      </a>
                      <span className="subtext">{order.customer_id}</span>
                    </td>
                    <td>
                      {order.customer_name}
                      <span className="subtext">{order.customer_segment}</span>
                    </td>
                    <td>{date(order.order_date)}</td>
                    <td>
                      <Status value={order.status} />
                    </td>
                    <td className="numeric amount">
                      {money(order.total_amount)}
                    </td>
                    <td>
                      <a
                        className="arrow-link"
                        aria-label={`View ${order.order_id}`}
                        href={`#/orders/${order.order_id}`}
                      >
                        ↗
                      </a>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
          {loading ? (
            <div className="loading" role="status">
              Loading orders…
            </div>
          ) : !error && result?.total === 0 ? (
            <div className="empty">
              <h3>No matching orders</h3>
              <p>Try another customer, date range, or status.</p>
              <button className="text-button" onClick={reset}>
                Clear filters
              </button>
            </div>
          ) : null}
        </div>
        <div className="pagination">
          <span>
            {result?.total
              ? `${count((page - 1) * 25 + 1)}–${count(Math.min(page * 25, result.total))} of ${count(result.total)} orders`
              : "0 orders"}
          </span>
          <div>
            <button
              onClick={() => turnPage(page - 1)}
              disabled={loading || page === 1}
            >
              ← Previous
            </button>
            <span>Page {page}</span>
            <button
              onClick={() => turnPage(page + 1)}
              disabled={loading || !result || page * 25 >= result.total}
            >
              Next →
            </button>
          </div>
        </div>
      </section>
      <p className="table-note">
        All amounts in USD. Order totals include discounts and tax.
      </p>
    </>
  );
}
function OrderDetail({ id }: { id: string }) {
  const [data, setData] = useState<DetailResult | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    const c = new AbortController();
    setData(null);
    setError("");
    api<DetailResult>(`/api/orders/${encodeURIComponent(id)}`, c.signal)
      .then(setData)
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => c.abort();
  }, [id]);
  if (error)
    return (
      <>
        <a className="back" href="#/orders">
          ← All orders
        </a>
        <ErrorNotice message={error} />
      </>
    );
  if (!data)
    return (
      <div className="loading" role="status">
        Loading order history…
      </div>
    );
  const { order, lines, payments, shipments, refunds, audit, refundLines } =
    data;
  return (
    <>
      <a className="back" href="#/orders">
        ← All orders
      </a>
      <div className="page-heading">
        <div>
          <p className="eyebrow">ORDER DETAILS</p>
          <h1>{order.order_id}</h1>
          <p className="muted">Placed {date(order.order_date, true)}</p>
        </div>
        <Status value={order.status} />
      </div>
      <div className="detail-grid">
        <div>
          <section className="card">
            <div className="section-heading">
              <h2>Items ordered</h2>
              <span className="count-tag">{lines.length} items</span>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th className="numeric">Qty</th>
                    <th className="numeric">Unit price</th>
                    <th className="numeric">Discounts</th>
                    <th className="numeric">Net merchandise</th>
                  </tr>
                </thead>
                <tbody>
                  {lines.map((l) => (
                    <tr key={String(l.order_line_id)}>
                      <td>
                        <strong>{l.product_name}</strong>
                        <span className="subtext">
                          {l.product_id}
                          {l.promotion_code ? ` · ${l.promotion_code}` : ""}
                        </span>
                      </td>
                      <td className="numeric">{l.quantity}</td>
                      <td className="numeric">{money(l.unit_price)}</td>
                      <td className="numeric">
                        −
                        {money(
                          Number(l.discount_amount) +
                            Number(l.order_discount_amount),
                        )}
                      </td>
                      <td className="numeric amount">{money(l.line_total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="totals">
              <div>
                <span>Subtotal</span>
                <span>{money(order.subtotal)}</span>
              </div>
              <div>
                <span>
                  Discounts{order.coupon_code ? ` · ${order.coupon_code}` : ""}
                </span>
                <span>−{money(order.discount_amount)}</span>
              </div>
              <div>
                <span>Tax</span>
                <span>{money(order.tax_amount)}</span>
              </div>
              <div className="total">
                <strong>Order total</strong>
                <strong>{money(order.total_amount)}</strong>
              </div>
            </div>
          </section>
          <section className="card">
            <h2>Payments & refunds</h2>
            {payments.length === 0 ? (
              <p className="muted">No payment attempts.</p>
            ) : (
              payments.map((p) => (
                <div className="record" key={String(p.payment_id)}>
                  <div>
                    <strong>{label(p.payment_type)} payment</strong>
                    <span className="subtext">
                      {p.payment_id} · {date(p.payment_date, true)}
                    </span>
                  </div>
                  <div className="record-value">
                    <strong>{money(p.amount)}</strong>
                    <Status value={p.payment_status} />
                  </div>
                </div>
              ))
            )}
            {refunds.map((r) => (
              <div className="refund-record" key={String(r.refund_id)}>
                <div className="record">
                  <div>
                    <strong>Refund · {r.refund_reason}</strong>
                    <span className="subtext">
                      {r.refund_id} · {date(r.refund_date, true)}
                    </span>
                  </div>
                  <strong>−{money(r.refund_amount)}</strong>
                </div>
                {refundLines
                  .filter((l) => l.refund_id === r.refund_id)
                  .map((l) => (
                    <p className="subtext" key={String(l.order_line_id)}>
                      {l.order_line_id} · {l.quantity} returned · merchandise{" "}
                      {money(l.merchandise_amount)} + tax {money(l.tax_amount)}
                    </p>
                  ))}
              </div>
            ))}
            {refunds.length === 0 ? (
              <p className="muted small">No refunds recorded.</p>
            ) : null}
          </section>
          <section className="card">
            <h2>Order timeline</h2>
            <ol className="timeline">
              {audit.map((a) => (
                <li key={String(a.event_id)}>
                  <span className="timeline-dot" />
                  <div>
                    <strong>
                      {a.entity_type === "order"
                        ? label(a.new_value)
                        : a.entity_type === "payment"
                          ? `Payment ${label(a.new_value).toLowerCase()}`
                          : `Refund issued · ${money(a.new_value)}`}
                    </strong>
                    <span className="subtext">
                      {date(a.timestamp, true)} · {a.user_id}
                    </span>
                  </div>
                </li>
              ))}
            </ol>
          </section>
        </div>
        <aside>
          <section className="card customer-card">
            <div className="avatar">
              {String(order.customer_name).slice(0, 1)}
            </div>
            <h2>{order.customer_name}</h2>
            <p className="muted">{order.customer_segment}</p>
            <dl>
              <dt>Customer ID</dt>
              <dd>{order.customer_id}</dd>
              <dt>Location</dt>
              <dd>
                {order.state}, {order.country}
              </dd>
              <dt>Currency</dt>
              <dd>{order.currency}</dd>
            </dl>
          </section>
          <section className="card">
            <h2>Fulfillment</h2>
            {shipments.length ? (
              shipments.map((s) => (
                <div key={String(s.shipment_id)}>
                  <p>
                    <strong>{s.carrier}</strong>
                    <span className="subtext">{s.tracking_number}</span>
                  </p>
                  <dl>
                    <dt>Shipped</dt>
                    <dd>{date(s.shipped_at, true)}</dd>
                    <dt>Delivered</dt>
                    <dd>{date(s.delivered_at, true)}</dd>
                  </dl>
                </div>
              ))
            ) : (
              <p className="muted">This order has not shipped.</p>
            )}
          </section>
          <div className="detail-tip">
            <strong>A complete transaction history</strong>
            <p>
              Amounts, payment attempts and delivery events are linked to this
              order. Failed payment attempts are not captured funds.
            </p>
          </div>
        </aside>
      </div>
    </>
  );
}
function App() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [sessionError, setSessionError] = useState("");
  const [hash, setHash] = useState(location.hash);
  useEffect(() => {
    const c = new AbortController();
    api<{ authenticated: boolean }>("/api/session", c.signal)
      .then((d) => setAuthenticated(d.authenticated))
      .catch((e) => {
        if (e.name !== "AbortError")
          setSessionError("Unable to reach the portal. Refresh to try again.");
      });
    const handler = () => {
      setHash(location.hash);
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", handler);
    return () => {
      c.abort();
      window.removeEventListener("hashchange", handler);
    };
  }, []);
  async function logout() {
    try {
      await fetch("/api/logout", { method: "POST" });
      setAuthenticated(false);
    } catch {
      setSessionError("Unable to sign out. Please retry.");
    }
  }
  if (sessionError) return <ErrorNotice message={sessionError} />;
  if (authenticated === null)
    return <div className="loading">Opening workspace…</div>;
  if (!authenticated) return <Login onLogin={() => setAuthenticated(true)} />;
  const id = hash.startsWith("#/orders/") ? hash.slice(9) : "";
  return (
    <div className="workspace">
      <aside className="sidebar">
        <a className="brand" href="#/orders">
          <span className="brand-mark">N</span> northline
          <span className="brand-dot">®</span>
        </a>
        <p className="nav-label">OPERATIONS</p>
        <a className="nav-item active" href="#/orders">
          <span>▦</span> Orders <span className="nav-arrow">↗</span>
        </a>
        <div className="sidebar-bottom">
          <span className="operator-avatar">OP</span>
          <div>
            <strong>Operations</strong>
            <span>Development workspace</span>
          </div>
        </div>
      </aside>
      <div className="workspace-main">
        <header className="topbar">
          <span>Order Operations Portal</span>
          <div>
            <span className="demo-label">SYNTHETIC DATA</span>
            <button className="text-button" onClick={logout}>
              Sign out ↗
            </button>
          </div>
        </header>
        <main className="content">
          <div hidden={Boolean(id)}>
            <OrderList />
          </div>
          {id ? <OrderDetail id={id} /> : null}
        </main>
        <footer>
          Northline Operations <span>Development environment · USD · UTC</span>
        </footer>
      </div>
    </div>
  );
}
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
