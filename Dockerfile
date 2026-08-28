FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents ./agents
COPY server ./server
COPY data ./data

EXPOSE 8080
CMD exec gunicorn server.main:app --workers 1 --threads 8 --timeout 180 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT}
