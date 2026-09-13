-- All writes and audit entries execute inside the caller's SQL transaction.
SET XACT_ABORT ON;
SET LOCK_TIMEOUT 5000;
DECLARE @status nvarchar(40), @updated datetime2(3), @total decimal(19,4),
 @now datetime2(3)=SYSUTCDATETIME(), @action nvarchar(20)=JSON_VALUE(@payload,'$.action'),
 @reason nvarchar(500)=JSON_VALUE(@payload,'$.reason'), @newStatus nvarchar(40),
 @related nvarchar(40), @before nvarchar(max), @after nvarchar(max);
-- Serialize portal actions on this order, including different request IDs.
SELECT @status=status,@updated=updated_at,@total=total_amount
 FROM app.orders WITH (UPDLOCK,HOLDLOCK) WHERE order_id=@id;
IF @status IS NULL THROW 51001,'Order not found.',1;
IF EXISTS(SELECT 1 FROM app.audit_log WHERE event_id=@requestId)
BEGIN
 IF NOT EXISTS(SELECT 1 FROM app.audit_log WHERE event_id=@requestId AND entity_type='order'
  AND entity_id=@id AND operation='ACTION' AND old_value COLLATE Latin1_General_100_BIN2=@payload COLLATE Latin1_General_100_BIN2)
  THROW 51000,'Request ID already used for another action.',1;
 SELECT @id order_id,CAST(1 AS bit) replayed;
 RETURN;
END;
IF @updated<>CONVERT(datetime2(3),JSON_VALUE(@payload,'$.expectedUpdatedAt'),127)
 THROW 51000,'Order changed. Refresh its details before submitting another action.',1;
IF @now<=@updated SET @now=DATEADD(millisecond,1,@updated);
DECLARE @payment nvarchar(40), @paidAt datetime2(3);
IF (SELECT COUNT(*) FROM app.payments WHERE order_id=@id AND payment_status='CAPTURED')<>1
 THROW 51000,'This action requires exactly one captured payment.',1;
SELECT @payment=payment_id,@paidAt=payment_date FROM app.payments
 WHERE order_id=@id AND payment_status='CAPTURED' AND amount=@total;
IF @payment IS NULL OR @paidAt>@now THROW 51000,'Captured payment does not reconcile with this order.',1;
IF NOT EXISTS(SELECT 1 FROM app.order_lines WHERE order_id=@id)
 OR (SELECT SUM(line_total+tax_amount) FROM app.order_lines WHERE order_id=@id)<>@total
 THROW 51000,'Order lines do not reconcile with the order total.',1;
