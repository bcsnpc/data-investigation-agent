export const statuses = [
  "PENDING_PAYMENT",
  "PAID",
  "SHIPPED",
  "DELIVERED",
  "CANCELLED",
  "PARTIALLY_RETURNED",
  "RETURNED",
];
export function parseFilters(query) {
  const page = query.page === undefined ? 1 : Number(query.page);
  if (!Number.isInteger(page) || page < 1 || page > 10000)
    throw new Error("Page must be between 1 and 10000.");
  const search = query.search ?? "";
  const status = query.status ?? "";
  if (typeof search !== "string" || search.length > 100)
    throw new Error("Search must be at most 100 characters.");
  if (typeof status !== "string" || (status && !statuses.includes(status)))
    throw new Error("Select a valid order status.");
  const dates = {};
  for (const key of ["from", "to"]) {
    const value = query[key] ?? "";
    if (
      typeof value !== "string" ||
      (value &&
        (!/^\d{4}-\d{2}-\d{2}$/.test(value) ||
          Number.isNaN(Date.parse(value)) ||
          new Date(value).toISOString().slice(0, 10) !== value ||
          value < "2000-01-01" ||
          value > "2099-12-31"))
    )
      throw new Error("Enter a valid date between 2000 and 2099.");
    dates[key] = value;
  }
  if (dates.from && dates.to && dates.from > dates.to)
    throw new Error("Start date must be before end date.");
  return { page, search: search.trim(), status, ...dates, pageSize: 25 };
}
export function validOrderId(id) {
  return /^ORD-\d{6}$/.test(id);
}
