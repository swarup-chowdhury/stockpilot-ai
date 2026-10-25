CREATE OR REPLACE PACKAGE inventory_pkg AS
  PROCEDURE record_stock_movement(p_product_id NUMBER,p_batch_id NUMBER,p_type VARCHAR2,p_quantity NUMBER,p_reason VARCHAR2,p_reference VARCHAR2,p_user_id NUMBER);
  PROCEDURE receive_stock(p_po_id NUMBER,p_user_id NUMBER,p_received_count OUT NUMBER);
  PROCEDURE process_sale(p_sale_id NUMBER,p_user_id NUMBER);
  FUNCTION inventory_valuation RETURN NUMBER;
  FUNCTION reorder_point(p_product_id NUMBER,p_lookback_days NUMBER DEFAULT 30) RETURN NUMBER;
  PROCEDURE low_stock_report(p_result OUT SYS_REFCURSOR);
END inventory_pkg;
/
CREATE OR REPLACE PACKAGE BODY inventory_pkg AS
  PROCEDURE record_stock_movement(p_product_id NUMBER,p_batch_id NUMBER,p_type VARCHAR2,p_quantity NUMBER,p_reason VARCHAR2,p_reference VARCHAR2,p_user_id NUMBER) IS
  BEGIN
    IF p_quantity = 0 THEN RAISE_APPLICATION_ERROR(-20001,'Movement quantity cannot be zero'); END IF;
    INSERT INTO stock_movements(product_id,batch_id,movement_type,quantity,reason,reference_no,user_id) VALUES(p_product_id,p_batch_id,p_type,p_quantity,p_reason,p_reference,p_user_id);
    UPDATE products SET current_qty=current_qty+p_quantity WHERE product_id=p_product_id;
    IF SQL%ROWCOUNT=0 THEN RAISE_APPLICATION_ERROR(-20002,'Product not found'); END IF;
  END;
  PROCEDURE receive_stock(p_po_id NUMBER,p_user_id NUMBER,p_received_count OUT NUMBER) IS
    CURSOR c_items IS SELECT po_item_id,product_id,ordered_qty,received_qty,unit_cost FROM purchase_order_items WHERE po_id=p_po_id FOR UPDATE;
    l_qty NUMBER; l_batch NUMBER;
  BEGIN
    p_received_count:=0;
    FOR item IN c_items LOOP
      l_qty:=item.ordered_qty-item.received_qty;
      IF l_qty>0 THEN
        INSERT INTO stock_batches(product_id,batch_code,quantity,received_date) VALUES(item.product_id,'PO-'||p_po_id||'-'||item.product_id,l_qty,SYSDATE) RETURNING batch_id INTO l_batch;
        record_stock_movement(item.product_id,l_batch,'RECEIPT',l_qty,'Purchase receipt','PO-'||p_po_id,p_user_id);
        UPDATE purchase_order_items SET received_qty=ordered_qty WHERE po_item_id=item.po_item_id;
        p_received_count:=p_received_count+l_qty;
      END IF;
    END LOOP;
    UPDATE purchase_orders SET status='RECEIVED' WHERE po_id=p_po_id;
  EXCEPTION WHEN OTHERS THEN RAISE;
  END;
  PROCEDURE process_sale(p_sale_id NUMBER,p_user_id NUMBER) IS
    CURSOR c_items IS SELECT si.product_id,si.quantity FROM sale_items si WHERE si.sale_id=p_sale_id;
    l_stock NUMBER;
  BEGIN
    FOR item IN c_items LOOP
      SELECT current_qty INTO l_stock FROM products WHERE product_id=item.product_id FOR UPDATE;
      IF l_stock<item.quantity THEN RAISE_APPLICATION_ERROR(-20003,'Insufficient stock'); END IF;
      record_stock_movement(item.product_id,NULL,'SALE',-item.quantity,'Sale deduction','SALE-'||p_sale_id,p_user_id);
    END LOOP;
    UPDATE sales SET status='COMPLETED' WHERE sale_id=p_sale_id;
  EXCEPTION WHEN OTHERS THEN RAISE;
  END;
  FUNCTION inventory_valuation RETURN NUMBER IS l_total NUMBER; BEGIN SELECT NVL(SUM(current_qty*purchase_cost),0) INTO l_total FROM products WHERE active='Y'; RETURN l_total; END;
  FUNCTION reorder_point(p_product_id NUMBER,p_lookback_days NUMBER DEFAULT 30) RETURN NUMBER IS l_avg NUMBER; l_lead NUMBER; BEGIN SELECT NVL(AVG(ABS(sm.quantity)),0) / GREATEST(p_lookback_days,1), NVL(s.lead_time_days,4) INTO l_avg,l_lead FROM products p LEFT JOIN suppliers s ON s.supplier_id=p.supplier_id LEFT JOIN stock_movements sm ON sm.product_id=p.product_id AND sm.movement_type='SALE' AND sm.created_at>=SYSTIMESTAMP-p_lookback_days WHERE p.product_id=p_product_id GROUP BY s.lead_time_days; RETURN ROUND(l_avg*l_lead)+2; END;
  PROCEDURE low_stock_report(p_result OUT SYS_REFCURSOR) IS BEGIN OPEN p_result FOR SELECT sku,product_name,current_qty,reorder_level FROM products WHERE active='Y' AND current_qty<=reorder_level ORDER BY current_qty; END;
END inventory_pkg;
/
