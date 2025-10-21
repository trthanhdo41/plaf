#!/bin/bash

# PLAF Stop Script
# Stops both Backend and Frontend servers

echo "Stopping PLAF servers..."

# Kill by PID files if they exist
if [ -f ".backend.pid" ]; then
    kill $(cat .backend.pid) 2>/dev/null && echo "✅ Backend stopped"
    rm -f .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    kill $(cat .frontend.pid) 2>/dev/null && echo "✅ Frontend stopped"
    rm -f .frontend.pid
fi

# Kill by port as backup
pkill -f "python.*src/api/main" 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ All PLAF servers stopped"

