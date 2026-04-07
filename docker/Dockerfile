# ============================================================
#  Dockerfile — Multi-stage build for retail-platform app
#  Author: Swanand Awatade | Binary Hat Pvt. Ltd.
# ============================================================

# ── Stage 1: Test ─────────────────────────────────────────
FROM python:3.11-slim AS tester

WORKDIR /build
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest pytest-cov

COPY app/ .
RUN python -m pytest tests/ -v \
    --cov=src \
    --cov-report=term-missing \
    --cov-fail-under=80

# ── Stage 2: Production Image ──────────────────────────────
FROM python:3.11-slim AS production

# Security: non-root user
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -d /app -s /sbin/nologin appuser

WORKDIR /app

# Install deps first (layer caching)
COPY app/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    # Remove pip cache
    rm -rf /root/.cache/pip

# Copy app source
COPY --from=tester /build/src/ .

# Switch to non-root
USER appuser

ENV PORT=8080 \
    APP_VERSION=1.0.0 \
    DEPLOY_ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD ["gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "60", \
     "--keepalive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:app"]
