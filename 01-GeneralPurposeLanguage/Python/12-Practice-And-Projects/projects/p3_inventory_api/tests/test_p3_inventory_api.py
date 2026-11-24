import importlib

import pytest
from fastapi.testclient import TestClient

KEY = {"X-API-Key": "test-key"}


def mod(name):
    return importlib.import_module(f"inventory_api.{name}")


@pytest.fixture
def app():
    return mod("app").create_app(":memory:", api_key="test-key")


@pytest.fixture
def client(app):
    with TestClient(app, headers=KEY) as c:
        yield c


@pytest.fixture
def anon(app):
    with TestClient(app) as c:
        yield c


def make(client, **over):
    body = {"name": "Widget", "sku": "W-1", "price": 9.5, "stock": 10, "category": "tools"} | over
    r = client.post("/products", json=body)
    assert r.status_code == 201, r.text
    return r.json()


# ---- auth + meta
def test_health_needs_no_key(anon):
    assert anon.get("/health").json() == {"status": "ok"}


def test_missing_key_is_401(anon):
    assert anon.get("/products").status_code == 401


def test_wrong_key_is_401(anon):
    assert anon.get("/products", headers={"X-API-Key": "nope"}).status_code == 401


def test_openapi_lists_routes(anon):
    paths = anon.get("/openapi.json").json()["paths"]
    assert "/products" in paths and "/products/{product_id}/stock" in paths
    assert "post" in paths["/products"]


# ---- create / read
def test_create_returns_201_and_id(client):
    p = make(client)
    assert p == {"id": 1, "name": "Widget", "sku": "W-1", "price": 9.5, "stock": 10, "category": "tools"}


def test_stock_defaults_to_zero(client):
    r = client.post("/products", json={"name": "A", "sku": "A", "price": 1})
    assert r.json()["stock"] == 0 and r.json()["category"] is None


def test_get_product(client):
    p = make(client)
    assert client.get(f"/products/{p['id']}").json() == p


def test_get_unknown_is_404(client):
    assert client.get("/products/999").status_code == 404


def test_duplicate_sku_is_409(client):
    make(client)
    r = client.post("/products", json={"name": "Other", "sku": "W-1", "price": 1})
    assert r.status_code == 409


@pytest.mark.parametrize("bad", [
    {"price": -1},
    {"name": ""},
    {"sku": "has space"},
    {"stock": -5},
    {"price": "cheap"},
])
def test_invalid_create_is_422(client, bad):
    body = {"name": "Widget", "sku": "W-1", "price": 1} | bad
    assert client.post("/products", json=body).status_code == 422


def test_missing_field_is_422(client):
    assert client.post("/products", json={"name": "x"}).status_code == 422


# ---- update / delete
def test_patch_changes_only_given_fields(client):
    p = make(client)
    r = client.patch(f"/products/{p['id']}", json={"price": 12})
    assert r.status_code == 200
    assert r.json() == p | {"price": 12}


def test_patch_empty_body_changes_nothing(client):
    p = make(client)
    assert client.patch(f"/products/{p['id']}", json={}).json() == p


def test_patch_unknown_is_404(client):
    assert client.patch("/products/5", json={"price": 1}).status_code == 404


def test_patch_to_taken_sku_is_409(client):
    make(client)
    b = make(client, sku="B-2")
    assert client.patch(f"/products/{b['id']}", json={"sku": "W-1"}).status_code == 409


def test_patch_cannot_set_stock(client):
    p = make(client)
    assert client.patch(f"/products/{p['id']}", json={"stock": 99}).status_code == 422


def test_delete(client):
    p = make(client)
    assert client.delete(f"/products/{p['id']}").status_code == 204
    assert client.get(f"/products/{p['id']}").status_code == 404


def test_delete_unknown_is_404(client):
    assert client.delete("/products/1").status_code == 404


# ---- stock
def test_stock_add_and_remove(client):
    p = make(client, stock=5)
    assert client.post(f"/products/{p['id']}/stock", json={"delta": 3}).json()["stock"] == 8
    assert client.post(f"/products/{p['id']}/stock", json={"delta": -8}).json()["stock"] == 0


def test_stock_never_negative(client):
    p = make(client, stock=2)
    r = client.post(f"/products/{p['id']}/stock", json={"delta": -3})
    assert r.status_code == 409
    assert client.get(f"/products/{p['id']}").json()["stock"] == 2


def test_stock_zero_delta_is_422(client):
    p = make(client)
    assert client.post(f"/products/{p['id']}/stock", json={"delta": 0}).status_code == 422


def test_stock_unknown_product_is_404(client):
    assert client.post("/products/7/stock", json={"delta": 1}).status_code == 404


