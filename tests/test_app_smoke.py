import importlib


def test_fresh_seed_and_private_workspace_flow(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    import db as db_module

    db_module._SCHEMA_READY = False
    db_module._TENANCY_READY = False
    database_path = tmp_path / "stockpilot.sqlite"
    conn = db_module.init_db(str(database_path))
    assert conn.execute("SELECT COUNT(*) FROM products WHERE workspace_id IS NOT NULL").fetchone()[0] > 0
    assert conn.execute("SELECT COUNT(*) FROM users WHERE workspace_id IS NOT NULL").fetchone()[0] == 3

    app_module = importlib.import_module("app")
    app_module.app.config.update(TESTING=True, DATABASE_PATH=str(database_path), SESSION_COOKIE_SECURE=False)
    client = app_module.app.test_client()

    response = client.post(
        "/api/register-admin",
        json={
            "name": "Private Owner",
            "email": "private-owner@example.com",
            "password": "secure123",
            "workspace_name": "Private Workspace",
        },
    )
    assert response.status_code == 201
    bootstrap = client.get("/api/bootstrap").get_json()
    assert bootstrap["workspace"]["name"] == "Private Workspace"
    assert bootstrap["user"]["is_demo"] is False
    assert bootstrap["products"] == []
    assert bootstrap["sales"] == []

    csrf = bootstrap["csrf_token"]
    headers = {"X-CSRF-Token": csrf}
    response = client.post(
        "/api/products",
        json={
            "name": "Private Rice",
            "sku": "PRIVATE-001",
            "barcode": "PRIVATE-001",
            "purchase_cost": "100",
            "selling_price": "140",
            "current_qty": "10",
            "minimum_stock": "2",
            "reorder_level": "4",
        },
        headers=headers,
    )
    assert response.status_code == 201
    product_id = response.get_json()["id"]

    response = client.post(
        "/api/sales",
        json={"items": [{"product_id": product_id, "quantity": 2}], "discount": 0, "payment_method": "cash"},
        headers=headers,
    )
    assert response.status_code == 201
    bootstrap = client.get("/api/bootstrap").get_json()
    assert len(bootstrap["sales"]) == 1
    assert bootstrap["products"][0]["current_qty"] == 8

    assert client.post("/api/notifications/999999/read", headers=headers).status_code == 404
