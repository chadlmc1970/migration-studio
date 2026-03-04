#!/bin/bash
# Reliable dev environment startup script with cache clearing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🧹 Cleaning up old processes..."
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:3001 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

echo "🗑️  Clearing frontend caches..."
cd "$PROJECT_ROOT/frontend"
rm -rf .next node_modules/.cache 2>/dev/null || true

echo "🚀 Starting backend server..."
cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/migration_studio_backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

sleep 3

echo "🎨 Starting frontend server..."
cd "$PROJECT_ROOT/frontend"
npm run dev > /tmp/migration_studio_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

sleep 5

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Migration Studio Dev Environment Ready"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Frontend:  http://localhost:3001"
echo "📍 Backend:   http://localhost:8000"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f /tmp/migration_studio_backend.log"
echo "   Frontend: tail -f /tmp/migration_studio_frontend.log"
echo ""
echo "🛑 To stop both servers:"
echo "   lsof -ti:8000 | xargs kill; lsof -ti:3001 | xargs kill"
echo ""
echo "💡 Tip: If you see webpack errors, re-run this script to auto-clean caches"
echo ""
