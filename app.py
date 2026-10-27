import csv
import io
import os
import secrets
from functools import wraps
from flask import Flask, g, jsonify, render_template, request, session, make_response, send_from_directory
from config import Config
from db import init_db, rows, row_dict
from services import dashboard, product_rows, supplier_records, create_product, process_sale, receive_purchase, record_waste, report, assistant_answer

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"


def db():
    if "db" not in g:
        g.db = init_db(app.config["DATABASE_PATH"])
    return g.db

@app.before_request
def attach_db():
    if request.path.startswith("/api") or request.path == "/healthz":
        db()

@app.teardown_appcontext
def close_db(error=None):
    conn = g.pop("db", None)
    if conn: conn.close()

@app.context_processor
def inject_user():
    return {"current_user": session.get("user")}


def api_login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return jsonify({"error": "Authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapped


def roles(*allowed):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            user = session.get("user")
            if not user: return jsonify({"error": "Authentication required"}), 401
            if user["role"] not in allowed: return jsonify({"error": "Your role cannot perform this action"}), 403
            token = request.headers.get("X-CSRF-Token")
            if request.method not in ("GET", "HEAD") and token != session.get("csrf_token"):
                return jsonify({"error": "Invalid security token"}), 400
            return fn(*args, **kwargs)
        return wrapped
    return decorator

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/manus-routes.json")
def route_manifest():
    return send_from_directory("public", "manus-routes.json")

@app.get("/healthz")
def healthz():
    return jsonify({"ok": True, "service": "stockpilot"})

@app.post("/api/login")
def login():
    payload = request.get_json(silent=True) or {}
    email, password = payload.get("email", "").strip().lower(), payload.get("password", "")
    user = db().execute("SELECT id,name,email,role,password_hash FROM users WHERE lower(email)=? AND active=1", (email,)).fetchone()
    from db import password_hash
    if not user or password_hash(password) != user["password_hash"]:
        return jsonify({"error": "Incorrect email or password"}), 401
    session.clear(); session.permanent = True
    session["user"] = {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}
    session["csrf_token"] = secrets.token_urlsafe(24)
    return jsonify({"user": session["user"], "csrf_token": session["csrf_token"]})

@app.post("/api/logout")
@api_login_required
def logout():
    session.clear(); return jsonify({"ok": True})

@app.get("/api/bootstrap")
@api_login_required
def bootstrap():
    conn = db(); products = product_rows(conn); notifications = rows(conn, "SELECT * FROM notifications ORDER BY is_read, id DESC LIMIT 20")
    return jsonify({"user": session["user"], "csrf_token": session.get("csrf_token"), "dashboard": dashboard(conn), "products": products, "categories": rows(conn, "SELECT * FROM categories ORDER BY name"), "suppliers": supplier_records(conn), "notifications": notifications, "purchase_orders": rows(conn, "SELECT po.*, s.name supplier FROM purchase_orders po JOIN suppliers s ON s.id=po.supplier_id ORDER BY po.id DESC"), "algorithms": algorithm_payload()})

@app.get("/api/products")
@api_login_required
def products():
    q = request.args.get("q", "").lower(); status = request.args.get("status", "all"); category = request.args.get("category", "all")
    result = product_rows(db())
    if q: result = [p for p in result if q in p["name"].lower() or q in p["sku"].lower() or q in p["barcode"]]
    if category != "all": result = [p for p in result if p["category"] == category]
    if status == "low": result = [p for p in result if p["current_qty"] <= p["reorder_level"]]
    return jsonify(result)

@app.post("/api/products")
@roles("admin", "manager")
def add_product():
    try: return jsonify({"id": create_product(db(), request.get_json(silent=True) or {}, session["user"]["id"])}), 201
    except Exception as exc: return jsonify({"error": str(exc)}), 400

@app.post("/api/sales")
@roles("admin", "manager", "staff")
def add_sale():
    try: return jsonify(process_sale(db(), request.get_json(silent=True) or {}, session["user"]["id"])), 201
    except Exception as exc: return jsonify({"error": str(exc)}), 400

@app.post("/api/purchase-orders/<int:po_id>/receive")
@roles("admin", "manager")
def receive(po_id):
    try: return jsonify({"received": receive_purchase(db(), po_id, session["user"]["id"])})
    except Exception as exc: return jsonify({"error": str(exc)}), 400

@app.post("/api/waste")
@roles("admin", "manager")
def waste():
    try: return jsonify({"recorded": record_waste(db(), request.get_json(silent=True) or {}, session["user"]["id"])})
    except Exception as exc: return jsonify({"error": str(exc)}), 400

@app.post("/api/notifications/<int:notification_id>/read")
@api_login_required
@roles("admin", "manager", "staff")
def mark_read(notification_id):
    db().execute("UPDATE notifications SET is_read=1 WHERE id=?", (notification_id,)); db().commit(); return jsonify({"ok": True})

@app.post("/api/assistant")
@api_login_required
def assistant():
    return jsonify(assistant_answer(db(), (request.get_json(silent=True) or {}).get("question", "")))

@app.get("/api/reports/<report_type>.csv")
@api_login_required
def report_csv(report_type):
    records = report(db(), report_type)
    output = io.StringIO(); writer = csv.DictWriter(output, fieldnames=list(records[0].keys()) if records else ["Message"])
    writer.writeheader()
    if records: writer.writerows(records)
    else: writer.writerow({"Message": "No records for this report"})
    response = make_response(output.getvalue()); response.headers["Content-Type"] = "text/csv"; response.headers["Content-Disposition"] = f"attachment; filename=stockpilot-{report_type}.csv"; return response

@app.get("/api/reports/<report_type>")
@api_login_required
def report_json(report_type): return jsonify(report(db(), report_type))


def algorithm_payload():
    return [
        {"id":"merge-sort","name":"Merge Sort","tag":"Ordering","complexity":"O(n log n)","use":"Sort sales or products predictably for ranking without relying on a built-in sort.","steps":["Split records into halves","Sort each half recursively","Merge by comparing the front item"],"example":"Products sorted by current stock from high to low using a custom merge routine.","test":"[3, 1, 2] → [1, 2, 3]"},
        {"id":"binary-search","name":"Binary Search","tag":"Lookup","complexity":"O(log n)","use":"Find an exact SKU quickly after enforcing sorted SKU data.","steps":["Set low and high indexes","Compare the middle SKU","Discard the impossible half"],"example":"Look up SP-0024 in the sorted product index.","test":"Sorted precondition enforced; missing SKU returns null."},
        {"id":"hash-lookup","name":"Hash SKU Lookup","tag":"Lookup","complexity":"O(1) average / O(n) worst", "use":"Map barcode or SKU to a product for fast checkout scans.","steps":["Build a dictionary keyed by SKU","Hash the incoming key","Return the mapped record"],"example":"Checkout resolves SP-0012 without scanning every product.","test":"Duplicate keys are rejected by the database unique constraint."},
        {"id":"dijkstra","name":"Dijkstra Route Analysis","tag":"Graph","complexity":"O((V+E) log V)","use":"Compare nonnegative warehouse-to-store route distances; distance is not a delivery-performance score.","steps":["Start at the warehouse","Relax the shortest known edge","Repeat from the nearest unvisited node"],"example":"Warehouse → Hub → Store route with nonnegative km weights.","test":"Negative edges are rejected."},
        {"id":"priority-queue","name":"Restock Priority Queue","tag":"Ranking","complexity":"O(n log n)","use":"Surface critical stock gaps before watch-level gaps.","steps":["Push alerts into a min-heap","Rank severity and gap","Pop the next action"],"example":"Critical grocery shortages rise above healthy categories.","test":"Critical status is always returned before watch status."},
        {"id":"fefo","name":"FEFO Batch Selection","tag":"Expiry","complexity":"O(n log n)","use":"Deduct the batch expiring first for perishables.","steps":["Sort positive-quantity batches by expiry","Take from the earliest expiry","Continue until quantity is fulfilled"],"example":"Fresh milk batch expiring in 9 days is picked before the 35-day batch.","test":"Selection never treats expired stock as sellable."}
    ]

if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000")); app.run(host="0.0.0.0", port=port, debug=False)
