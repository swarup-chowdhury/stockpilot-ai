# StockPilot AI

## Smart Inventory & Demand Intelligence System

StockPilot AI is a full-stack inventory management and demand-intelligence application built with Python and Flask. It is designed for grocery shops, supermarkets, retail stores, wholesalers, and small businesses that need a reliable way to manage products, suppliers, sales, purchase orders, stock batches, expiry dates, reports, and intelligent restocking decisions.

The project is implemented as a working business application rather than a static dashboard. Sales reduce inventory, purchase receipts increase inventory, waste uses FEFO batch selection, reports are generated from stored records, and all stock-affecting operations create an auditable movement history.

> **Academic project:** Python Programming — MCA (AI/ML), Chandigarh University  
> **Student:** Swarup Chowdhury  
> **Roll number:** 26MCI10229  
> **Section:** 26MAM4(B)  
> **Submitted to:** Mr. Sanjeev Kumar (E20624)

## Links

- **Live application:** [StockPilot AI](https://stockpilot-tg4klhpc.manus.space/)
- **GitHub repository:** [github.com/swarup-chowdhury/stockpilot-ai](https://github.com/swarup-chowdhury/stockpilot-ai)
- **Project report:** [`reports/StockPilot_AI_Python_Programming_Project_Report_Swarup_Chowdhury.pdf`](reports/StockPilot_AI_Python_Programming_Project_Report_Swarup_Chowdhury.pdf)
- **Editable report:** [`reports/StockPilot_AI_Python_Programming_Project_Report_Swarup_Chowdhury.docx`](reports/StockPilot_AI_Python_Programming_Project_Report_Swarup_Chowdhury.docx)

## Table of Contents

- [Project Overview](#project-overview)
- [Main Features](#main-features)
- [User Roles and Workspaces](#user-roles-and-workspaces)
- [Technology Stack](#technology-stack)
- [Application Architecture](#application-architecture)
- [Project Structure](#project-structure)
- [Demo Login](#demo-login)
- [Local Installation](#local-installation)
- [Environment Configuration](#environment-configuration)
- [Database Design](#database-design)
- [Core Business Workflows](#core-business-workflows)
- [Restocking Methodology](#restocking-methodology)
- [Algorithms Demonstrated](#algorithms-demonstrated)
- [API Overview](#api-overview)
- [Reports and Exports](#reports-and-exports)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Oracle and PL/SQL Artifacts](#oracle-and-plsql-artifacts)
- [Security](#security)
- [Academic Relevance](#academic-relevance)
- [Limitations and Future Scope](#limitations-and-future-scope)
- [License](#license)

## Project Overview

Many small businesses manage inventory using notebooks or disconnected spreadsheets. This makes it difficult to answer important operational questions:

1. What products are currently available?
2. Which products are low in stock?
3. Which batches are expiring soon or already expired?
4. How much inventory value is currently held?
5. Which products are selling quickly or slowly?
6. What should be purchased next?
7. Can every stock change be traced back to a business event?

StockPilot AI brings these activities into a single web application. It combines transaction-safe inventory operations with explainable analytics so users can understand not only **what** the system recommends, but also **why** it recommends it.

## Main Features

### Executive dashboard

- Active product count
- Inventory valuation at purchase cost
- Estimated retail value
- Today’s sales and gross profit
- Low-stock products
- Expiring and expired batches
- Pending purchase orders
- Fast movers and slow movers
- Sales momentum and daily trends
- Category distribution
- Critical operational alerts
- Recent stock movement history

### Product and inventory management

- Add, edit, view, search, filter, and deactivate products
- SKU and barcode support
- Duplicate SKU prevention
- Category and supplier mapping
- Purchase price and selling price
- Current quantity and minimum stock level
- Reorder level and lead-time information
- Product status and expiry tracking
- Inventory valuation
- Auditable stock ledger

### Sales and billing

- Multi-item sales
- Decimal-safe currency calculations
- Discount and tax support
- Payment method and payment status
- Stock validation before sale completion
- Safe inventory deduction
- FEFO batch selection for perishable products
- Printable invoice-ready sale records
- Sale movement and audit history

### Suppliers and purchase orders

- Supplier directory
- Product-supplier mapping
- Purchase order creation
- Purchase order line items
- Draft, sent, partial, received, and cancelled statuses
- Partial receiving support
- Supplier purchase history
- Receipt movement and inventory updates
- Supplier delivery and price information

### Expiry and waste management

- Batch-level expiry dates
- Expiring-soon alerts
- Expired-stock alerts
- FEFO batch selection
- Waste and damage recording
- Waste reason tracking
- Stock movement and audit trail
- Expiry and waste reports

### Smart restocking

The restocking engine displays:

- Current stock
- Average daily demand
- Supplier lead-time demand
- Safety stock
- Reorder point
- Target stock
- Suggested purchase quantity
- Estimated purchase cost
- Suggested supplier
- Explanation or reason
- Confidence and data-quality level

The recommendations are explainable business-rule recommendations. They are not represented as a black-box machine-learning model.

### Analytics

- Daily sales totals
- Monthly sales totals
- Product demand history
- Category performance
- Fast and slow movers
- Weekly demand patterns
- Baseline 7-day and 30-day forecasting
- Forecast limitations
- Mean absolute error when sufficient history exists
- Inventory valuation reports
- Sales and profit summaries

### Algorithm Insights

The Algorithm Lab demonstrates custom algorithms with a business use case, steps, complexity, and working examples:

- Merge Sort
- Binary Search with sorted-input precondition
- Hash-based SKU lookup
- Dijkstra shortest-path routing
- Priority queue for critical restocking alerts
- FEFO batch selection

### Business assistant

The assistant supports safe, parameterized business questions such as:

- Which products are low in stock?
- What is expiring soon?
- Which products are fast movers?
- What should be reordered?
- What is the current inventory value?
- What sales were recorded recently?

The assistant does not execute arbitrary SQL, Python code, or user-supplied commands.

### Reports and exports

- Inventory valuation
- Low-stock products
- Expiry and waste
- Sales and profit
- Purchases
- Supplier history
- Fast and slow movers
- Forecast summary
- Stock audit
- CSV exports
- Printable report views

## User Roles and Workspaces

StockPilot AI supports backend-enforced roles:

| Role | Typical permissions |
|---|---|
| Admin / Owner | Full workspace administration, products, sales, purchasing, reports, users, and settings |
| Inventory Manager | Product, supplier, purchase order, receiving, stock, expiry, and report operations |
| Staff | Sales, billing, product lookup, and permitted day-to-day inventory actions |

### Account-scoped workspaces

Every registered admin receives a separate workspace. The persistent database uses a workspace ID to isolate each account’s users and operational data.

- The built-in demo account contains fictional demo records.
- New accounts start with an empty operational workspace.
- A new account does not receive copied demo products, suppliers, sales, or purchase orders.
- Dashboard greetings and workspace labels use the authenticated user’s own information.
- Reads and writes are filtered by the authenticated workspace on the backend.

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Web framework | Flask 3.0.3 |
| Database adapter | PyMySQL for managed MySQL-compatible persistence |
| Local database | SQLite fallback for local development |
| Production target | Oracle Database and PL/SQL artifacts included |
| Frontend | HTML5, CSS3, JavaScript |
| Styling | Responsive custom CSS with dashboard design system |
| Analytics | Python standard-library calculations, Decimal arithmetic, optional NumPy/pandas support |
| Authentication | Hashed passwords, secure sessions, role enforcement, CSRF protection |
| Testing | PyTest and Python compilation checks |
| Packaging | Docker |
| Version control | Git and GitHub |

## Application Architecture

```text
Browser
  |
  | HTML / CSS / JavaScript fetch requests
  v
Flask routes in app.py
  |
  | Authentication, sessions, roles, CSRF, validation
  v
Service layer in services.py
  |
  | Transaction-safe business operations
  v
Database adapter in db.py
  |
  +--> Managed MySQL-compatible database when DATABASE_URL exists
  |
  +--> SQLite local fallback when DATABASE_URL is absent
  |
  +--> Oracle schema/package artifacts under oracle/

Analytics and algorithms
  |
  +--> analytics.py
  +--> algorithms.py
```

### Request flow example

1. A user submits a sale from the browser.
2. JavaScript sends the sale payload to the protected Flask API.
3. Flask validates the session, role, CSRF token, and request body.
4. `services.py` validates product availability and Decimal-safe totals.
5. FEFO chooses the earliest-expiring eligible batches.
6. Product quantities and batch quantities are updated.
7. Sale items, stock movements, audit records, and notifications are written.
8. The transaction commits only when every line succeeds.
9. The frontend refreshes data from the database-backed bootstrap endpoint.

## Project Structure

```text
stockpilot/
├── app.py                         # Flask routes, auth, APIs, reports, health endpoint
├── config.py                      # Environment-driven configuration
├── db.py                          # Database adapters, schema, migration, demo seed
├── services.py                    # Transactional business services
├── analytics.py                   # Demand, forecast, valuation, and restocking helpers
├── algorithms.py                  # Custom DAA algorithms
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Production container configuration
├── .env.example                   # Safe environment template
├── public/
│   └── manus-routes.json          # Managed route manifest
├── templates/
│   └── index.html                 # Application shell and authentication forms
├── static/
│   ├── app.js                     # Client-side controller and API actions
│   ├── styles.css                 # Responsive dashboard styles
│   └── favicon.svg                # First-party favicon
├── oracle/
│   ├── schema.sql                 # Oracle tables, constraints, indexes, sequences
│   ├── inventory_pkg.sql          # Oracle PL/SQL package specification/body
│   └── seed_data.sql              # Oracle demo seed guidance
├── docs/
│   ├── ARCHITECTURE.md            # System architecture
│   ├── DAA.md                     # Algorithms and complexity
│   ├── ORACLE_SETUP.md            # Oracle setup and deployment notes
│   ├── TRAINING_GUIDE.md          # End-user training guide
│   └── MULTI_USER_PERSISTENCE.md  # Workspace isolation documentation
├── tests/
│   └── test_core.py               # Core algorithm and business-rule tests
└── reports/
    ├── StockPilot_AI_Python_Programming_Project_Report_Swarup_Chowdhury.pdf
    └── StockPilot_AI_Python_Programming_Project_Report_Swarup_Chowdhury.docx
```

## Demo Login

Use the fictional demo account for evaluation:

```text
Email:    owner@stockpilot.ai
Password: demo123
```

The demo workspace is clearly labelled as fictional evaluation data. Do not use this demo password for a production deployment.

To create a new private workspace, choose **Create new admin** on the login page and provide:

- Full name
- Email address
- Password
- Workspace name

A new workspace starts with no copied demo operational data.

## Local Installation

### Requirements

- Python 3.11 or later
- Git
- SQLite for local fallback, or a reachable MySQL-compatible database
- Optional: Docker
- Optional: Oracle client/database for Oracle deployment work

### Clone the project

```bash
git clone https://github.com/swarup-chowdhury/stockpilot-ai.git
cd stockpilot-ai
```

### Create and activate a virtual environment

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Configure local environment

```bash
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

For a simple local run, leave `DATABASE_URL` empty. The application will use the SQLite fallback and create its local database file according to the configured path.

### Start the application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:3000
```

The application listens on the `PORT` environment variable when supplied and defaults to port `3000`.

### Verify health and route manifest

```bash
curl http://127.0.0.1:3000/healthz
curl http://127.0.0.1:3000/manus-routes.json
```

## Environment Configuration

The safe template is stored in `.env.example`. Important settings include:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask session signing key; use a long random value in production |
| `DATABASE_URL` | Managed MySQL-compatible database DSN; empty means local SQLite fallback |
| `SQLITE_PATH` | Local SQLite database path |
| `PORT` | HTTP listening port; defaults to 3000 |
| `FLASK_DEBUG` | Development debug mode; keep disabled in production |
| `APP_ENV` | Environment label such as development or production |

Never commit `.env`, database passwords, access tokens, or private credentials to GitHub.

## Database Design

Core entities include:

- `workspaces`
- `users`
- `categories`
- `suppliers`
- `products`
- `stock_batches`
- `sales`
- `sale_items`
- `purchase_orders`
- `purchase_order_items`
- `stock_movements`
- `notifications`
- `audit_logs`
- `inventory_policies`

### Transaction rules

Stock-affecting operations are handled in the service layer:

- Sale: validates stock, deducts batches, records sale items, movement, and audit history.
- Purchase receipt: increases stock, creates or updates batches, records receipt movement, and updates purchase status.
- Waste: selects eligible batches using FEFO, reduces quantities, and records reason and movement.
- Manual adjustment: changes quantity only with an explicit audit reason.

If an operation fails, the transaction is rolled back so partial updates are not left behind.

## Core Business Workflows

### Add a product

1. Open Inventory.
2. Select Add product.
3. Enter name, SKU, barcode, category, supplier, price, quantity, and reorder information.
4. Submit the form.
5. The backend validates duplicate identifiers and numeric values.
6. The application creates the product, opening stock batch, stock movement, and audit record.

### Record a sale

1. Open Sales & Billing.
2. Add one or more products to the sale.
3. Apply discount and tax if required.
4. Choose payment method and status.
5. Submit the sale.
6. The backend validates stock and deducts eligible FEFO batches.
7. The invoice-ready sale and audit information are stored.

### Receive a purchase order

1. Open Purchasing.
2. Select a sent or partially received purchase order.
3. Enter the quantity received for each line.
4. Confirm receipt.
5. Inventory quantities and batches are updated.
6. The purchase order status changes to partial or received.

### Process expiry or waste

1. Open Expiry & Waste.
2. Review expiring and expired batches.
3. Select a product and quantity.
4. Choose a reason such as expired, damaged, or wastage.
5. Confirm the action.
6. FEFO selects the earliest-expiring batch first.
7. The stock movement, waste record, and audit history are saved.

## Restocking Methodology

StockPilot uses an explainable baseline restocking engine.

### Average daily demand

```text
Average daily demand = Units sold during lookback period / Lookback days
```

### Lead-time demand

```text
Lead-time demand = Average daily demand × Supplier lead time in days
```

### Reorder point

```text
Reorder point = Lead-time demand + Safety stock
```

### Suggested quantity

```text
Target stock = reorder point plus a planning buffer
Suggested quantity = max(0, Target stock − Current stock)
```

The engine also reports data quality and confidence. Products with limited sales history are explicitly marked as fallback or low-data recommendations.

## Algorithms Demonstrated

| Algorithm | Application use | Complexity |
|---|---|---|
| Merge Sort | Sort products, sales, and recommendations in a stable way | O(n log n) time, O(n) space |
| Binary Search | Search sorted SKU collections | O(log n), sorted input required |
| Hash lookup | Fast SKU and barcode resolution at checkout | O(1) average lookup |
| Dijkstra | Find shortest warehouse route when route data exists | O((V + E) log V) |
| Priority Queue | Display critical restocking alerts first | O(n log n) build/pop |
| FEFO | Select earliest-expiring batches first | O(n log n) sorting |

Detailed explanations and pseudocode are available in [`docs/DAA.md`](docs/DAA.md).

## API Overview

The Flask API includes protected endpoints for:

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | Unauthenticated health check |
| `GET /manus-routes.json` | User-facing route manifest |
| `POST /api/login` | Authenticate a user |
| `POST /api/logout` | End the current session |
| `POST /api/register-admin` | Create a new admin workspace |
| `GET /api/bootstrap` | Load workspace-scoped dashboard data |
| `GET /api/products` | Search and filter products |
| `POST /api/products` | Create a product |
| `PUT /api/products/<id>` | Update a product |
| `POST /api/sales` | Process a sale |
| `GET /api/sales` | Read sales records |
| `POST /api/purchases/<id>/receive` | Receive purchase order items |
| `POST /api/record-waste` | Record expiry, damage, or waste |
| `GET /api/reports/<type>.csv` | Export a report as CSV |
| `POST /api/assistant` | Ask a supported business question |
| `POST /api/notifications/<id>/read` | Mark an alert as read |

All protected reads and writes use the authenticated workspace scope.

## Reports and Exports

Available report families include:

- Inventory valuation
- Low-stock products
- Expiry and waste
- Sales and gross profit
- Purchases
- Suppliers
- Fast and slow movers
- Forecast summary
- Stock audit

Reports can be reviewed in the application, exported as CSV, or printed from the browser.

## Testing

Run compilation checks:

```bash
python -m py_compile app.py services.py db.py analytics.py algorithms.py
```

Run the automated test suite:

```bash
python -m pytest -q
```

The test suite covers:

- Merge Sort ordering
- Binary Search sorted-input behavior
- Graph validation and Dijkstra routing
- Priority queue alert ordering
- FEFO batch selection
- Decimal-safe totals
- Restocking calculations
- Insufficient-stock rejection
- Safe assistant behavior
- Workspace isolation checks where configured

## Docker Deployment

Build the production image:

```bash
docker build -t stockpilot-ai .
```

Run the container locally:

```bash
docker run --rm \
  -p 3000:3000 \
  -e SECRET_KEY="replace-with-a-long-random-secret" \
  -e DATABASE_URL="your-managed-database-url" \
  stockpilot-ai
```

The container honors `PORT` and provides `/healthz` as the health endpoint. Runtime database credentials should be injected through the deployment environment rather than committed into the image or source code.

## Oracle and PL/SQL Artifacts

The project includes Oracle-oriented academic artifacts:

- [`oracle/schema.sql`](oracle/schema.sql) — normalized Oracle schema, constraints, indexes, and sequences
- [`oracle/inventory_pkg.sql`](oracle/inventory_pkg.sql) — package specification and body for core inventory operations
- [`oracle/seed_data.sql`](oracle/seed_data.sql) — fictional demo data and setup guidance
- [`docs/ORACLE_SETUP.md`](docs/ORACLE_SETUP.md) — Oracle configuration and deployment notes

The Python application uses an adapter-based approach. The local and managed MySQL-compatible adapters support the working application; Oracle remains documented as the production database target for the academic project.

## Security

Security features include:

- Password hashing
- Secure session management
- Protected authentication routes
- Backend role enforcement
- CSRF protection for state-changing operations
- Workspace-level data isolation
- Duplicate SKU and barcode validation
- Parameterized database operations
- Safe assistant intents without arbitrary SQL execution
- Environment-driven secrets
- Production health endpoint without authentication

For production use, replace all demo credentials, configure a strong random `SECRET_KEY`, enable TLS, use a managed database, and apply least-privilege database credentials.

## Academic Relevance

This project demonstrates practical Python programming concepts:

- Modules and reusable functions
- Object-oriented and service-layer organization
- Exception handling and transaction rollback
- Decimal arithmetic for financial data
- Lists, dictionaries, sets, queues, and priority queues
- Sorting, searching, hashing, and graph traversal
- Database connectivity and SQL operations
- HTTP routing and JSON APIs
- Form validation and secure authentication
- CSV export and report generation
- Unit testing and deployment packaging

## Limitations and Future Scope

Current limitations and possible improvements include:

- Forecasting is a baseline method and should be evaluated against more advanced time-series models with larger datasets.
- Supplier price comparison can be expanded with historical vendor quotations.
- Barcode scanning and mobile receiving can improve warehouse speed.
- Scheduled notifications can be connected to email or messaging providers.
- Oracle integration testing can be added to the continuous integration pipeline.
- Advanced demand forecasting can use richer seasonal, promotion, and holiday features.
- Multi-location inventory can be added with a location dimension and inter-store transfers.

## License

This repository is an academic project created for educational and demonstration purposes. Add a formal open-source license before redistributing the project for production or commercial use.

## Author

**Swarup Chowdhury**  
MCA (AI/ML)  
Chandigarh University  
Section 26MAM4(B)  
Roll Number 26MCI10229
