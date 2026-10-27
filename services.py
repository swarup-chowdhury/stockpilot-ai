from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from db import rows
from analytics import category_mix, daily_sales, restock_recommendations, top_products, money
from algorithms import fefo_batches


def product_rows(conn, workspace_id):
    return rows(conn, """SELECT p.*, COALESCE(c.name,'Uncategorized') category, s.name supplier, s.lead_time_days, s.reliability
        FROM products p
        LEFT JOIN categories c ON c.id=p.category_id AND c.workspace_id=?
        LEFT JOIN suppliers s ON s.id=p.supplier_id AND s.workspace_id=?
        WHERE p.active=1 AND p.workspace_id=? ORDER BY p.name""", (workspace_id, workspace_id, workspace_id))


def sale_records(conn, workspace_id):
    sales = rows(conn, "SELECT * FROM sales WHERE workspace_id=? ORDER BY sale_date DESC", (workspace_id,))
    for sale in sales:
        sale["items"] = rows(conn, "SELECT * FROM sale_items WHERE sale_id=? AND workspace_id=?", (sale["id"], workspace_id))
    return sales


def supplier_records(conn, workspace_id):
    suppliers = rows(conn, "SELECT * FROM suppliers WHERE workspace_id=? ORDER BY name", (workspace_id,))
    for supplier in suppliers:
        supplier["product_ids"] = [r["id"] for r in conn.execute("SELECT id FROM products WHERE supplier_id=? AND workspace_id=?", (supplier["id"], workspace_id)).fetchall()]
    return suppliers


def dashboard(conn, workspace_id, demo_mode=False):
    products = product_rows(conn, workspace_id)
    sales = sale_records(conn, workspace_id)
    suppliers = supplier_records(conn, workspace_id)
    batches = rows(conn, "SELECT * FROM stock_batches WHERE workspace_id=?", (workspace_id,))
    today = date.today().isoformat()
    inventory_value = sum((Decimal(str(p["purchase_cost"])) * p["current_qty"] for p in products), Decimal("0"))
    selling_value = sum((Decimal(str(p["selling_price"])) * p["current_qty"] for p in products), Decimal("0"))
    today_sales = sum((Decimal(str(s["total"])) for s in sales if s["sale_date"][:10] == today and s["status"] == "completed"), Decimal("0"))
    profit = sum(((Decimal(str(i["unit_price"])) - Decimal(str(i["cost_price"]))) * i["quantity"] for s in sales for i in s["items"] if s["status"] == "completed"), Decimal("0"))
    low = [p for p in products if p["current_qty"] <= p["reorder_level"]]
    product_names = {p["id"]: p["name"] for p in products}
    expiring = [{**b, "name": product_names.get(b["product_id"], "Unknown product")} for b in batches if b.get("expiry_date") and b["expiry_date"] <= (date.today() + timedelta(days=30)).isoformat() and b["quantity"] > 0]
    purchase_pending = rows(conn, "SELECT po.*, s.name supplier FROM purchase_orders po JOIN suppliers s ON s.id=po.supplier_id AND s.workspace_id=? WHERE po.status IN ('pending','partial') AND po.workspace_id=? ORDER BY expected_date", (workspace_id, workspace_id))
    recommendations = restock_recommendations(products, sales, suppliers, batches)
    movements = rows(conn, "SELECT m.*, p.name product, p.sku FROM stock_movements m JOIN products p ON p.id=m.product_id AND p.workspace_id=? WHERE m.workspace_id=? ORDER BY m.id DESC LIMIT 8", (workspace_id, workspace_id))
    return {"metrics": {"active_products": len(products), "inventory_value": float(money(inventory_value)), "selling_value": float(money(selling_value)), "low_stock": len(low), "expiring": len(expiring), "today_sales": float(money(today_sales)), "gross_profit": float(money(profit)), "pending_pos": len(purchase_pending)}, "low_stock": low[:6], "expiring": expiring[:6], "pending_pos": purchase_pending[:5], "recommendations": recommendations[:6], "movements": movements, "sales_trend": daily_sales(sales, 14), "category_mix": category_mix(products), "top_products": top_products(products, sales), "demo_mode": bool(demo_mode), "is_empty": not products and not sales}


def _ensure_product_refs(conn, workspace_id, category_id, supplier_id):
    if not category_id:
        row = conn.execute("SELECT id FROM categories WHERE workspace_id=? ORDER BY id LIMIT 1", (workspace_id,)).fetchone()
        if row:
            category_id = row["id"]
        else:
            category_id = conn.execute("INSERT INTO categories(name,workspace_id) VALUES(?,?)", ("General", workspace_id)).lastrowid
    if not supplier_id:
        row = conn.execute("SELECT id FROM suppliers WHERE workspace_id=? ORDER BY id LIMIT 1", (workspace_id,)).fetchone()
        if row:
            supplier_id = row["id"]
        else:
            supplier_id = conn.execute("INSERT INTO suppliers(name,contact,email,workspace_id) VALUES(?,?,?,?)", ("Add supplier", "", "", workspace_id)).lastrowid
    return int(category_id), int(supplier_id)


