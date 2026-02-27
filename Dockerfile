#syntax=docker/dockerfile:1
#*********************************** Backend API DockerFile  ***********************************
# =========================
# Builder
# =========================
FROM python:3.14.3-alpine3.23 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies (ONLY in builder)
RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    musl-dev \
    gcc \
    libffi-dev

# Create virtualenv
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools wheel

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir .

# =========================
# Runtime
# =========================
FROM python:3.14.3-alpine3.23

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# Install ONLY runtime libraries (no compilers)
# wget: used by HEALTHCHECK (more reliable than Python urllib in minimal Alpine)
RUN apk add --no-cache \
    libpq \
    wget

# Create non-root user
RUN addgroup -S app && adduser -S app -G app

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /venv /venv

# Copy app
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN mkdir -p /app/staticfiles && \
    chown -R app:app /app

USER app

# -------------------------
# Healthcheck (ECS ready)
# -------------------------
HEALTHCHECK --interval=20s --timeout=5s --start-period=60s --retries=3 \
CMD python -c "import urllib.request,sys; \
    sys.exit(0) if urllib.request.urlopen('http://localhost:8000/api/health/').status == 200 else sys.exit(1)"

EXPOSE 8000

CMD ["/entrypoint.sh"]