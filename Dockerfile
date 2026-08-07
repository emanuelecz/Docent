FROM python:3.11-slim

# Install system dependencies needed for psycopg2, pgvector bindings, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager used by this project)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency manifests first for better layer caching
COPY pyproject.toml uv.lock ./

# Install all dependencies into the system Python (no virtualenv inside container)
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application source
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Default command: run the API server via uvicorn
CMD ["uv", "run", "uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
