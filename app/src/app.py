"""
app/src/app.py — Retail Platform Microservice
Author: Swanand Awatade | Binary Hat Pvt. Ltd.
DevOps Transformation Project — 40% faster time-to-market
"""
import os
import time
import logging
import datetime
from flask import Flask, jsonify, request, g
from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest,
    CONTENT_TYPE_LATEST, CollectorRegistry
)

# ── App Setup ─────────────────────────────────────────────
app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s"
)
log = logging.getLogger(__name__)

# ── Prometheus Metrics ────────────────────────────────────
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)
ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Currently active HTTP requests"
)
APP_INFO = Gauge(
    "app_info",
    "Application metadata",
    ["version", "environment", "build"]
)

# Set app info metric on startup
APP_INFO.labels(
    version=os.getenv("APP_VERSION", "1.0.0"),
    environment=os.getenv("DEPLOY_ENV", "production"),
    build=os.getenv("BUILD_NUMBER", "local")
).set(1)

# ── Middleware: track metrics on every request ─────────────
@app.before_request
def start_timer():
    g.start_time = time.time()
    ACTIVE_REQUESTS.inc()

@app.after_request
def record_metrics(response):
    if request.path != "/metrics":
        duration = time.time() - g.start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.path
        ).observe(duration)
        ACTIVE_REQUESTS.dec()
        log.info(
            "%s %s %d %.3fs",
            request.method, request.path,
            response.status_code, duration
        )
    return response

# ── Routes ─────────────────────────────────────────────────
@app.route("/")
def index():
    return jsonify({
        "service":     "retail-platform",
        "version":     os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("DEPLOY_ENV", "production"),
        "build":       os.getenv("BUILD_NUMBER", "local"),
        "timestamp":   datetime.datetime.utcnow().isoformat()
    })

@app.route("/health")
def health():
    return jsonify({
        "status":      "healthy",
        "version":     os.getenv("APP_VERSION", "1.0.0"),
        "uptime":      time.time(),
        "timestamp":   datetime.datetime.utcnow().isoformat()
    }), 200

@app.route("/ready")
def ready():
    """Kubernetes/ALB readiness probe."""
    return jsonify({"ready": True}), 200

@app.route("/api/products", methods=["GET"])
def get_products():
    """Simulated product catalogue endpoint."""
    products = [
        {"id": 1, "name": "Laptop",     "price": 999.99,  "stock": 42},
        {"id": 2, "name": "Smartphone", "price": 599.99,  "stock": 150},
        {"id": 3, "name": "Headphones", "price": 149.99,  "stock": 75},
        {"id": 4, "name": "Monitor",    "price": 349.99,  "stock": 30},
        {"id": 5, "name": "Keyboard",   "price":  79.99,  "stock": 200},
    ]
    return jsonify({"products": products, "count": len(products)})

@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    if product_id < 1 or product_id > 5:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"id": product_id, "name": f"Product {product_id}", "price": 99.99})

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({"error": "product_id and quantity required"}), 400
    order = {
        "order_id":   f"ORD-{int(time.time())}",
        "product_id": data["product_id"],
        "quantity":   data["quantity"],
        "status":     "created",
        "timestamp":  datetime.datetime.utcnow().isoformat()
    }
    log.info("Order created: %s", order["order_id"])
    return jsonify(order), 201

@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "path": request.path}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
