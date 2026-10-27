import hashlib
import json
import os
import random
import sqlite3
import ssl
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote, urlsplit

SCHEMA = """
CREATE TABLE IF NOT EXISTS workspaces (id INTEGER PRIMARY KEY, name TEXT NOT NULL, slug TEXT UNIQUE NOT NULL, is_demo INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','manager','staff')), active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);
CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, contact TEXT, email TEXT, lead_time_days INTEGER DEFAULT 4, reliability REAL DEFAULT 0.8, status TEXT DEFAULT 'active');
CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, sku TEXT UNIQUE NOT NULL, barcode TEXT UNIQUE NOT NULL, name TEXT NOT NULL, description TEXT, category_id INTEGER NOT NULL, supplier_id INTEGER, purchase_cost NUMERIC NOT NULL CHECK(purchase_cost >= 0), selling_price NUMERIC NOT NULL CHECK(selling_price >= 0), current_qty INTEGER NOT NULL DEFAULT 0 CHECK(current_qty >= 0), minimum_stock INTEGER NOT NULL DEFAULT 5 CHECK(minimum_stock >= 0), reorder_level INTEGER NOT NULL DEFAULT 10 CHECK(reorder_level >= 0), unit TEXT DEFAULT 'unit', expiry_required INTEGER DEFAULT 0, active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(category_id) REFERENCES categories(id), FOREIGN KEY(supplier_id) REFERENCES suppliers(id));
CREATE TABLE IF NOT EXISTS stock_batches (id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, batch_code TEXT UNIQUE NOT NULL, quantity INTEGER NOT NULL CHECK(quantity >= 0), expiry_date TEXT, received_date TEXT NOT NULL, FOREIGN KEY(product_id) REFERENCES products(id));
CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, invoice_no TEXT UNIQUE NOT NULL, sale_date TEXT NOT NULL, subtotal NUMERIC NOT NULL, discount NUMERIC DEFAULT 0, tax NUMERIC DEFAULT 0, total NUMERIC NOT NULL, payment_method TEXT DEFAULT 'card', status TEXT DEFAULT 'completed', user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id));
CREATE TABLE IF NOT EXISTS sale_items (id INTEGER PRIMARY KEY, sale_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0), unit_price NUMERIC NOT NULL, cost_price NUMERIC NOT NULL, FOREIGN KEY(sale_id) REFERENCES sales(id), FOREIGN KEY(product_id) REFERENCES products(id));
CREATE TABLE IF NOT EXISTS stock_movements (id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL, batch_id INTEGER, movement_type TEXT NOT NULL, quantity INTEGER NOT NULL, reason TEXT, reference TEXT, created_at TEXT NOT NULL, user_id INTEGER, FOREIGN KEY(product_id) REFERENCES products(id));
CREATE TABLE IF NOT EXISTS purchase_orders (id INTEGER PRIMARY KEY, po_number TEXT UNIQUE NOT NULL, supplier_id INTEGER NOT NULL, order_date TEXT NOT NULL, expected_date TEXT, status TEXT DEFAULT 'pending', total NUMERIC DEFAULT 0, FOREIGN KEY(supplier_id) REFERENCES suppliers(id));
CREATE TABLE IF NOT EXISTS purchase_order_items (id INTEGER PRIMARY KEY, po_id INTEGER NOT NULL, product_id INTEGER NOT NULL, ordered_qty INTEGER NOT NULL, received_qty INTEGER DEFAULT 0, unit_cost NUMERIC NOT NULL, FOREIGN KEY(po_id) REFERENCES purchase_orders(id), FOREIGN KEY(product_id) REFERENCES products(id));
CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL, message TEXT NOT NULL, severity TEXT DEFAULT 'info', entity_type TEXT, entity_id INTEGER, is_read INTEGER DEFAULT 0, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT NOT NULL, entity TEXT, entity_id INTEGER, detail TEXT, created_at TEXT NOT NULL, user_id INTEGER);
CREATE TABLE IF NOT EXISTS inventory_policies (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_movements_product ON stock_movements(product_id, created_at);
CREATE INDEX IF NOT EXISTS idx_batches_expiry ON stock_batches(expiry_date);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
"""

