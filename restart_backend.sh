#!/bin/bash
# Quick script to restart backend

echo "🛑 Stopping backend..."
pkill -f "python.*api/main" 2>/dev/null
sleep 2

echo "🚀 Starting backend..."
cd "/Users/mac/Desktop/plaf "
source venv/bin/activate
export GEMINI_API_KEY=AIzaSyAyUJgplnBnutMJMbpHhlAvEaBDeo4jXUU
python src/api/main.py

