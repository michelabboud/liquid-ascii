# Multi-stage Dockerfile for Liquid ASCII Art Animation
# Optimized for small image size and fast builds

# Stage 1: Builder
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libportaudio2 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency installation
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml README.md ./

# Install dependencies in a virtual environment
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install -e .

# Stage 2: Runtime
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY benchmarks/ ./benchmarks/
COPY pyproject.toml README.md ./

# Ensure virtual environment is used
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Set terminal environment variables
ENV TERM=xterm-256color
ENV COLUMNS=80
ENV LINES=40

# Create non-root user for security
RUN useradd -m -u 1000 liquidascii && \
    chown -R liquidascii:liquidascii /app

USER liquidascii

# Default entry point
ENTRYPOINT ["python", "-m", "src.main"]

# Default command (can be overridden)
CMD ["--help"]

# Metadata
LABEL maintainer="Liquid ASCII Contributors"
LABEL description="Terminal-based ASCII art animation with liquid 3D rendering and lip sync"
LABEL version="0.2.0"
