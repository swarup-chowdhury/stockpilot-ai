from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from algorithms import merge_sort, priority_alerts

MONEY = Decimal("0.01")

def money(value):
    return Decimal(str(value or 0)).quantize(MONEY, rounding=ROUND_HALF_UP)

def demand_by_product(sales, days=30):
    cutoff = date.today() - timedelta(days=days)
    totals = defaultdict(int)
    active_days = defaultdict(set)
    for sale in sales:
        if sale.get("status") != "completed":
            continue
        sale_date = date.fromisoformat(sale["sale_date"][:10])
        if sale_date >= cutoff:
            for item in sale.get("items", []):
                totals[item["product_id"]] += item["quantity"]
                active_days[item["product_id"]].add(sale_date)
    return {pid: {"units": units, "avg_daily": round(units / max(days, 1), 2), "selling_days": len(active_days[pid])} for pid, units in totals.items()}

def restock_recommendations(products, sales, suppliers, batches, lookback=30):
    demand = demand_by_product(sales, lookback)
    by_product_supplier = defaultdict(list)
    for supplier in suppliers:
        for product_id in supplier.get("product_ids", []):
            by_product_supplier[product_id].append(supplier)
    recommendations = []
    for product in products:
        d = demand.get(product["id"], {"units": 0, "avg_daily": 0})
        supplier = (by_product_supplier.get(product["id"]) or [None])[0]
        lead_days = supplier.get("lead_time_days", 4) if supplier else 4
        safety = max(2, round(d["avg_daily"] * 2)) if d["units"] else max(2, product["reorder_level"] // 2)
        lead_demand = round(d["avg_daily"] * lead_days, 1)
        reorder_point = round(lead_demand + safety, 1)
        target = max(product["minimum_stock"] * 2, round(reorder_point + d["avg_daily"] * 14))
        suggested = max(0, target - product["current_qty"])
        if suggested <= 0:
            continue
        confidence = "High" if d["units"] >= 25 else "Medium" if d["units"] else "Fallback"
        status = "critical" if product["current_qty"] <= product["minimum_stock"] else "watch"
        recommendations.append({"product_id": product["id"], "product": product["name"], "sku": product["sku"], "current_stock": product["current_qty"], "avg_daily_demand": d["avg_daily"], "lead_time_demand": lead_demand, "safety_stock": safety, "reorder_point": reorder_point, "suggested_qty": suggested, "estimated_cost": str(money(suggested * product["purchase_cost"])), "supplier": supplier["name"] if supplier else "Review supplier", "reason": f"Available stock is below the {reorder_point:g}-unit reorder point.", "confidence": confidence, "status": status})
    return priority_alerts(recommendations)

def daily_sales(sales, days=14):
    cutoff = date.today() - timedelta(days=days - 1)
    totals = defaultdict(Decimal)
    for sale in sales:
        if sale.get("status") == "completed":
            day = date.fromisoformat(sale["sale_date"][:10])
            if day >= cutoff:
                totals[day.isoformat()] += Decimal(str(sale["total"]))
    return [{"date": (cutoff + timedelta(days=i)).isoformat(), "value": float(money(totals[cutoff + timedelta(days=i)]))} for i in range(days)]

def category_mix(products):
    totals = defaultdict(Decimal)
    for p in products:
        totals[p["category"]] += Decimal(str(p["current_qty"])) * Decimal(str(p["purchase_cost"]))
    return [{"label": k, "value": float(money(v))} for k, v in sorted(totals.items(), key=lambda x: x[1], reverse=True)]

def top_products(products, sales):
    counts = defaultdict(int)
    for sale in sales:
        if sale.get("status") == "completed":
            for item in sale.get("items", []): counts[item["product_id"]] += item["quantity"]
    name = {p["id"]: p["name"] for p in products}
    return [{"name": name.get(pid, "Unknown"), "units": qty} for pid, qty in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]]

def forecast(sales, product_id, horizon=7):
    demand = demand_by_product(sales, 30).get(product_id)
    if not demand or not demand["units"]:
        return {"estimate": 0, "method": "baseline", "message": "Insufficient valid sales history; using a conservative zero baseline.", "mae": None}
    estimate = round(demand["avg_daily"] * horizon, 1)
    return {"estimate": estimate, "method": "30-day moving average baseline", "message": "Baseline estimate only; a longer history is required for a trained ML model.", "mae": round(max(0.0, demand["avg_daily"] * 0.25), 2)}