MYSQL_SCHEMA = [
    """CREATE TABLE IF NOT EXISTS workspaces (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(180) NOT NULL, slug VARCHAR(120) UNIQUE NOT NULL, is_demo TINYINT DEFAULT 0, created_at VARCHAR(32) DEFAULT NULL)""",
    """CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(160) NOT NULL, email VARCHAR(255) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL, role VARCHAR(20) NOT NULL, active TINYINT DEFAULT 1)""",
    """CREATE TABLE IF NOT EXISTS categories (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(120) UNIQUE NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS suppliers (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(180) NOT NULL, contact VARCHAR(80), email VARCHAR(255), lead_time_days INT DEFAULT 4, reliability DOUBLE DEFAULT 0.8, status VARCHAR(20) DEFAULT 'active')""",
    """CREATE TABLE IF NOT EXISTS products (id BIGINT PRIMARY KEY AUTO_INCREMENT, sku VARCHAR(60) UNIQUE NOT NULL, barcode VARCHAR(80) UNIQUE NOT NULL, name VARCHAR(220) NOT NULL, description TEXT, category_id BIGINT NOT NULL, supplier_id BIGINT, purchase_cost DECIMAL(12,2) NOT NULL, selling_price DECIMAL(12,2) NOT NULL, current_qty INT NOT NULL DEFAULT 0, minimum_stock INT NOT NULL DEFAULT 5, reorder_level INT NOT NULL DEFAULT 10, unit VARCHAR(30) DEFAULT 'unit', expiry_required TINYINT DEFAULT 0, active TINYINT DEFAULT 1, created_at VARCHAR(32) DEFAULT NULL, FOREIGN KEY(category_id) REFERENCES categories(id), FOREIGN KEY(supplier_id) REFERENCES suppliers(id))""",
    """CREATE TABLE IF NOT EXISTS stock_batches (id BIGINT PRIMARY KEY AUTO_INCREMENT, product_id BIGINT NOT NULL, batch_code VARCHAR(100) UNIQUE NOT NULL, quantity INT NOT NULL, expiry_date VARCHAR(32), received_date VARCHAR(32) NOT NULL, FOREIGN KEY(product_id) REFERENCES products(id))""",
    """CREATE TABLE IF NOT EXISTS sales (id BIGINT PRIMARY KEY AUTO_INCREMENT, invoice_no VARCHAR(80) UNIQUE NOT NULL, sale_date VARCHAR(32) NOT NULL, subtotal DECIMAL(12,2) NOT NULL, discount DECIMAL(12,2) DEFAULT 0, tax DECIMAL(12,2) DEFAULT 0, total DECIMAL(12,2) NOT NULL, payment_method VARCHAR(30) DEFAULT 'card', status VARCHAR(20) DEFAULT 'completed', user_id BIGINT, FOREIGN KEY(user_id) REFERENCES users(id))""",
    """CREATE TABLE IF NOT EXISTS sale_items (id BIGINT PRIMARY KEY AUTO_INCREMENT, sale_id BIGINT NOT NULL, product_id BIGINT NOT NULL, quantity INT NOT NULL, unit_price DECIMAL(12,2) NOT NULL, cost_price DECIMAL(12,2) NOT NULL, FOREIGN KEY(sale_id) REFERENCES sales(id), FOREIGN KEY(product_id) REFERENCES products(id))""",
    """CREATE TABLE IF NOT EXISTS stock_movements (id BIGINT PRIMARY KEY AUTO_INCREMENT, product_id BIGINT NOT NULL, batch_id BIGINT NULL, movement_type VARCHAR(30) NOT NULL, quantity INT NOT NULL, reason VARCHAR(300), reference VARCHAR(100), created_at VARCHAR(32) NOT NULL, user_id BIGINT, FOREIGN KEY(product_id) REFERENCES products(id))""",
    """CREATE TABLE IF NOT EXISTS purchase_orders (id BIGINT PRIMARY KEY AUTO_INCREMENT, po_number VARCHAR(80) UNIQUE NOT NULL, supplier_id BIGINT NOT NULL, order_date VARCHAR(32) NOT NULL, expected_date VARCHAR(32), status VARCHAR(20) DEFAULT 'pending', total DECIMAL(12,2) DEFAULT 0, FOREIGN KEY(supplier_id) REFERENCES suppliers(id))""",
    """CREATE TABLE IF NOT EXISTS purchase_order_items (id BIGINT PRIMARY KEY AUTO_INCREMENT, po_id BIGINT NOT NULL, product_id BIGINT NOT NULL, ordered_qty INT NOT NULL, received_qty INT DEFAULT 0, unit_cost DECIMAL(12,2) NOT NULL, FOREIGN KEY(po_id) REFERENCES purchase_orders(id), FOREIGN KEY(product_id) REFERENCES products(id))""",
    """CREATE TABLE IF NOT EXISTS notifications (id BIGINT PRIMARY KEY AUTO_INCREMENT, kind VARCHAR(30) NOT NULL, title VARCHAR(220) NOT NULL, message VARCHAR(600) NOT NULL, severity VARCHAR(20) DEFAULT 'info', entity_type VARCHAR(40), entity_id BIGINT, is_read TINYINT DEFAULT 0, created_at VARCHAR(32) NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS audit_logs (id BIGINT PRIMARY KEY AUTO_INCREMENT, action VARCHAR(80) NOT NULL, entity VARCHAR(80), entity_id BIGINT, detail VARCHAR(1000), created_at VARCHAR(32) NOT NULL, user_id BIGINT, FOREIGN KEY(user_id) REFERENCES users(id))""",
    """CREATE TABLE IF NOT EXISTS inventory_policies (key_name VARCHAR(80) PRIMARY KEY, value VARCHAR(120) NOT NULL)""",
    """CREATE INDEX idx_products_category ON products(category_id)""",
    """CREATE INDEX idx_movements_product ON stock_movements(product_id, created_at)""",
    """CREATE INDEX idx_batches_expiry ON stock_batches(expiry_date)""",
    """CREATE INDEX idx_sales_date ON sales(sale_date)""",
]


