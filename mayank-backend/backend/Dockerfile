FROM python:3.12-slim

# Faster, quieter, reproducible Python in containers.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# System deps for PyMuPDF / sentence-transformers wheels (kept minimal).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first so this layer is cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application (includes the prebuilt FIA Chroma index under app/rag/).
COPY . .

# Run as a non-root user.
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Container healthcheck hits the existing /health/ endpoint.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/health/" || exit 1

# Shell form so ${PORT} is expanded (Railway/Render inject their own PORT).
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
