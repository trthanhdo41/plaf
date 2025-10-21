#!/bin/bash

# PLAF Quick Start Script for Ubuntu/Linux
# This script runs the full pipeline and starts Student Portal

set -e  # Exit on error

echo "========================================"
echo "PLAF SYSTEM - QUICK START"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    # Try to use Python 3.11 or 3.12 (pandas 2.1.4 doesn't support 3.14 yet)
    if command -v python3.11 &> /dev/null; then
        python3.11 -m venv venv
    elif command -v python3.12 &> /dev/null; then
        python3.12 -m venv venv
    elif command -v python3.10 &> /dev/null; then
        python3.10 -m venv venv
    else
        echo "⚠️  Warning: Using default python3 (may cause issues if version > 3.13)"
        python3 -m venv venv
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ ! -f ".dependencies_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch .dependencies_installed
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "========================================"
echo "STEP 1: Running ML Pipeline"
echo "========================================"
echo ""

# Run pipeline
python run_pipeline.py

echo ""
echo "========================================"
echo "STEP 2: Loading VLE Data"
echo "========================================"
echo ""

# Load VLE data from OULAD into database
python src/data/load_vle_data.py

echo ""
echo "========================================"
echo "STEP 3: Creating Demo Accounts"
echo "========================================"
echo ""

# Create demo accounts
python src/data/create_demo_accounts.py

echo ""
echo "========================================"
echo "STEP 4: Setup API Key for AI Features"
echo "========================================"
echo ""

# Check if API key is already set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  AI features require a Gemini API key."
    echo ""
    echo "To get your API key:"
    echo "1. Visit: https://aistudio.google.com/app/apikey"
    echo "2. Click 'Create API Key'"
    echo "3. Copy the generated key"
    echo ""
    
    read -p "Enter your Gemini API key (or press Enter to skip): " api_key
    
    if [ ! -z "$api_key" ]; then
        export GEMINI_API_KEY="$api_key"
        echo "✅ API key set successfully!"
        
        # Test API key
        echo "Testing API key..."
        python -c "
import os
try:
    from src.chatbot.rag_system import RAGSystem
    rag = RAGSystem()
    print('✅ API key is working!')
except Exception as e:
    print('❌ API key error:', str(e))
    print('AI features may not work properly.')
"
    else
        echo "⚠️  Skipping API key setup. AI features will be disabled."
    fi
else
    echo "✅ API key already set!"
fi

echo ""
echo "========================================"
echo "STEP 5: Setup Complete!"
echo "========================================"
echo ""

echo "✅ All setup steps completed successfully!"
echo ""
echo "========================================"
echo "🚀 Starting PLAF System..."
echo "========================================"
echo ""

# Run the full system startup script
./start_plaf.sh