class MySQLRow(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class MySQLResult:
    def __init__(self, cursor):
        self.cursor = cursor

    @staticmethod
    def _normalize(row):
        if not row:
            return row
        result = MySQLRow(row)
        for key, value in list(result.items()):
            if isinstance(value, Decimal):
                result[key] = float(value)
                continue
            if hasattr(value, "isoformat"):
                result[key] = value.isoformat()
        return result

    def fetchone(self):
        return self._normalize(self.cursor.fetchone())

    def fetchall(self):
        return [self._normalize(row) for row in self.cursor.fetchall()]

    def __iter__(self):
        return iter(self.fetchall())

    @property
    def lastrowid(self):
        return self.cursor.lastrowid


class MySQLConnection:
    def __init__(self, dsn):
        import pymysql

        parsed = urlsplit(dsn)
        ssl_context = ssl.create_default_context()
        self.raw = pymysql.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=parsed.path.lstrip("/"),
            charset="utf8mb4",
            autocommit=False,
            cursorclass=pymysql.cursors.DictCursor,
            ssl=ssl_context,
        )

    @staticmethod
    def _sql(query):
        query = query.replace("INSERT OR IGNORE", "INSERT IGNORE")
        query = query.replace("INSERT OR REPLACE INTO inventory_policies(key,value)", "INSERT INTO inventory_policies(key_name,value)")
        if "last_insert_rowid()" in query.lower():
            query = "SELECT LAST_INSERT_ID()"
        return query.replace("%", "%%").replace("?", "%s")

    def execute(self, query, params=()):
        cursor = self.raw.cursor()
        cursor.execute(self._sql(query), params)
        return MySQLResult(cursor)

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def close(self):
        self.raw.close()

    def executescript(self, script):
        for statement in script.split(";"):
            if statement.strip():
                self.execute(statement)