# ---- search / filter / pagination
@pytest.fixture
def stocked(client):
    for i, (name, cat, price) in enumerate([
        ("Hammer", "tools", 10), ("Screwdriver", "tools", 6), ("Apple", "food", 1),
        ("Pear", "food", 2), ("Hammock", "garden", 40),
    ]):
        make(client, name=name, sku=f"S-{i}", category=cat, price=price)
    return client


def test_list_all(stocked):
    body = stocked.get("/products").json()
    assert body["total"] == 5 and len(body["items"]) == 5
    assert [p["id"] for p in body["items"]] == [1, 2, 3, 4, 5]


def test_search_q_is_case_insensitive(stocked):
    names = [p["name"] for p in stocked.get("/products", params={"q": "HAM"}).json()["items"]]
    assert names == ["Hammer", "Hammock"]


def test_filter_category(stocked):
    body = stocked.get("/products", params={"category": "food"}).json()
    assert body["total"] == 2


def test_filter_price_range(stocked):
    body = stocked.get("/products", params={"min_price": 2, "max_price": 10}).json()
    assert sorted(p["name"] for p in body["items"]) == ["Hammer", "Pear", "Screwdriver"]


def test_filters_combine(stocked):
    body = stocked.get("/products", params={"category": "tools", "q": "screw"}).json()
    assert [p["name"] for p in body["items"]] == ["Screwdriver"]


def test_pagination(stocked):
    body = stocked.get("/products", params={"limit": 2, "offset": 2}).json()
    assert body["total"] == 5 and body["limit"] == 2 and body["offset"] == 2
    assert [p["id"] for p in body["items"]] == [3, 4]


def test_offset_past_end_is_empty(stocked):
    body = stocked.get("/products", params={"offset": 50}).json()
    assert body["items"] == [] and body["total"] == 5


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"min_price": -1}])
def test_bad_query_params_are_422(client, params):
    assert client.get("/products", params=params).status_code == 422


# ---- factory + dependency injection + repository
def test_each_app_has_its_own_database():
    create_app = mod("app").create_app
    a, b = create_app(), create_app()
    with TestClient(a, headers={"X-API-Key": "dev-key"}) as ca, TestClient(b, headers={"X-API-Key": "dev-key"}) as cb:
        make(ca)
        assert cb.get("/products").json()["total"] == 0


def test_dependency_override_repo_on_disk(app, tmp_path):
    m = mod("app")
    repo = mod("repository").ProductRepository(str(tmp_path / "inv.db"))
    app.dependency_overrides[m.get_repo] = lambda: repo
    with TestClient(app, headers=KEY) as c:
        make(c)
    assert repo.get(1)["sku"] == "W-1"
    repo.close()
    reopened = mod("repository").ProductRepository(str(tmp_path / "inv.db"))
    assert reopened.list()[1] == 1
    reopened.close()


def test_dependency_override_auth(app):
    m = mod("app")
    app.dependency_overrides[m.require_api_key] = lambda: None
    with TestClient(app) as c:
        assert c.get("/products").status_code == 200


def test_repository_errors():
    r = mod("repository")
    repo = r.ProductRepository()
    p = repo.create(name="A", sku="A", price=1, stock=1)
    with pytest.raises(r.InsufficientStock):
        repo.adjust_stock(p["id"], -2)
    with pytest.raises(r.NotFound):
        repo.adjust_stock(99, 1)
    with pytest.raises(r.Conflict):
        repo.create(name="B", sku="A", price=1)
    assert issubclass(r.InsufficientStock, r.Conflict)


@pytest.mark.parametrize("change", [{"stock": 2**63}, {"price": "inf"}, {"price": "nan"}])
def test_create_rejects_out_of_range_numbers(client, change):
    body = {"name": "X", "sku": "X", "price": 1, **change}
    assert client.post("/products", json=body).status_code == 422
    assert client.get("/products").json()["total"] == 0


def test_stock_addition_cannot_overflow(client):
    product = make(client, stock=2**63 - 1)
    assert client.post(f"/products/{product['id']}/stock", json={"delta": 1}).status_code == 409
    assert client.get(f"/products/{product['id']}").json()["stock"] == 2**63 - 1
    assert client.post(f"/products/{product['id']}/stock", json={"delta": -(2**63)}).status_code == 409


def test_identifiers_delta_and_price_filters_are_bounded(client):
    product = make(client)
    assert client.get(f"/products/{2**63}").status_code == 422
    assert client.post(f"/products/{product['id']}/stock", json={"delta": 2**63}).status_code == 422
    assert client.patch(f"/products/{product['id']}", json={"price": "inf"}).status_code == 422
    assert client.get("/products", params={"min_price": "inf"}).status_code == 422
