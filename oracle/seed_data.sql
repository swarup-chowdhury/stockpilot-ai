-- Run only in a fictional demo schema after schema.sql and inventory_pkg.sql.
INSERT INTO roles(role_name) VALUES('admin'); INSERT INTO roles(role_name) VALUES('manager'); INSERT INTO roles(role_name) VALUES('staff');
INSERT INTO inventory_policies(policy_key,policy_value) VALUES('safety_stock_days','2');
INSERT INTO inventory_policies(policy_key,policy_value) VALUES('target_days','14');
COMMIT;
-- Product, supplier, sale and batch fixtures should be loaded through the seed-data service
-- or an approved import script so password hashes and business dates are generated safely.
