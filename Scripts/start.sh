#!/bin/sh
set -e

# ── Wait for database (local Docker only) ────────────────────
# On Render/Production, DATABASE_URL points to Supabase
# which is always available — no need to wait
if [ -z "$DATABASE_URL" ]; then
    DB_HOST="${DB_HOST:-db}"
    DB_PORT="${DB_PORT:-5432}"
    echo "==> Waiting for database at ${DB_HOST}:${DB_PORT}..."
    while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
        sleep 1
    done
    echo "==> Database is ready."
else
    echo "==> Using DATABASE_URL — skipping wait."
fi

# ── Collect static files ──────────────────────────────────────
echo "==> Collecting static files..."
python manage.py collectstatic --noinput

# ── Run migrations ────────────────────────────────────────────
echo "==> Running migrations..."
python manage.py migrate --noinput

# ── Start Gunicorn ────────────────────────────────────────────
APP_MODULE="${GUNICORN_APP_MODULE:-core.wsgi:application}"
BIND_ADDR="0.0.0.0:${PORT:-8000}"
WORKERS="${GUNICORN_WORKERS:-2}"
TIMEOUT="${GUNICORN_TIMEOUT:-120}"

echo "==> Starting Gunicorn on ${BIND_ADDR} (${WORKERS} workers)..."
exec gunicorn "$APP_MODULE" \
    --bind     "$BIND_ADDR" \
    --workers  "$WORKERS" \
    --timeout  "$TIMEOUT" \
    --access-logfile - \
    --error-logfile  -
    