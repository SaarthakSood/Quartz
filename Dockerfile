FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 HF_HOME=/app/.cache/huggingface PYTHONDONTWRITEBYTECODE=1
# CPU-only torch (the default PyPI wheel drags in ~2 GB of CUDA libs)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ backend/
COPY frontend/ frontend/
# Bake model weights into the image so the first request is fast (non-fatal if it fails)
RUN python -c "from backend import detector; detector.warm_up(); print(detector.status())" || true
RUN useradd -m -u 1000 appuser && mkdir -p /app/.cache && chown -R appuser:appuser /app
USER appuser
EXPOSE 7860
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "7860"]
