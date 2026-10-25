# StockPilot AI — Delivery Checklist

## Foundation and access

- [ ] Flask application starts on the configured port and serves a responsive shell plus `/manus-routes.json`.
- [ ] Login and logout work with hashed passwords, secure session settings, protected API routes, and backend-enforced Admin/Manager/Staff roles.
- [ ] Demo mode is clearly labelled, uses fictional seeded records, and contains no watermark or platform branding in product UI or exports.

## Inventory operations

- [ ] Users can search, filter, view, add, edit, and deactivate products with SKU/barcode validation, categories, suppliers, prices, quantities, reorder thresholds, and expiry data.
- [ ] Every purchase, sale, return, waste, expiry, or manual adjustment is transactional and creates an auditable stock movement; insufficient stock is rejected safely.
- [ ] Stock batches support expiry warnings, expired alerts, waste recording, and FEFO deduction for perishable inventory.

## Sales and purchasing

- [ ] Sales support multiple products, Decimal-safe subtotal/discount/tax/final totals, stock validation, payment status/method, printable invoice, and return-ready records.
- [ ] Suppliers and purchase orders support statuses, line items, partial receipt actions, history, and inventory updates.

## Intelligence and analytics

- [ ] Dashboard metrics come from stored records and include valuation, low stock, expiry, sales, gross profit, purchase orders, movers, trends, category mix, and critical alerts.
- [ ] Restock recommendations show current stock, demand, lead-time demand, safety stock, reorder point, suggested quantity, cost, supplier, reason, and data-quality confidence.
- [ ] Analytics show daily/monthly demand, category performance, fast/slow movers, baseline 7/30-day forecasting, limitations, and relevant reports.
- [ ] Business assistant answers supported inventory questions using allowlisted service intents and never executes arbitrary SQL or code.

## Algorithms and Oracle

- [ ] Algorithm Insights visibly demonstrates custom Merge Sort, Binary Search with sorted precondition, hash SKU lookup, Dijkstra with nonnegative edges, priority queue alert ranking, and FEFO; each includes use case, steps, complexity, example, and test evidence.
- [ ] Oracle artifacts include normalized schema, constraints/indexes, sequences, seed guidance, `INVENTORY_PKG` spec/body, transaction ownership notes, and setup documentation.

## Reporting and quality

- [ ] Reports cover valuation, low stock, expiry/waste, sales/profit, purchases, suppliers, movers, forecasts, and stock audit; active filters are respected for CSV and printable output.
- [ ] Notifications are condition-based and can be marked read.
- [ ] `.env.example`, dependency manifest, docs, tests, logging, safe errors, and input validation are included.
- [ ] Python compilation, unit tests, route manifest validation, and a read-only requirements review pass before checkpoint.
