import { useRef, useState } from "react";
type Row = Record<string, string | number | null>;
export function OrderActions({
  order,
  lines,
  refundLines,
  onSaved,
}: {
  order: Row;
  lines: Row[];
  refundLines: Row[];
  onSaved: () => Promise<void>;
}) {
  const action =
    order.status === "PAID"
      ? "ship"
      : order.status === "SHIPPED"
        ? "deliver"
        : ["DELIVERED", "PARTIALLY_RETURNED"].includes(String(order.status))
          ? "return"
          : null;
  const [reason, setReason] = useState("");
  const [carrier, setCarrier] = useState("");
  const [trackingNumber, setTracking] = useState("");
  const [lineIds, setLines] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const pending = useRef<{ signature: string; requestId: string } | null>(null);
  const submitting = useRef(false);
  if (!action) return null;
  const available = lines.filter(
    (l) => !refundLines.some((r) => r.order_line_id === l.order_line_id),
  );
  const title = {
    ship: "Ship order",
    deliver: "Record delivery",
    return: "Return items",
  }[action];
  const amount = available
    .filter((l) => lineIds.includes(String(l.order_line_id)))
    .reduce((sum, l) => sum + Number(l.line_total) + Number(l.tax_amount), 0);
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (submitting.current || saved) return;
    submitting.current = true;
    setBusy(true);
    setError("");
    const body = {
      action,
      expectedUpdatedAt: order.updated_at,
      reason,
      ...(action === "ship" ? { carrier, trackingNumber } : {}),
      ...(action === "return" ? { lineIds: [...lineIds].sort() } : {}),
    };
    const signature = JSON.stringify(body);
    if (pending.current?.signature !== signature)
      pending.current = { signature, requestId: crypto.randomUUID() };
    try {
      const response = await fetch(`/api/orders/${order.order_id}/actions`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Order-Action": "1" },
        body: JSON.stringify({ ...body, requestId: pending.current.requestId }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Action failed.");
      setSaved(true);
      await onSaved();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Request failed. Retry with the same values to safely check the result.",
      );
    } finally {
      submitting.current = false;
      setBusy(false);
    }
  }
  return (
    <section className="card order-actions" aria-label="Order actions">
      <h2>{title}</h2>
      <p className="muted">
        Changes are recorded as the shared portal operator. Times are recorded
        in UTC.
      </p>
      <form onSubmit={submit}>
        <fieldset disabled={busy || saved}>
          <legend className="sr-only">{title}</legend>
          {action === "ship" ? (
            <div className="action-fields">
              <label>
                Carrier
                <input
                  required
                  maxLength={40}
                  value={carrier}
                  onChange={(e) => setCarrier(e.target.value)}
                />
              </label>
              <label>
                Tracking number
                <input
                  required
                  pattern="[A-Za-z0-9-]{3,60}"
                  maxLength={60}
                  value={trackingNumber}
                  onChange={(e) => setTracking(e.target.value)}
                />
              </label>
            </div>
          ) : null}
          {action === "return" ? (
            <>
              <p>
                Select items to return. All units of each selected line will be
                refunded, including the original tax.
              </p>
              {available.map((l) => (
                <label className="return-option" key={String(l.order_line_id)}>
                  <input
                    type="checkbox"
                    checked={lineIds.includes(String(l.order_line_id))}
                    onChange={(e) =>
                      setLines((ids) =>
                        e.target.checked
                          ? [...ids, String(l.order_line_id)]
                          : ids.filter((id) => id !== l.order_line_id),
                      )
                    }
                  />
                  <span>
                    {l.product_name} · {l.quantity} units
                  </span>
                </label>
              ))}
              <p>
                <strong>
                  Refund:{" "}
                  {new Intl.NumberFormat("en-US", {
                    style: "currency",
                    currency: "USD",
                  }).format(amount)}
                </strong>
              </p>
              <p className="fine">
                Records a synthetic refund in this workspace; no payment
                provider is contacted.
              </p>
            </>
          ) : null}
          {action === "deliver" ? (
            <p>Confirm that all items in the shipment have been delivered.</p>
          ) : null}
          <label>
            Reason
            <textarea
              required
              minLength={3}
              maxLength={500}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </label>
          <button
            className="primary"
            disabled={busy || saved || (action === "return" && !lineIds.length)}
          >
            {busy ? "Saving…" : title}
          </button>
        </fieldset>
      </form>
      {error ? (
        <div className="error" role="alert">
          {error}
        </div>
      ) : null}
      {saved ? <p role="status">Action saved.</p> : null}
      <button
        className="text-button"
        disabled={busy}
        onClick={() => {
          onSaved().catch(() =>
            setError("Unable to refresh. Please reload the page."),
          );
        }}
      >
        Refresh order details
      </button>
    </section>
  );
}