def create_product(conn, payload, user_id, workspace_id):
    required = ["sku", "barcode", "name", "purchase_cost", "selling_price", "current_qty", "minimum_stock", "reorder_level"]
    if any(payload.get(k) in (None, "") for k in required):
        raise ValueError("Complete all required product fields")
    try:
        category_id, supplier_id = _ensure_product_refs(conn, workspace_id, payload.get("category_id"), payload.get("supplier_id"))
        values = (payload["sku"].strip(), payload["barcode"].strip(), payload["name"].strip(), payload.get("description", ""), category_id, supplier_id, float(payload["purchase_cost"]), float(payload["selling_price"]), int(payload["current_qty"]), int(payload["minimum_stock"]), int(payload["reorder_level"]), payload.get("unit", "unit"), 1 if payload.get("expiry_required") else 0, workspace_id)
    except (TypeError, ValueError):
        raise ValueError("Prices and quantities must be valid numbers")
    if any(value < 0 for value in values[6:11]):
        raise ValueError("Prices and quantities cannot be negative")
    try:
        cur = conn.execute("INSERT INTO products(sku,barcode,name,description,category_id,supplier_id,purchase_cost,selling_price,current_qty,minimum_stock,reorder_level,unit,expiry_required,workspace_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
        product_id = cur.lastrowid
        if values[8]:
            conn.execute("INSERT INTO stock_batches(product_id,batch_code,quantity,received_date,workspace_id) VALUES(?,?,?,?,?)", (product_id, f"OPEN-{product_id}", values[8], date.today().isoformat(), workspace_id))
            conn.execute("INSERT INTO stock_movements(product_id,movement_type,quantity,reason,reference,created_at,user_id,workspace_id) VALUES(?,?,?,?,?,?,?,?)", (product_id, "opening", values[8], "Opening stock", "PRODUCT_CREATE", date.today().isoformat(), user_id, workspace_id))
        conn.execute("INSERT INTO audit_logs(action,entity,entity_id,detail,created_at,user_id,workspace_id) VALUES(?,?,?,?,?,?,?)", ("create", "product", product_id, "Product created", date.today().isoformat(), user_id, workspace_id))
        conn.commit()
        return product_id
    except Exception:
        conn.rollback()
        raise


def process_sale(conn, payload, user_id, workspace_id):
    items = payload.get("items", [])
    if not items: raise ValueError("Add at least one product to the sale")
    try:
        subtotal = Decimal("0")
        enriched = []
        for item in items:
            product = conn.execute("SELECT * FROM products WHERE id=? AND workspace_id=? AND active=1", (int(item["product_id"]), workspace_id)).fetchone()
            quantity = int(item["quantity"])
            if not product or quantity <= 0: raise ValueError("Invalid sale line")
            if product["current_qty"] < quantity: raise ValueError(f"Insufficient stock for {product['name']}")
            line = Decimal(str(product["selling_price"])) * quantity
            subtotal += line
            enriched.append((product, quantity, line))
        discount = Decimal(str(payload.get("discount", 0) or 0))
        tax_rate = Decimal(str(payload.get("tax_rate", "5") or "0")) / 100
        tax = (subtotal - discount) * tax_rate
        total = (subtotal - discount + tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        invoice = f"INV-{date.today().strftime('%y%m%d')}-{conn.execute('SELECT COUNT(*) FROM sales WHERE workspace_id=?', (workspace_id,)).fetchone()[0] + 1:04d}"
        cur = conn.execute("INSERT INTO sales(invoice_no,sale_date,subtotal,discount,tax,total,payment_method,status,user_id,workspace_id) VALUES(?,?,?,?,?,?,?,?,?,?)", (invoice, date.today().isoformat(), str(subtotal), str(discount), str(tax), str(total), payload.get("payment_method", "card"), "completed", user_id, workspace_id))
        sale_id = cur.lastrowid
        for product, quantity, line in enriched:
            conn.execute("INSERT INTO sale_items(sale_id,product_id,quantity,unit_price,cost_price,workspace_id) VALUES(?,?,?,?,?,?)", (sale_id, product["id"], quantity, product["selling_price"], product["purchase_cost"], workspace_id))
            batches = [dict(r) for r in conn.execute("SELECT * FROM stock_batches WHERE product_id=? AND workspace_id=? AND quantity>0 ORDER BY COALESCE(expiry_date,'9999-12-31')", (product["id"], workspace_id))]
            selected, left = fefo_batches(batches, quantity)
            if left: raise ValueError(f"Insufficient batch stock for {product['name']}")
            for take in selected:
                conn.execute("UPDATE stock_batches SET quantity=quantity-? WHERE id=? AND workspace_id=?", (take["quantity"], take["batch_id"], workspace_id))
            conn.execute("UPDATE products SET current_qty=current_qty-? WHERE id=? AND workspace_id=?", (quantity, product["id"], workspace_id))
            conn.execute("INSERT INTO stock_movements(product_id,movement_type,quantity,reason,reference,created_at,user_id,workspace_id) VALUES(?,?,?,?,?,?,?,?)", (product["id"], "sale", -quantity, "Sale deduction (FEFO)", invoice, date.today().isoformat(), user_id, workspace_id))
        conn.execute("INSERT INTO audit_logs(action,entity,entity_id,detail,created_at,user_id,workspace_id) VALUES(?,?,?,?,?,?,?)", ("create", "sale", sale_id, invoice, date.today().isoformat(), user_id, workspace_id))
        conn.commit()
        return {"id": sale_id, "invoice_no": invoice, "total": float(total)}
    except Exception:
        conn.rollback(); raise


def receive_purchase(conn, po_id, user_id, workspace_id):
    po = conn.execute("SELECT * FROM purchase_orders WHERE id=? AND workspace_id=?", (po_id, workspace_id)).fetchone()
    if not po: raise ValueError("Purchase order not found")
    items = rows(conn, "SELECT * FROM purchase_order_items WHERE po_id=? AND workspace_id=?", (po_id, workspace_id))
    if not items: raise ValueError("Purchase order has no line items")
    try:
        total_received = 0
        for item in items:
            receive_qty = item["ordered_qty"] - item["received_qty"]
            if receive_qty <= 0: continue
            batch_code = f"{po['po_number']}-{item['product_id']}"
            conn.execute("INSERT OR IGNORE INTO stock_batches(product_id,batch_code,quantity,expiry_date,received_date,workspace_id) VALUES(?,?,?,?,?,?)", (item["product_id"], batch_code, 0, None, date.today().isoformat(), workspace_id))
            conn.execute("UPDATE stock_batches SET quantity=quantity+? WHERE batch_code=? AND workspace_id=?", (receive_qty, batch_code, workspace_id))
            conn.execute("UPDATE products SET current_qty=current_qty+? WHERE id=? AND workspace_id=?", (receive_qty, item["product_id"], workspace_id))
            conn.execute("UPDATE purchase_order_items SET received_qty=ordered_qty WHERE id=? AND workspace_id=?", (item["id"], workspace_id))
            conn.execute("INSERT INTO stock_movements(product_id,movement_type,quantity,reason,reference,created_at,user_id,workspace_id) VALUES(?,?,?,?,?,?,?,?)", (item["product_id"], "receipt", receive_qty, "Purchase receipt", po["po_number"], date.today().isoformat(), user_id, workspace_id))
            total_received += receive_qty
        conn.execute("UPDATE purchase_orders SET status='received' WHERE id=? AND workspace_id=?", (po_id, workspace_id))
        conn.commit(); return total_received
    except Exception:
        conn.rollback(); raise


def record_waste(conn, payload, user_id, workspace_id):
    product_id = int(payload.get("product_id") or 0)
    quantity = int(payload.get("quantity") or 0)
    reason = (payload.get("reason") or "Damaged goods").strip()
    product = conn.execute("SELECT * FROM products WHERE id=? AND workspace_id=? AND active=1", (product_id, workspace_id)).fetchone()
    if not product or quantity <= 0: raise ValueError("Choose a product and a positive quantity")
    if product["current_qty"] < quantity: raise ValueError("Waste quantity cannot exceed available stock")
    try:
        batches = [dict(r) for r in conn.execute("SELECT * FROM stock_batches WHERE product_id=? AND workspace_id=? AND quantity>0 ORDER BY COALESCE(expiry_date,'9999-12-31')", (product_id, workspace_id))]
        selected, left = fefo_batches(batches, quantity)
        if left: raise ValueError("Available batch quantity is insufficient")
        for take in selected: conn.execute("UPDATE stock_batches SET quantity=quantity-? WHERE id=? AND workspace_id=?", (take["quantity"], take["batch_id"], workspace_id))
        conn.execute("UPDATE products SET current_qty=current_qty-? WHERE id=? AND workspace_id=?", (quantity, product_id, workspace_id))
        conn.execute("INSERT INTO stock_movements(product_id,movement_type,quantity,reason,reference,created_at,user_id,workspace_id) VALUES(?,?,?,?,?,?,?,?)", (product_id, "waste", -quantity, reason, "WASTE", date.today().isoformat(), user_id, workspace_id))
        conn.execute("INSERT INTO audit_logs(action,entity,entity_id,detail,created_at,user_id,workspace_id) VALUES(?,?,?,?,?,?,?)", ("waste", "product", product_id, f"{quantity} units · {reason}", date.today().isoformat(), user_id, workspace_id))
        conn.commit(); return quantity
    except Exception:
        conn.rollback(); raise


def report(conn, report_type, workspace_id):
    products = product_rows(conn, workspace_id); sales = sale_records(conn, workspace_id)
    if report_type == "inventory": return [{"SKU": p["sku"], "Product": p["name"], "Category": p["category"], "Qty": p["current_qty"], "Unit Cost": p["purchase_cost"], "Value": float(money(p["current_qty"] * Decimal(str(p["purchase_cost"]))))} for p in products]
    if report_type == "low-stock": return [{"SKU": p["sku"], "Product": p["name"], "Stock": p["current_qty"], "Reorder Level": p["reorder_level"], "Supplier": p["supplier"]} for p in products if p["current_qty"] <= p["reorder_level"]]
    if report_type == "sales": return [{"Invoice": s["invoice_no"], "Date": s["sale_date"], "Subtotal": s["subtotal"], "Tax": s["tax"], "Total": s["total"], "Payment": s["payment_method"]} for s in sales[:100]]
    if report_type == "audit": return rows(conn, "SELECT m.created_at Date, p.sku SKU, p.name Product, m.movement_type Type, m.quantity Quantity, m.reason Reason, m.reference Reference FROM stock_movements m JOIN products p ON p.id=m.product_id AND p.workspace_id=? WHERE m.workspace_id=? ORDER BY m.id DESC LIMIT 200", (workspace_id, workspace_id))
    if report_type == "expiry": return rows(conn, "SELECT p.sku SKU,p.name Product,b.batch_code Batch,b.quantity Quantity,b.expiry_date Expiry FROM stock_batches b JOIN products p ON p.id=b.product_id AND p.workspace_id=? WHERE b.workspace_id=? AND b.expiry_date IS NOT NULL ORDER BY b.expiry_date", (workspace_id, workspace_id))
    return []


def assistant_answer(conn, question, workspace_id):
    q = question.lower().strip(); products = product_rows(conn, workspace_id); sales = sale_records(conn, workspace_id)
    if any(word in q for word in ("restock", "reorder", "replenish")):
        recs = restock_recommendations(products, sales, supplier_records(conn, workspace_id), rows(conn, "SELECT * FROM stock_batches WHERE workspace_id=?", (workspace_id,)))
        return {"title": "Restocking priorities", "answer": f"I found {len(recs)} products that need attention. The top signal is {recs[0]['product']} at {recs[0]['current_stock']} units." if recs else "No products are currently below the calculated target.", "items": recs[:5]}
    if "fast" in q or "selling" in q:
        return {"title": "Fast-moving products", "answer": "These are the strongest unit movers in recorded completed sales.", "items": top_products(products, sales)}
    if "valuation" in q or "inventory value" in q:
        value = sum((Decimal(str(p["purchase_cost"])) * p["current_qty"] for p in products), Decimal("0")); return {"title": "Current inventory valuation", "answer": f"Recorded inventory at purchase cost is ₹{money(value):,.2f} across {len(products)} active products.", "items": []}
    if "expire" in q:
        soon = rows(conn, "SELECT p.name,b.expiry_date,b.quantity FROM stock_batches b JOIN products p ON p.id=b.product_id AND p.workspace_id=? WHERE b.workspace_id=? AND b.expiry_date IS NOT NULL AND b.quantity>0 ORDER BY b.expiry_date LIMIT 6", (workspace_id, workspace_id)); return {"title": "Expiry watch", "answer": "These batches are the next expiry signals in the ledger.", "items": soon}
    if "supplier" in q or "delivery" in q:
        items = [{"supplier": s["name"], "reliability": f"{s['reliability']*100:.0f}%", "lead_time_days": s["lead_time_days"]} for s in sorted(supplier_records(conn, workspace_id), key=lambda x: x["reliability"], reverse=True)]; return {"title": "Supplier performance", "answer": "Supplier scores use recorded lead time and reliability fields in this workspace.", "items": items}
    return {"title": "Try a supported question", "answer": "I can answer about restocking, fastest sellers, expiring products, inventory valuation, or supplier delivery performance.", "items": []}