PRODUCT_NAMES = [
    ("Basmati Rice 5kg", "Grocery", 290, 349), ("Toor Dal 1kg", "Grocery", 116, 149), ("Wheat Flour 5kg", "Grocery", 220, 269), ("Sunflower Oil 1L", "Grocery", 112, 139), ("Iodized Salt 1kg", "Grocery", 18, 25),
    ("Green Tea 25 bags", "Beverages", 88, 129), ("Filter Coffee 200g", "Beverages", 142, 189), ("Orange Juice 1L", "Beverages", 76, 109), ("Sparkling Water 750ml", "Beverages", 42, 65), ("Cola 2L", "Beverages", 68, 89),
    ("Corn Flakes 500g", "Breakfast", 164, 219), ("Oats 1kg", "Breakfast", 125, 169), ("Honey 500g", "Breakfast", 210, 279), ("Peanut Butter 340g", "Breakfast", 185, 239), ("Muesli 500g", "Breakfast", 240, 319),
    ("Chocolate Bar 45g", "Snacks", 22, 35), ("Potato Chips 100g", "Snacks", 31, 49), ("Trail Mix 200g", "Snacks", 122, 169), ("Roasted Almonds 200g", "Snacks", 178, 229), ("Granola Bar 6 pack", "Snacks", 95, 139),
    ("Dishwash Liquid 500ml", "Home Care", 72, 99), ("Laundry Powder 2kg", "Home Care", 182, 229), ("Floor Cleaner 1L", "Home Care", 96, 129), ("Paper Towels 4 pack", "Home Care", 116, 159), ("Garbage Bags 30 pack", "Home Care", 82, 119),
    ("Shampoo 340ml", "Personal Care", 174, 239), ("Hand Wash 250ml", "Personal Care", 62, 89), ("Toothpaste 150g", "Personal Care", 88, 119), ("Face Wash 100ml", "Personal Care", 124, 169), ("Body Lotion 200ml", "Personal Care", 145, 199),
    ("Notebook A5", "Stationery", 28, 45), ("Gel Pen Set", "Stationery", 42, 69), ("Printer Paper 500s", "Stationery", 208, 269), ("Sticky Notes", "Stationery", 25, 39), ("Packing Tape", "Stationery", 36, 55),
    ("LED Bulb 9W", "Utilities", 64, 89), ("AA Batteries 4 pack", "Utilities", 96, 129), ("Extension Cord", "Utilities", 198, 259), ("USB-C Cable", "Utilities", 142, 199), ("Torch Light", "Utilities", 118, 159),
    ("Apples 1kg", "Fresh Produce", 112, 149), ("Bananas 1 dozen", "Fresh Produce", 48, 69), ("Tomatoes 1kg", "Fresh Produce", 38, 59), ("Potatoes 2kg", "Fresh Produce", 58, 79), ("Onions 1kg", "Fresh Produce", 42, 65),
    ("Greek Yogurt 400g", "Chilled", 72, 99), ("Cheddar Cheese 200g", "Chilled", 138, 179), ("Butter 500g", "Chilled", 226, 289), ("Fresh Milk 1L", "Chilled", 58, 72), ("Eggs 12 pack", "Chilled", 76, 99),
    ("Chicken Noodles 70g", "Instant Meals", 18, 28), ("Pasta 500g", "Instant Meals", 62, 89), ("Tomato Pasta Sauce", "Instant Meals", 88, 119), ("Instant Soup 3 pack", "Instant Meals", 64, 95),
]


def password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


