# Oracle setup

The production database target is Oracle Database with `python-oracledb`. The preview uses SQLite only as a visibly separated development adapter; it is not presented as Oracle.

1. Create an Oracle schema/user with the least privileges needed for the tables, sequences, package, and indexes.
2. Run `@oracle/schema.sql` as the application owner.
3. Run `@oracle/inventory_pkg.sql` to compile `INVENTORY_PKG`.
4. Run `@oracle/seed_data.sql` only in a demo schema.
5. Configure `ORACLE_DSN`, `ORACLE_USER`, and `ORACLE_PASSWORD` through environment variables or a secret manager.
6. Exercise the receipt and sale paths against Oracle integration tests after installing `python-oracledb` in thick or thin mode as appropriate.

The service layer owns the transaction boundary: one business operation commits after all product, batch, movement, and audit rows succeed, and rolls back on any exception. The package deliberately does not commit internally so the calling application can compose operations. Foreign keys, unique indexes, and check constraints enforce structural integrity. The movement trigger is narrowly scoped to create an audit row for direct movement inserts; normal business operations write the richer audit record themselves.

For deployment behind Preview HTTPS, session cookies use `SameSite=None; Secure`. Use a long random `SECRET_KEY` in production and disable demo seed mode. Never commit database passwords, API keys, or real customer data.
