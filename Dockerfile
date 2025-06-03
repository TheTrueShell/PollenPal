# Use Python 3.11 slim as base image
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Install the package in the virtual environment
RUN uv pip install -e .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash pollenpal
RUN chown -R pollenpal:pollenpal /app
USER pollenpal

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Default command
CMD ["uv", "run", "uvicorn", "pollenpal.api.main:app", "--host", "0.0.0.0", "--port", "3000"] 