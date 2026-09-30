from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

BASE = "/products"


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Each test gets a fresh in-memory SQLite database."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def payload(**overrides):
    data = {
        "product_id": 1,
        "product_name": "Laptop",
        "category": "Electronics",
        "price": 55000,
        "quantity": 10,
    }
    return {**data, **overrides}


# ---------- POST ----------
def test_create_product(client: TestClient):
    r = client.post(BASE, json=payload())
    assert r.status_code == 201
    assert r.json() == payload(price=55000.0)


def test_create_strips_whitespace(client: TestClient):
    r = client.post(BASE, json=payload(product_name="  Laptop  ", category=" Electronics "))
    assert r.json()["product_name"] == "Laptop"
    assert r.json()["category"] == "Electronics"


def test_duplicate_product_id(client: TestClient):
    client.post(BASE, json=payload())
    r = client.post(BASE, json=payload(product_name="Other"))
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "duplicate_product_id"


@pytest.mark.parametrize(
    "field,value",
    [("price", 0), ("price", -5), ("quantity", 0), ("quantity", -1), ("product_id", 0),
     ("product_name", ""), ("category", "   ")],
)
def test_invalid_values_rejected(client: TestClient, field: str, value: object):
    r = client.post(BASE, json=payload(**{field: value}))
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
    assert r.json()["error"]["details"][0]["field"] == field


def test_missing_field(client: TestClient):
    body = payload()
    del body["category"]
    r = client.post(BASE, json=body)
    assert r.status_code == 422
    assert r.json()["error"]["details"][0]["field"] == "category"


def test_wrong_type(client: TestClient):
    assert client.post(BASE, json=payload(quantity="ten")).status_code == 422


# ---------- GET ----------
def test_list_products(client: TestClient):
    client.post(BASE, json=payload())
    client.post(BASE, json=payload(product_id=2, product_name="Chair", category="Furniture"))
    r = client.get(BASE)
    assert r.status_code == 200
    assert [p["product_id"] for p in r.json()] == [1, 2]


def test_list_empty(client: TestClient):
    assert client.get(BASE).json() == []


def test_filter_by_category(client: TestClient):
    client.post(BASE, json=payload())
    client.post(BASE, json=payload(product_id=2, product_name="Chair", category="Furniture"))
    r = client.get(BASE, params={"category": "electronics"})  # case-insensitive
    assert [p["product_id"] for p in r.json()] == [1]


def test_filter_unknown_category(client: TestClient):
    client.post(BASE, json=payload())
    assert client.get(BASE, params={"category": "Toys"}).json() == []


def test_pagination(client: TestClient):
    for i in range(1, 6):
        client.post(BASE, json=payload(product_id=i))
    r = client.get(BASE, params={"skip": 1, "limit": 2})
    assert [p["product_id"] for p in r.json()] == [2, 3]


def test_get_product(client: TestClient):
    client.post(BASE, json=payload())
    r = client.get(f"{BASE}/1")
    assert r.status_code == 200
    assert r.json()["category"] == "Electronics"


def test_get_product_not_found(client: TestClient):
    r = client.get(f"{BASE}/99")
    assert r.status_code == 404
    assert r.json()["error"]["message"] == "Product with ID 99 not found."


def test_invalid_id_in_path(client: TestClient):
    assert client.get(f"{BASE}/abc").status_code == 422
    assert client.get(f"{BASE}/0").status_code == 422


# ---------- PUT ----------
def test_update_product(client: TestClient):
    client.post(BASE, json=payload())
    body = {"product_name": "Gaming Laptop", "category": "Electronics", "price": 80000, "quantity": 5}
    r = client.put(f"{BASE}/1", json=body)
    assert r.status_code == 200
    assert r.json()["product_id"] == 1
    assert client.get(f"{BASE}/1").json()["product_name"] == "Gaming Laptop"


def test_update_not_found(client: TestClient):
    body = {"product_name": "X", "category": "Y", "price": 1, "quantity": 1}
    assert client.put(f"{BASE}/99", json=body).status_code == 404


def test_update_invalid_price(client: TestClient):
    client.post(BASE, json=payload())
    body = {"product_name": "X", "category": "Y", "price": 0, "quantity": 1}
    assert client.put(f"{BASE}/1", json=body).status_code == 422


def test_update_requires_all_fields(client: TestClient):
    client.post(BASE, json=payload())
    assert client.put(f"{BASE}/1", json={"price": 10}).status_code == 422


# ---------- DELETE ----------
def test_delete_product(client: TestClient):
    client.post(BASE, json=payload())
    assert client.delete(f"{BASE}/1").status_code == 200
    assert client.get(f"{BASE}/1").status_code == 404


def test_delete_not_found(client: TestClient):
    assert client.delete(f"{BASE}/99").status_code == 404


# ---------- misc ----------
def test_health(client: TestClient):
    assert client.get("/health").json() == {"status": "ok"}
