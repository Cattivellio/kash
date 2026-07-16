FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/

ENV KASH_HOST=0.0.0.0
ENV KASH_PORT=8400

EXPOSE 8400

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8400"]
