#!/bin/bash
set -e

echo "Starting TeleBirr API..."

# Wait for database connection (optional)
echo "Database URL: $DATABASE_URL"

# Start the application
exec gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
