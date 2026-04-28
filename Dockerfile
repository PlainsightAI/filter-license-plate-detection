# syntax=docker/dockerfile:1.4
# torch on PyPI (>=2.10) includes CUDA on Linux x86_64 automatically.
# GPU is available when run with --gpus; falls back to CPU otherwise.
FROM python:3.11.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd -ms /bin/bash appuser
WORKDIR /app

COPY --chown=appuser:appuser . .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# No model is bundled in the image. Mount or set FILTER_MODEL_PATH at runtime.
# Example: docker run -v /host/model.pth:/app/model.pth -e FILTER_MODEL_PATH=/app/model.pth ...
USER appuser
CMD ["python", "-m", "filter_license_plate_detection.filter"]
