#!/bin/bash
# Quick script to restart backend

echo "🛑 Stopping backend..."
pkill -f "python.*api/main" 2>/dev/null
sleep 2

echo "🚀 Starting backend..."

# Get script directory (works for both relative and absolute paths)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "📝 Loading API key from .env file..."
    set -a
    source .env
    set +a
    echo "✅ API key loaded"
else
    echo "⚠️  Warning: .env file not found!"
    echo "Create .env file with: GEMINI_API_KEY=your_key_here"
fi

# Check if API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY not set!"
    echo "Please create a .env file with your API key"
    exit 1
fi

echo "✅ Starting backend with API key from .env..."
python src/api/main.py

