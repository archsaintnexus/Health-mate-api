FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --retries 10 --timeout 120 -r requirements.txt
RUN pip install gunicorn
COPY . .
WORKDIR /app/Health-mate-api
RUN python manage.py collectstatic --no-input || true
EXPOSE 8000
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
