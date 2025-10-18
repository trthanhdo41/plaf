#!/bin/bash

# Script to update Gemini API key and restart Student Portal

if [ -z "$1" ]; then
    echo "Usage: ./update_api_key.sh YOUR_API_KEY"
    echo "Example: ./update_api_key.sh AIzaSyAyUJgplnBnutMJMbpHhlAvEaBDeo4jXUU"
    exit 1
fi

API_KEY=$1

echo "Updating Gemini API key..."
export GEMINI_API_KEY=$API_KEY

echo "Testing API key..."
cd "/Users/mac/Desktop/plaf "
source venv/bin/activate

python -c "
import os
from src.chatbot.rag_system import RAGSystem

# Test API key
try:
    rag = RAGSystem()
    print('✅ API key is working!')
except Exception as e:
    print('❌ API key error:', str(e))
"

if [ $? -eq 0 ]; then
    echo "✅ API key updated successfully!"
    echo "Student Portal will use the new API key."
    echo ""
    echo "To restart Student Portal:"
    echo "streamlit run src/lms_portal/student_app.py --server.port 8501"
else
    echo "❌ API key test failed. Please check your API key."
fi
