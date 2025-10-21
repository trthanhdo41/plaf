#!/bin/bash

# PLAF Full System Startup Script
# Starts both Backend API and Next.js Frontend

set -e

echo "========================================"
echo "🚀 PLAF - Starting Full System"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run quick_start.sh first to setup the system."
    exit 1
fi

# Check if frontend is set up
if [ ! -d "frontend/node_modules" ]; then
    echo "Setting up frontend..."
    cd frontend
    npm install
    cd ..
    echo "✅ Frontend dependencies installed"
fi

echo "========================================"
echo "STEP 1: Starting Backend API Server"
echo "========================================"
echo ""

# Activate virtual environment
source venv/bin/activate

# Check if API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set!"
    echo "AI features (chatbot, advisor) will not work."
    echo ""
    read -p "Enter your Gemini API key (or press Enter to skip): " api_key
    
    if [ ! -z "$api_key" ]; then
        export GEMINI_API_KEY="$api_key"
        echo "✅ API key set!"
    else
        echo "⚠️  Continuing without API key..."
    fi
    echo ""
fi

# Start backend in background
echo "Starting FastAPI backend on http://localhost:8000..."
python src/api/main.py > /dev/null 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait for backend to be ready
echo "Waiting for backend to initialize..."
for i in {1..15}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo "✅ Backend API is ready!"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "⚠️  Backend may still be starting..."
    fi
    sleep 1
done
echo ""

echo "========================================"
echo "STEP 2: Starting Frontend Server"
echo "========================================"
echo ""

# Start frontend in background
cd frontend
echo "Starting Next.js frontend on http://localhost:3000..."
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""

# Wait for frontend to be ready
echo "Waiting for frontend to initialize..."
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
echo "✨ PLAF System is Running!"
echo "========================================"
echo ""
echo -e "${GREEN}🌐 Frontend (Next.js):${NC} http://localhost:3000"
echo -e "${BLUE}🔌 Backend API:${NC} http://localhost:8000"
echo -e "${BLUE}📚 API Documentation:${NC} http://localhost:8000/docs"
echo ""
echo "========================================"
echo "📝 Demo Login Credentials:"
echo "========================================"
echo ""
echo "  Email: student650515@ou.ac.uk"
echo "  Password: demo123"
echo ""
echo "  (Or create a new account via Sign Up)"
echo ""
echo "========================================"
echo "ℹ️  System Information:"
echo "========================================"
echo ""
echo "  • Backend PID: $BACKEND_PID"
echo "  • Frontend PID: $FRONTEND_PID"
echo "  • Logs: Check terminal output above"
echo ""
echo -e "${YELLOW}⚠️  To stop all servers:${NC}"
echo "  Press Ctrl+C or run: ./stop_plaf.sh"
echo ""

# Save PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Trap to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    rm -f .backend.pid .frontend.pid
    echo "✅ All servers stopped"
    exit 0
}

trap cleanup INT TERM

# Keep script running and show logs
echo "📊 Monitoring servers (Ctrl+C to stop)..."
echo ""

# Wait for both processes
wait

