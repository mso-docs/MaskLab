# TASK-012 / REQ-023. Prepared image; building/publishing is not deployment authorization.
FROM node:22-bookworm-slim AS ui
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
FROM python:3.14-slim-bookworm AS package
WORKDIR /build
COPY requirements-dev.lock ./
RUN pip install --no-cache-dir --require-hashes -r requirements-dev.lock
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY --from=ui /build/src/masklab/static ./src/masklab/static
RUN python -m build --wheel --no-isolation
FROM python:3.14-slim-bookworm
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir --require-hashes -r requirements.lock
COPY --from=package /build/dist/*.whl ./
RUN pip install --no-deps *.whl && useradd -m -u 10001 masklab && mkdir /workspace && chown masklab:masklab /workspace
USER masklab
ENV MASKLAB_DATA_DIR=/workspace MASKLAB_MODE=demo
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"
CMD ["masklab","serve","--host","0.0.0.0"]