IF @action='ship'
BEGIN
 IF @status<>'PAID' OR EXISTS(SELECT 1 FROM app.shipments WHERE order_id=@id)
  OR EXISTS(SELECT 1 FROM app.refunds WHERE order_id=@id)
  THROW 51000,'Only a paid order without shipments or refunds can ship.',1;
 SET @related=CONVERT(nvarchar(36),NEWID());
 INSERT app.shipments(shipment_id,order_id,carrier,tracking_number,shipped_at)
 VALUES(@related,@id,JSON_VALUE(@payload,'$.carrier'),JSON_VALUE(@payload,'$.trackingNumber'),@now);
 INSERT app.shipment_lines(shipment_id,order_line_id,quantity)
 SELECT @related,order_line_id,quantity FROM app.order_lines WHERE order_id=@id;
 SET @newStatus='SHIPPED';
 SET @after=(SELECT s.*,JSON_QUERY((SELECT order_line_id,quantity FROM app.shipment_lines WHERE shipment_id=@related FOR JSON PATH)) lines
 FROM app.shipments s WHERE shipment_id=@related FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
END
ELSE IF @action='deliver'
BEGIN
 IF @status<>'SHIPPED' OR (SELECT COUNT(*) FROM app.shipments WHERE order_id=@id)<>1
  OR EXISTS(SELECT 1 FROM app.shipments WHERE order_id=@id AND (delivered_at IS NOT NULL OR shipped_at>@now))
  THROW 51000,'Only an undelivered shipped order can be delivered.',1;
 SELECT @related=shipment_id FROM app.shipments WHERE order_id=@id;
 IF EXISTS(SELECT 1 FROM app.order_lines l LEFT JOIN app.shipment_lines sl ON sl.order_line_id=l.order_line_id AND sl.shipment_id=@related
  WHERE l.order_id=@id AND (sl.quantity IS NULL OR sl.quantity<>l.quantity))
  OR EXISTS(SELECT 1 FROM app.shipment_lines sl JOIN app.order_lines l ON l.order_line_id=sl.order_line_id WHERE sl.shipment_id=@related AND l.order_id<>@id)
  THROW 51000,'Shipment lines do not match this order.',1;
 SET @before=(SELECT * FROM app.shipments WHERE shipment_id=@related FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
 UPDATE app.shipments SET delivered_at=@now WHERE shipment_id=@related;
 SET @after=(SELECT * FROM app.shipments WHERE shipment_id=@related FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
 SET @newStatus='DELIVERED';
END
ELSE IF @action='return'
BEGIN
 IF @status NOT IN ('DELIVERED','PARTIALLY_RETURNED')
  OR NOT EXISTS(SELECT 1 FROM app.shipments WHERE order_id=@id)
  OR EXISTS(SELECT 1 FROM app.shipments WHERE order_id=@id AND (delivered_at IS NULL OR delivered_at>@now))
  THROW 51000,'Only delivered items can be returned.',1;
 DECLARE @lines TABLE(id nvarchar(40) PRIMARY KEY);
 INSERT @lines SELECT value FROM OPENJSON(@payload,'$.lineIds');
 IF NOT EXISTS(SELECT 1 FROM @lines) OR EXISTS(SELECT 1 FROM @lines x LEFT JOIN app.order_lines l ON l.order_line_id=x.id
  WHERE l.order_id IS NULL OR l.order_id<>@id)
  OR EXISTS(SELECT 1 FROM @lines x JOIN app.refund_lines r ON r.order_line_id=x.id)
  THROW 51000,'A selected line is outside this order or has already been returned.',1;
 IF EXISTS(SELECT 1 FROM @lines x JOIN app.order_lines l ON l.order_line_id=x.id
  WHERE l.quantity<>(SELECT COALESCE(SUM(sl.quantity),0) FROM app.shipment_lines sl JOIN app.shipments s ON s.shipment_id=sl.shipment_id
    WHERE sl.order_line_id=l.order_line_id AND s.order_id=@id AND s.delivered_at IS NOT NULL))
  THROW 51000,'Selected items are not fully delivered.',1;
 DECLARE @amount decimal(19,4)=(SELECT SUM(l.line_total+l.tax_amount) FROM app.order_lines l JOIN @lines x ON x.id=l.order_line_id);
 IF @amount<=0 OR @amount+COALESCE((SELECT SUM(refund_amount) FROM app.refunds WHERE order_id=@id),0)>@total
  THROW 51000,'Refund would exceed captured funds.',1;
 SET @related=CONVERT(nvarchar(36),NEWID());
 INSERT app.refunds(refund_id,order_id,refund_amount,refund_reason,refund_date,payment_id)
 VALUES(@related,@id,@amount,@reason,@now,@payment);
 INSERT app.refund_lines(refund_id,order_line_id,quantity,merchandise_amount,tax_amount)
 SELECT @related,l.order_line_id,l.quantity,l.line_total,l.tax_amount FROM app.order_lines l JOIN @lines x ON x.id=l.order_line_id;
 SET @newStatus=CASE WHEN EXISTS(SELECT 1 FROM app.order_lines l WHERE l.order_id=@id
  AND NOT EXISTS(SELECT 1 FROM app.refund_lines r WHERE r.order_line_id=l.order_line_id)) THEN 'PARTIALLY_RETURNED' ELSE 'RETURNED' END;
 SET @after=(SELECT r.*,JSON_QUERY((SELECT order_line_id,quantity,merchandise_amount,tax_amount FROM app.refund_lines WHERE refund_id=@related FOR JSON PATH)) lines
 FROM app.refunds r WHERE refund_id=@related FOR JSON PATH,WITHOUT_ARRAY_WRAPPER);
END
ELSE THROW 51000,'Unsupported action.',1;
UPDATE app.orders SET status=@newStatus,updated_at=@now WHERE order_id=@id;
INSERT app.audit_log(event_id,entity_type,entity_id,operation,field,old_value,new_value,user_id,[timestamp]) VALUES
 (CONVERT(nvarchar(36),NEWID()),'order',@id,'UPDATE','status',@status,@newStatus,'portal-operator',@now),
 (CONVERT(nvarchar(36),NEWID()),CASE WHEN @action='return' THEN 'refund' ELSE 'shipment' END,@related,
 CASE WHEN @action='deliver' THEN 'UPDATE' ELSE 'CREATE' END,'record',@before,@after,'portal-operator',@now),
 (@requestId,'order',@id,'ACTION',@action,@payload,
 (SELECT @status old_status,@newStatus new_status,@reason reason,@related related_id FOR JSON PATH,WITHOUT_ARRAY_WRAPPER),'portal-operator',@now);
SELECT @id order_id,CAST(0 AS bit) replayed;
