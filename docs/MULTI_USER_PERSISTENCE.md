# Multi-user persistence and workspace isolation

StockPilot uses one durable managed MySQL database with account-scoped workspace rows. This is safer and easier to operate than creating a separate physical database for every signup while providing the same user-facing result: each admin sees and edits only the records belonging to their workspace.

The `workspaces` table identifies each private workspace. Every operational table carries `workspace_id`, and the Flask session stores the authenticated workspace ID. Service-layer reads, writes, reports, notifications, inventory movements, and assistant answers require that scope. The backend never trusts a workspace ID supplied by the browser.

The built-in `owner@stockpilot.ai` demo login belongs to the `demo` workspace and is the only workspace seeded with fictional records. The visible demo ribbon appears only for that account. A new admin registration creates a new workspace and owner user with no products, sales, suppliers, purchase orders, notifications, or demo records. The empty dashboard explains the training path and guides the user to add their first product.

Migration is idempotent. On first startup after this release, the application creates `workspaces`, adds missing `workspace_id` columns to existing tables, creates the demo workspace, and backfills existing records into that demo workspace. New records are written with the active workspace ID inside the same transaction as their business operation.

## User flow

1. Select **Create new admin** on the login screen.
2. Enter a name, workspace name, unique email/user ID, and password of at least eight characters.
3. StockPilot creates the account and private workspace, signs the user in, and shows the empty training dashboard.
4. Add the first product. If the workspace has no category or supplier yet, the first product action creates minimal workspace-local placeholders; no demo records are copied.
5. Log out and sign in again to confirm that the same workspace data persists.

The demo credentials remain `owner@stockpilot.ai` / `demo123` for evaluation only.