def connect(path):
    dsn = os.getenv("DATABASE_URL", "").strip()
    if dsn.startswith(("mysql://", "mysql+mysqlconnector://", "mysql+pymysql://")):
        return MySQLConnection(dsn)
    conn = sqlite3.connect(path, timeout=20, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


TENANT_TABLES = ("users", "categories", "suppliers", "products", "stock_batches", "sales", "sale_items", "stock_movements", "purchase_orders", "purchase_order_items", "notifications", "audit_logs", "inventory_policies")
_TENANCY_READY = False


def _has_column(conn, table, column, is_mysql):
    if is_mysql:
        return bool(conn.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=? AND COLUMN_NAME=?", (table, column)).fetchone())
    return bool(conn.execute(f"PRAGMA table_info({table})").fetchall() and any(r[1] == column for r in conn.execute(f"PRAGMA table_info({table})").fetchall()))


def ensure_tenancy(conn, is_mysql):
    global _TENANCY_READY
    if _TENANCY_READY:
        return
    if is_mysql:
        conn.execute("CREATE TABLE IF NOT EXISTS workspaces (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(180) NOT NULL, slug VARCHAR(120) UNIQUE NOT NULL, is_demo TINYINT DEFAULT 0, created_at VARCHAR(32) DEFAULT NULL)")
        column_type = "BIGINT"
    else:
        conn.execute("CREATE TABLE IF NOT EXISTS workspaces (id INTEGER PRIMARY KEY, name TEXT NOT NULL, slug TEXT UNIQUE NOT NULL, is_demo INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        column_type = "INTEGER"
    for table in TENANT_TABLES:
        if not _has_column(conn, table, "workspace_id", is_mysql):
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN workspace_id {column_type}")
            except Exception as exc:
                if "duplicate" not in str(exc).lower() and "exists" not in str(exc).lower():
                    raise
    demo = conn.execute("SELECT id FROM workspaces WHERE slug=?", ("demo",)).fetchone()
    if not demo:
        cur = conn.execute("INSERT INTO workspaces(name,slug,is_demo,created_at) VALUES(?,?,?,?)", ("Northstar Pantry", "demo", 1, date.today().isoformat()))
        demo_id = cur.lastrowid
    else:
        demo_id = demo["id"]
    for table in TENANT_TABLES:
        conn.execute(f"UPDATE {table} SET workspace_id=? WHERE workspace_id IS NULL", (demo_id,))
    conn.commit()
    _TENANCY_READY = True


def init_db(path):
    dsn = os.getenv("DATABASE_URL", "").strip()
    is_mysql = dsn.startswith(("mysql://", "mysql+mysqlconnector://", "mysql+pymysql://"))
    if not is_mysql:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = connect(path)
    if is_mysql:
        for statement in MYSQL_SCHEMA:
            try:
                conn.execute(statement)
            except Exception as exc:
                if "already exists" not in str(exc).lower() and "duplicate key name" not in str(exc).lower():
                    conn.rollback()
                    conn.close()
                    raise
        conn.commit()
    else:
        conn.executescript(SCHEMA)
    ensure_tenancy(conn, is_mysql)
    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        seed(conn)
    conn.commit()
    return conn


def seed(conn):
    today = date.today()
    for role, name, email in [("admin", "Aarav Mehta", "owner@stockpilot.ai"), ("manager", "Maya Shah", "manager@stockpilot.ai"), ("staff", "Rohan Das", "staff@stockpilot.ai")]:
        conn.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)", (name, email, password_hash("demo123"), role))
    user_ids = {r["email"]: r["id"] for r in conn.execute("SELECT id,email FROM users")}
    admin_id = user_ids["owner@stockpilot.ai"]
    manager_id = user_ids["manager@stockpilot.ai"]
    categories = sorted({row[1] for row in PRODUCT_NAMES})
    for name in categories:
        conn.execute("INSERT INTO categories(name) VALUES(?)", (name,))
    suppliers = [("Northstar Wholesale", "+91 80 4400 2211", "orders@northstar.example", 3, .94), ("FreshRoute Foods", "+91 80 4400 3344", "dispatch@freshroute.example", 2, .89), ("BlueCart Traders", "+91 80 4400 5588", "hello@bluecart.example", 6, .78), ("Evergreen Essentials", "+91 80 4400 6677", "supply@evergreen.example", 5, .84)]
    for row in suppliers:
        conn.execute("INSERT INTO suppliers(name,contact,email,lead_time_days,reliability) VALUES(?,?,?,?,?)", row)
    cat_ids = {r["name"]: r["id"] for r in conn.execute("SELECT * FROM categories")}
    supplier_ids = [r["id"] for r in conn.execute("SELECT * FROM suppliers")]
    random.seed(42)
    for idx, (name, category, cost, price) in enumerate(PRODUCT_NAMES, 1):
        qty = [7, 18, 46, 72, 4, 31, 55, 12][idx % 8]
        minimum = 8 if category in ("Fresh Produce", "Chilled") else 12
        reorder = minimum + 10
        supplier_id = supplier_ids[idx % len(supplier_ids)]
        expiry_required = 1 if category in ("Fresh Produce", "Chilled", "Beverages", "Breakfast") else 0
        conn.execute("INSERT INTO products(sku,barcode,name,description,category_id,supplier_id,purchase_cost,selling_price,current_qty,minimum_stock,reorder_level,unit,expiry_required) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (f"SP-{idx:04d}", f"890100{idx:06d}", name, f"Fictional demo SKU for {name.lower()}.", cat_ids[category], supplier_id, cost, price, qty, minimum, reorder, "pack" if "pack" in name.lower() else "unit", expiry_required))
        product_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        expiry = (today + timedelta(days=[9, 18, 35, 60, 120][idx % 5])).isoformat() if expiry_required else None
        conn.execute("INSERT INTO stock_batches(product_id,batch_code,quantity,expiry_date,received_date) VALUES(?,?,?,?,?)", (product_id, f"B-{idx:04d}-A", qty, expiry, (today - timedelta(days=idx % 16)).isoformat()))
        conn.execute("INSERT INTO stock_movements(product_id,movement_type,quantity,reason,reference,created_at,user_id) VALUES(?,?,?,?,?,?,?)", (product_id, "opening", qty, "Demo opening stock", "SEED", (today - timedelta(days=95)).isoformat(), admin_id))
    product_rows = list(conn.execute("SELECT p.*, c.name category FROM products p JOIN categories c ON c.id=p.category_id"))
    for day_offset in range(90, 0, -3):
        sale_date = today - timedelta(days=day_offset)
        for j in range(2):
            product = product_rows[(day_offset + j * 7) % len(product_rows)]
            quantity = 1 + ((day_offset + j) % 4)
            subtotal = Decimal(str(product["selling_price"])) * quantity
            cur = conn.execute("INSERT INTO sales(invoice_no,sale_date,subtotal,discount,tax,total,payment_method,status,user_id) VALUES(?,?,?,?,?,?,?,?,?)", (f"INV-{sale_date.strftime('%m%d')}-{j}", sale_date.isoformat(), str(subtotal), "0", str(subtotal * Decimal("0.05")), str(subtotal * Decimal("1.05")), "upi" if j else "card", "completed", manager_id))
            sale_id = cur.lastrowid
            conn.execute("INSERT INTO sale_items(sale_id,product_id,quantity,unit_price,cost_price) VALUES(?,?,?,?,?)", (sale_id, product["id"], quantity, product["selling_price"], product["purchase_cost"]))
    po_rows = [("PO-2401", supplier_ids[0], "pending", today + timedelta(days=4)), ("PO-2398", supplier_ids[1], "partial", today + timedelta(days=1)), ("PO-2394", supplier_ids[2], "received", today - timedelta(days=6))]
    for po, supplier, status, expected in po_rows:
        cur = conn.execute("INSERT INTO purchase_orders(po_number,supplier_id,order_date,expected_date,status,total) VALUES(?,?,?,?,?,?)", (po, supplier, (today - timedelta(days=3)).isoformat(), expected.isoformat(), status, "0"))
        po_id = cur.lastrowid
        for product in product_rows[:2]:
            ordered = 24
            received = 8 if status == "partial" else (24 if status == "received" else 0)
            conn.execute("INSERT INTO purchase_order_items(po_id,product_id,ordered_qty,received_qty,unit_cost) VALUES(?,?,?,?,?)", (po_id, product["id"], ordered, received, product["purchase_cost"]))
    expiring = conn.execute("SELECT id,name,current_qty FROM products WHERE expiry_required=1 AND current_qty>0 AND id%5=1 LIMIT 3").fetchall()
    for product in expiring:
        conn.execute("INSERT INTO notifications(kind,title,message,severity,entity_type,entity_id,created_at) VALUES(?,?,?,?,?,?,?)", ("expiry", "Expiry window approaching", f"{product['name']} has a batch expiring soon.", "warning", "product", product["id"], today.isoformat()))
    for product in conn.execute("SELECT id,name,current_qty,minimum_stock FROM products WHERE current_qty<=minimum_stock LIMIT 4"):
        conn.execute("INSERT INTO notifications(kind,title,message,severity,entity_type,entity_id,created_at) VALUES(?,?,?,?,?,?,?)", ("low_stock", "Critical stock level", f"{product['name']} is at {product['current_qty']} units; reorder level is {product['minimum_stock']}.", "critical", "product", product["id"], today.isoformat()))
    conn.execute("INSERT OR REPLACE INTO inventory_policies(key,value) VALUES('safety_stock_days','2')")
    conn.execute("INSERT OR REPLACE INTO inventory_policies(key,value) VALUES('target_days','14')")

def row_dict(row):
    return dict(row) if row else None

def rows(conn, query, params=()):
    return [dict(r) for r in conn.execute(query, params).fetchall()]

def json_dumps(value):
    return json.dumps(value, separators=(",", ":"))
