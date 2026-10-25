# StockPilot AI — User Training Guide

## 1. Start the application

Open the StockPilot Preview and sign in with the demo owner account:

- Email: `owner@stockpilot.ai`
- Password: `demo123`

The demo workspace is named **Northstar Pantry**. The data is fictional, but the dashboard values are generated from database records.

StockPilot has three roles:

| Role | Typical access |
|---|---|
| Admin / Owner | Full dashboard, products, sales, purchasing, reports, and settings |
| Inventory Manager | Inventory, purchasing, restocking, expiry, analytics, and reports |
| Staff member | Sales and day-to-day stock visibility |

## 2. Understand the layout

The dark sidebar is the main navigation. **Overview** is the executive dashboard. **Inventory** manages products and stock health. **Sales & billing** is the checkout workflow. **Purchasing** tracks supplier orders and receipts. **Restocking AI** explains what to reorder. **Analytics** shows demand trends. **Expiry & waste** manages perishable risk. **Algorithm lab** demonstrates the MCA algorithms. **Reports** provides CSV exports. **Business assistant** answers supported business questions. **Settings** shows workspace and security information.

The top bar contains global search, notifications, and the current user. The purple demo ribbon means the records are fictional evaluation data, not a watermark.

## 3. Daily owner workflow

A useful daily routine is:

1. Open **Overview**.
2. Check inventory value, today's sales, low-stock count, and expiry windows.
3. Review **Critical inventory signals**.
4. Open **Restocking AI** and inspect the calculation columns.
5. Review **Expiry & waste** for batches expiring within 30 days.
6. Open **Purchasing** and receive any delivered purchase orders.
7. Use **Reports** to download a low-stock or audit CSV.
8. Ask the **Business assistant** about anything that needs clarification.

## 4. Practice exercise: inspect inventory

Open **Inventory** and search for `Rice` or `SP-0001`.

Read these fields:

- **Stock health:** compares current stock with the reorder level.
- **Purchase cost:** the cost used for inventory valuation.
- **Retail:** the selling price used in sales and profit calculations.
- **Supplier:** the preferred supplier attached to the product.

Open the product detail menu to review its SKU, barcode, current stock, reorder point, purchase cost, and retail price.

To add a product, select **Add product**, complete the required fields, and submit. The server validates prices, quantities, duplicate SKUs, and required fields. Opening stock creates a stock batch and an opening movement.

## 5. Practice exercise: complete a sale

1. Open **Sales & billing**.
2. Select **New sale**.
3. Choose a product with available stock.
4. Enter a quantity.
5. Optionally add a discount.
6. Select card, UPI, or cash.
7. Select **Complete sale**.

The application calculates subtotal, tax, discount, and total using Decimal-safe monetary calculations. It checks stock before committing. When the sale succeeds, the product quantity decreases and a sale movement is added to the audit ledger.

If you request more units than available, the operation is rejected and no partial sale is committed.

## 6. Practice exercise: receive a purchase order

1. Open **Purchasing**.
2. Review supplier reliability, lead time, and order status.
3. Find an order with `pending` or `partial` status.
4. Select **Receive**.

Receiving updates product stock, creates or updates a batch, records a receipt movement, updates the purchase order, and commits the operation together. This is the same transaction boundary documented for the Oracle package.

## 7. Understand Restocking AI

Open **Restocking AI**. Each recommendation explains:

- **Current stock:** available product quantity.
- **Average daily demand:** completed units sold divided by the lookback period.
- **Lead-time demand:** average daily demand multiplied by supplier lead time.
- **Safety stock:** a conservative buffer based on recent demand.
- **Reorder point:** lead-time demand plus safety stock.
- **Suggested quantity:** the gap between target stock and available stock.
- **Estimated cost:** suggested quantity multiplied by purchase cost.
- **Confidence:** High, Medium, or Fallback depending on history quality.

Use the confidence label to decide how much human review is needed. This feature is intentionally explainable business logic; it does not claim to be a sophisticated ML model.

## 8. Practice exercise: expiry and waste

Open **Expiry & waste**. Review batches expiring within 30 days. The system uses FEFO: First Expired, First Out.

To record waste:

1. Select **Record waste**.
2. Choose a product.
3. Enter the quantity.
4. Enter a reason such as damaged goods or expired stock.
5. Submit the form.

Stock is deducted from the earliest-expiring batches first. The movement is recorded as waste and an audit entry is created. Expired stock is not treated as sellable merely because its quantity is positive.

## 9. Use Analytics and Reports

Open **Analytics** to review the 14-day sales trend, demand leaders, forecast method, and data limitations. The forecast is a moving-average baseline. It should be used for planning, not presented as a guaranteed prediction.

Open **Reports** to preview or download:

- Inventory valuation
- Low-stock products
- Expiry batches
- Sales history
- Stock movement audit

Use CSV files for spreadsheet analysis or sharing. Use the browser print dialog for printable report previews.

## 10. Use the Business Assistant

Open **Business assistant** and ask one of these supported questions:

- Which products need restocking?
- Which products are selling fastest?
- What is my current inventory valuation?
- Which products may expire this month?
- Which suppliers have the best delivery performance?

The assistant uses bounded, predefined queries. It does not execute arbitrary SQL or code. If a question is outside the supported intents, it explains what it can answer.

## 11. Study the Algorithm Lab

Open **Algorithm lab** and review the business use case, steps, complexity, example, and test for each algorithm:

- Merge Sort: predictable product and sales ordering.
- Binary Search: fast lookup in sorted SKU data.
- Hash lookup: average O(1) SKU resolution.
- Dijkstra: shortest route distance with nonnegative edges.
- Priority queue: ranking critical restocking alerts.
- FEFO: selecting the batch that expires first.

For an MCA viva, explain not only the complexity but also the business reason the algorithm exists.

## 12. Recommended learning sequence

For your first session, complete: login, Overview, Inventory search, one sale, one purchase receipt, one restock review, one expiry review, one CSV export, and one assistant question.

For your second session, study the Algorithm Lab and read `docs/DAA.md`.

For your project demonstration, show one complete flow: a low-stock product appears on the dashboard, the restocking engine explains the recommendation, a purchase order is received, stock increases, and the audit ledger records the receipt.

For your Oracle presentation, read `docs/ORACLE_SETUP.md`, `oracle/schema.sql`, and `oracle/inventory_pkg.sql`. Explain that SQLite is only the development adapter in this Preview and Oracle is the production target.

## 13. Important safety rules

Do not use the demo password in production. Set a long random `SECRET_KEY`, configure Oracle credentials through environment variables or a secret manager, disable demo seeding, and verify role permissions before onboarding real staff. Always review stock and expiry recommendations before placing a real purchase order.
