# Backend image for Dokploy / any Docker host.
# DB lives on Neon (external) — no DB container needed.
# RAM: 1 worker ~ 175 MB. Do NOT raise --workers on a small VPS.

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p uploads   # StaticFiles mount requires this dir to exist

EXPOSE 8000

# Dokploy injects the exposed port; default 8000 otherwise.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
