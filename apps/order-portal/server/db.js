import { applyAction } from "./actions.js";
import sql from "mssql";
let poolPromise;
async function pool() {
  if (!poolPromise) {
    poolPromise = new sql.ConnectionPool({
      server: process.env.SQL_SERVER,
      database: process.env.SQL_DATABASE,
      user: process.env.SQL_USER,
      password: process.env.SQL_PASSWORD,
      options: { encrypt: true, trustServerCertificate: false, useUTC: true },
      connectionTimeout: 60000,
      requestTimeout: 30000,
      pool: { min: 0, max: 5, idleTimeoutMillis: 30000 },
    })
      .connect()
      .catch((error) => {
        poolPromise = undefined;
        throw error;
      });
  }
  return poolPromise;
}
export async function closePool() {
  if (poolPromise) await (await poolPromise).close();
  poolPromise = undefined;
}
async function consistentRead(connection, read) {
  if (connection instanceof sql.Transaction) return read(connection);
  const transaction = new sql.Transaction(connection);
  await transaction.begin();
  try {
    const result = await read(transaction);
    await transaction.commit();
    return result;
  } catch (error) {
    await transaction.rollback();
    throw error;
  }
}
export function createDatabase(getConnection = pool) {
  return {
    async action(id, command) {
      return applyAction(await getConnection(), id, command);
    },
    async summary() {
      const p = await getConnection();
      const result = await p.request().query(`SELECT COUNT(*) orders,
      SUM(CASE WHEN status IN ('PAID','SHIPPED','PENDING_PAYMENT') THEN 1 ELSE 0 END) active,
      SUM(CASE WHEN status IN ('PARTIALLY_RETURNED','RETURNED') THEN 1 ELSE 0 END) returned,
      SUM(CASE WHEN status='DELIVERED' THEN 1 ELSE 0 END) delivered
      FROM app.orders;`);
      return result.recordset[0];
    },
    async orders(filters) {
      const p = await getConnection();
      const r = p.request();
      r.input("search", sql.NVarChar(100), filters.search);
      r.input("status", sql.NVarChar(40), filters.status);
      r.input("from", sql.Date, filters.from || null);
      r.input("to", sql.Date, filters.to || null);
      r.input("offset", sql.Int, (filters.page - 1) * filters.pageSize);
      r.input("size", sql.Int, filters.pageSize);
      // CHARINDEX treats %, _, and quotes as literal characters, never SQL syntax.
      const where = `WHERE (@search='' OR CHARINDEX(@search,o.order_id)>0 OR CHARINDEX(@search,c.customer_name)>0 OR CHARINDEX(@search,c.customer_id)>0)
      AND (@status='' OR o.status=@status) AND (@from IS NULL OR o.order_date>=@from)
      AND (@to IS NULL OR o.order_date<DATEADD(day,1,@to))`;
      const result =
        await r.query(`SELECT COUNT(*) total FROM app.orders o JOIN app.customers c ON c.customer_id=o.customer_id ${where};
      SELECT o.order_id,o.order_date,o.status,o.total_amount,c.customer_name,c.customer_id,c.customer_segment
      FROM app.orders o JOIN app.customers c ON c.customer_id=o.customer_id ${where}
      ORDER BY o.order_date DESC,o.order_id DESC OFFSET @offset ROWS FETCH NEXT @size ROWS ONLY;`);
      return {
        orders: result.recordsets[1],
        total: result.recordsets[0][0].total,
        page: filters.page,
        pageSize: filters.pageSize,
      };
    },
    async detail(id) {
      const p = await getConnection();
      return consistentRead(p, async (connection) => {
        const result = await connection
          .request()
          .input("id", sql.NVarChar(40), id).query(`
      SELECT o.*,c.customer_name,c.customer_segment,c.state,c.country FROM app.orders o WITH (HOLDLOCK) JOIN app.customers c ON c.customer_id=o.customer_id WHERE o.order_id=@id;
      SELECT l.*,p.product_name FROM app.order_lines l JOIN app.products p ON p.product_id=l.product_id WHERE l.order_id=@id ORDER BY l.order_line_id;
      SELECT * FROM app.payments WHERE order_id=@id ORDER BY payment_date;
      SELECT * FROM app.shipments WHERE order_id=@id ORDER BY shipped_at;
      SELECT * FROM app.refunds WHERE order_id=@id ORDER BY refund_date;
      SELECT a.* FROM app.audit_log a WHERE (a.entity_type='order' AND a.entity_id=@id)
       OR (a.entity_type='payment' AND a.entity_id IN (SELECT payment_id FROM app.payments WHERE order_id=@id))
       OR (a.entity_type='shipment' AND a.entity_id IN (SELECT shipment_id FROM app.shipments WHERE order_id=@id))
       OR (a.entity_type='refund' AND a.entity_id IN (SELECT refund_id FROM app.refunds WHERE order_id=@id)) ORDER BY a.[timestamp],a.event_id;
      SELECT rl.* FROM app.refund_lines rl JOIN app.refunds r ON r.refund_id=rl.refund_id WHERE r.order_id=@id;
    `);
        if (!result.recordsets[0].length) return null;
        const [
          orders,
          lines,
          payments,
          shipments,
          refunds,
          audit,
          refundLines,
        ] = result.recordsets;
        return {
          order: orders[0],
          lines,
          payments,
          shipments,
          refunds,
          audit,
          refundLines,
        };
      });
    },
  };
}
export const database = createDatabase();
