# syntax=docker/dockerfile:1.4
# torch on PyPI (>=2.10) includes CUDA on Linux x86_64 automatically.
# GPU is available when run with --gpus; falls back to CPU otherwise.
# openfilter-base = python:3.11-slim + all outstanding Debian security patches
# (rebuilt weekly): provides the PYTHONDONTWRITEBYTECODE/PYTHONUNBUFFERED env, the
# appuser account, and /app (WORKDIR) + /app/logs — so none of that is repeated here.
FROM plainsightai/openfilter-base:py3.11

COPY --chown=appuser:appuser . .
# Preserve the build-commit facet: the release CI writes GITHUB_SHA, which
# openfilter reads from VERSION_SHA to report version_sha. Rename after COPY.
RUN if [ -f GITHUB_SHA ]; then mv GITHUB_SHA VERSION_SHA; fi
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# No model is bundled in the image. Mount or set FILTER_MODEL_PATH at runtime.
# Example: docker run -v /host/model.pth:/app/model.pth -e FILTER_MODEL_PATH=/app/model.pth ...
USER appuser
CMD ["python", "-m", "filter_license_plate_detection.filter"]
