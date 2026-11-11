FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS test
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
RUN flake8 . && pytest -q

FROM base AS runtime
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}
COPY app.py .
RUN useradd --uid 10001 --no-create-home appuser
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=15s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')" || exit 1
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
