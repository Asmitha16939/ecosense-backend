#!/bin/bash
# EcoSense Backend Startup Script
# Usage: bash start.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🌿 EcoSense Backend Startup"
echo "─────────────────────────────"

# Load .env to get DB credentials
export $(grep -v '^#' .env | xargs)

# Check if MySQL is accessible
echo "🔍 Checking MySQL connection..."
if mysql -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" &>/dev/null; then
    echo "✅ MySQL connected"
else
    echo "❌ MySQL connection failed."
    echo "   → Make sure MySQL is running"
    echo "   → Update DB_PASSWORD in backend/.env"
    exit 1
fi

# Create database & tables if not exists
echo "🗄️  Initialising database..."
mysql -u "$DB_USER" -p"$DB_PASSWORD" < init_db.sql 2>/dev/null || true
echo "✅ Database ready"

# Kill any process on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t &>/dev/null; then
    echo "⚠️  Port 8000 busy — killing existing process..."
    kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 1
fi

echo "🚀 Starting FastAPI on http://localhost:8000"
echo "   API docs: http://localhost:8000/api/docs"
echo "─────────────────────────────"
"$SCRIPT_DIR/venv/bin/python" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
