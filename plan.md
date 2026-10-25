# StockPilot AI — Implementation Plan

## Product approach

StockPilot AI is a responsive inventory operations cockpit for small retail businesses. The first release is a real Flask application with a clearly separated SQLite development adapter for the live preview, an Oracle schema and PL/SQL package under `oracle/` for the production database path, auditable stock movements, and browser interactions backed by JSON endpoints. Demo data is deterministic, fictional, and visibly labelled so the dashboard is useful immediately without confusing it with production records.

The backend owns authentication, permissions, validation, Decimal-safe totals, inventory mutations, notifications, recommendation calculations, assistant intents, exports, and algorithm demonstrations. The frontend is a server-served HTML shell with reusable CSS and vanilla JavaScript views. A later Oracle deployment can replace the development repository adapter while retaining service contracts and business rules.

## Project structure

```text
stockpilot/
├── app.py                    # Flask app, routes, API, session and error handling
├── config.py                 # environment-driven settings
├── db.py                     # SQLite development adapter, schema and seed data
├── services.py               # dashboard, inventory, sales, purchasing, assistant services
├── algorithms.py             # Merge Sort, Binary Search, hash lookup, Dijkstra, heap, FEFO
├── analytics.py              # demand trends, moving averages, restock calculations, reports
├── requirements.txt          # Flask, pandas, numpy, python-oracledb and test dependencies
├── .env.example              # non-secret configuration contract
├── .gitignore
├── templates/index.html      # application shell and login view
├── static/app.js             # client routing, forms, tables, charts and toasts
├── static/styles.css         # responsive design system; no watermark or platform branding
├── public/manus-routes.json  # route manifest for Preview
├── oracle/schema.sql         # normalized Oracle tables, constraints, indexes and sequences
├── oracle/inventory_pkg.sql  # INVENTORY_PKG specification and body
├── oracle/seed_data.sql      # Oracle demo seed guidance
├── docs/ORACLE_SETUP.md      # Oracle deployment and transaction ownership guide
├── docs/ARCHITECTURE.md     # MCA-friendly architecture, entities and data lineage
├── docs/DAA.md              # algorithm explanations and complexities
└── tests/test_core.py       # algorithm, finance, permissions and stock safety tests
```

## Data model and relationships

The development schema models `users` and `roles`, `categories`, `products`, `suppliers`, `product_suppliers`, `stock_batches`, `stock_movements`, `sales`, `sale_items`, `purchase_orders`, `purchase_order_items`, `notifications`, `audit_logs`, and `inventory_policies`. Products belong to categories and can map to many suppliers. Batches belong to products and carry expiry dates and quantities; every quantity change creates a movement. Sales have line items and deduct batches using FEFO. Purchase orders have line items and receipt actions create inbound movements. Notifications and audit logs reference the affected product or business action where useful.

Current stock is maintained transactionally on `products.current_qty` for fast dashboard reads and checked against the stock movement ledger during reconciliation. The ledger remains the audit source. Oracle adds foreign keys, check constraints, unique SKU/barcode indexes, quantity indexes, and a narrowly scoped movement audit trigger.

## Business intelligence

The restocking engine uses a transparent baseline: average daily demand over the selected lookback, lead-time demand, configurable safety stock, reorder point, and target-stock gap. A data-quality label distinguishes strong history from fallback estimates. Forecasting uses moving-average baselines and explicitly says when history is insufficient; it does not present simple rules as advanced AI. The assistant maps supported phrases to parameterized service queries only.

## Design direction

Three possible directions were considered: **Midnight Operations** (0.07: dark control-room shell with luminous indigo and teal signals), **Paper Ledger Modern** (0.06: warm documentation tones and tactile ledger surfaces), and **Signal Garden** (0.05: lighter botanical data dashboard with organic status cues). The chosen direction is **Midnight Operations**.

- **Design movement:** premium operational SaaS influenced by Linear, Ramp, and modern logistics control rooms.
- **Core principles:** information density without clutter; visible confidence and provenance; calm hierarchy with urgent signals reserved for risk; fast scan-to-action flows.
- **Color philosophy:** deep navy anchors trust and focus; cool slate creates a clean workspace; violet owns the brand; teal communicates intelligence; semantic green/amber/red are reserved for health, warning, and risk.
- **Layout paradigm:** a persistent command rail on the left and a wide editorial workspace that alternates metric bands, analytical lanes, and action tables rather than a uniform tile grid.
- **Signature elements:** violet-to-teal signal bars, compact status pills, and a translucent “demo mode” indicator that is part of the product chrome rather than a watermark.
- **Interaction philosophy:** every action shows its consequence, with optimistic updates only after the server confirms; filtering and tab changes are immediate; destructive actions require confirmation.
- **Animation:** 160–220ms ease-out for hover, drawers, tab transitions, and toast entry; subtle chart line draw and pulse only for live alert counts; respect reduced-motion preferences.
- **Typography:** Inter/system sans for operational UI, with a slightly heavier display weight for titles; numeric values use tabular numerals for easy comparison.
- **Brand essence:** “Clarity before the next purchase” for owners and operators; precise, calm, actionable.
- **Brand voice:** direct, useful, and evidence-led. Example lines: “Protect tomorrow’s shelf availability.” and “Every recommendation shows its math.”
- **Wordmark & logo:** the `S` mark is drawn as two offset warehouse-shelf brackets with a diagonal pilot line; the wordmark uses compact uppercase with a violet signal dot.
- **Signature brand color:** Pilot Violet `#7c5cff`.

## Build workflow

1. Establish the Flask shell, local data adapter, login, route manifest, and design system.
2. Add deterministic seed data and operational APIs for inventory, sales, purchase orders, alerts, reports, and assistant.
3. Add the dashboard and module views with working forms, filters, charts, exports, and print mode.
4. Add the DAA laboratory and documented Oracle schema/package artifacts.
5. Run unit tests, Python compilation, route manifest checks, and a read-only requirements review before checkpointing.
