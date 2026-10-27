# StockPilot AI Architecture

StockPilot uses a simple layered architecture. Flask routes accept browser requests and apply authentication, role checks, CSRF checks, and safe error handling. `services.py` owns transactional operations such as creating a sale, receiving a purchase order, and creating a product. `analytics.py` owns demand calculations, restocking, category analysis, and forecast baselines. `algorithms.py` contains the custom DAA implementations. `db.py` uses the project-scoped managed MySQL-compatible database whenever `DATABASE_URL` is supplied, which is the Preview and production default; SQLite remains a clearly labelled local fallback. Oracle is the academic production target and the SQL/PLSQL artifacts under `oracle/` are the deployment contract.

The normalized entities are users/roles, categories, products, suppliers, product-supplier relationships, stock batches, stock movements, sales, sale items, purchase orders, purchase order items, notifications, audit logs, and inventory policies. Products point to categories and preferred suppliers. Batches point to products and hold quantity plus expiry. Sales point to users and contain sale items. Every stock-affecting operation updates `products.current_qty`, changes batch quantities when needed, and inserts an immutable movement row inside the same transaction. A reconciliation query can compare product quantity against the sum of positive/negative movement quantities.

The assistant does not generate SQL. It classifies a small set of supported phrases into parameterized service functions, returning an explainable answer. The restocking baseline is intentionally transparent: average daily demand over completed sales, lead-time demand, safety stock, reorder point, and target-stock gap. In an Oracle deployment, the core receipt, movement, sale deduction, valuation, and low-stock cursor operations execute through `INVENTORY_PKG`; the Python adapter can call those procedures using `python-oracledb`.

## Running locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DEMO_MODE="true"
$env:PORT="3000"
python app.py
```

Open `http://localhost:3000`. With a managed database, the application creates its schema and seeds the fictional demo dataset once, then reuses the same database across Preview requests, process restarts, and published deployments. Demo accounts use password `demo123`: `owner@stockpilot.ai`, `manager@stockpilot.ai`, and `staff@stockpilot.ai`. These are fictional seed credentials for evaluation only, not production defaults.

## Persistence model

`DATABASE_URL` is supplied by Webdev for the shared managed MySQL-compatible database. Each request opens a database connection, performs its reads or transaction, commits successful writes, and closes the connection. The runtime filesystem is not treated as durable storage. A local SQLite file is used only when `DATABASE_URL` is intentionally absent. Existing application tables are created additively and demo seed data is inserted only when the managed `products` table is empty.
