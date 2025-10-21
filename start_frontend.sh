#!/bin/bash

# Start PLAF Frontend & Backend
# This script starts both the FastAPI backend and Next.js frontend

set -e

echo "========================================"
echo "🚀 PLAF - Starting Frontend & Backend"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run quick_start.sh first."
    exit 1
fi

# Start Backend API
echo "========================================"
echo "STEP 1: Starting Backend API"
echo "========================================"
echo ""

# Check if API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set. AI features may not work."
    echo "To set it, run: export GEMINI_API_KEY=your_key_here"
    echo ""
fi

echo "Starting FastAPI server on http://localhost:8000..."
venv/bin/python src/api/main.py &
API_PID=$!
echo "✅ Backend API started (PID: $API_PID)"
echo ""

# Wait for API to be ready
echo "Waiting for API to be ready..."
for i in {1..15}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo "✅ Backend API is ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "⚠️  API may still be starting..."
    fi
    sleep 1
done
echo ""

# Start Frontend
echo "========================================"
echo "STEP 2: Starting Frontend"
echo "========================================"
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

echo "Starting Next.js development server on http://localhost:3000..."
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""

cd ..

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
for i in {1..20}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "⚠️  Frontend may still be starting..."
    fi
    sleep 1
done
echo ""

echo "========================================"
echo "✅ PLAF is Running!"
echo "========================================"
echo ""
echo -e "${GREEN}🌐 Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}🔌 Backend API:${NC} http://localhost:8000"
echo -e "${BLUE}📚 API Docs:${NC} http://localhost:8000/docs"
echo ""
echo "Demo Login:"
echo "  Email: student11391@ou.ac.uk"
echo "  Password: demo123"
echo ""
echo -e "${YELLOW}To stop servers, press Ctrl+C${NC}"
echo ""

# Save PIDs for cleanup
echo $API_PID > .api.pid
echo $FRONTEND_PID > .frontend.pid

# Wait for user interrupt
trap 'echo ""; echo "Stopping servers..."; kill $API_PID $FRONTEND_PID 2>/dev/null; rm -f .api.pid .frontend.pid; echo "✅ Servers stopped"; exit 0' INT TERM

# Keep script running
wait

