"""
tests/test_app.py — Full test suite for retail-platform app
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Core Endpoint Tests ────────────────────────────────────
class TestCoreEndpoints:
    def test_index_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_index_returns_service_info(self, client):
        data = client.get("/").get_json()
        assert data["service"] == "retail-platform"
        assert "version" in data
        assert "timestamp" in data

    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_is_json(self, client):
        r = client.get("/health")
        assert "application/json" in r.content_type

    def test_health_status_field(self, client):
        data = client.get("/health").get_json()
        assert data["status"] == "healthy"

    def test_readiness_probe(self, client):
        r = client.get("/ready")
        assert r.status_code == 200
        assert client.get("/ready").get_json()["ready"] is True

    def test_metrics_endpoint(self, client):
        r = client.get("/metrics")
        assert r.status_code == 200
        assert b"http_requests_total" in r.data


# ── Products API Tests ─────────────────────────────────────
class TestProductsAPI:
    def test_list_products(self, client):
        r = client.get("/api/products")
        assert r.status_code == 200

    def test_products_response_structure(self, client):
        data = client.get("/api/products").get_json()
        assert "products" in data
        assert "count" in data
        assert isinstance(data["products"], list)
        assert data["count"] == len(data["products"])

    def test_products_have_required_fields(self, client):
        products = client.get("/api/products").get_json()["products"]
        for p in products:
            assert "id" in p
            assert "name" in p
            assert "price" in p

    def test_get_single_product(self, client):
        r = client.get("/api/products/1")
        assert r.status_code == 200
        data = r.get_json()
        assert data["id"] == 1

    def test_product_not_found(self, client):
        r = client.get("/api/products/9999")
        assert r.status_code == 404
        assert "error" in r.get_json()


# ── Orders API Tests ───────────────────────────────────────
class TestOrdersAPI:
    def test_create_order_success(self, client):
        r = client.post("/api/orders",
                        json={"product_id": 1, "quantity": 2},
                        content_type="application/json")
        assert r.status_code == 201

    def test_create_order_response_fields(self, client):
        r = client.post("/api/orders",
                        json={"product_id": 1, "quantity": 3},
                        content_type="application/json")
        data = r.get_json()
        assert "order_id" in data
        assert data["status"] == "created"
        assert data["product_id"] == 1
        assert data["quantity"] == 3

    def test_create_order_missing_product_id(self, client):
        r = client.post("/api/orders",
                        json={"quantity": 1},
                        content_type="application/json")
        assert r.status_code == 400

    def test_create_order_missing_quantity(self, client):
        r = client.post("/api/orders",
                        json={"product_id": 1},
                        content_type="application/json")
        assert r.status_code == 400

    def test_create_order_empty_body(self, client):
        r = client.post("/api/orders",
                        json={},
                        content_type="application/json")
        assert r.status_code == 400


# ── Error Handling Tests ───────────────────────────────────
class TestErrorHandling:
    def test_404_returns_json(self, client):
        r = client.get("/nonexistent-path")
        assert r.status_code == 404
        data = r.get_json()
        assert "error" in data

    def test_404_includes_path(self, client):
        r = client.get("/nonexistent-path")
        data = r.get_json()
        assert data.get("path") == "/nonexistent-path"
