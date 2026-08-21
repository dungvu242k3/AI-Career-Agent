FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY be/requirements.txt be/requirements-observability.txt /app/be/
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/be/requirements.txt \
    && python -m pip install --no-cache-dir -r /app/be/requirements-observability.txt

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/data \
    && chown appuser:appuser /app/data

COPY --chown=appuser:appuser ai /app/ai
COPY --chown=appuser:appuser be /app/be

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2)"

CMD ["uvicorn", "be.main:app", "--host", "0.0.0.0", "--port", "8000"]
