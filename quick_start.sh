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
echo "STEP 2: Creating Demo Accounts"
echo "========================================"
echo ""

# Create demo accounts
python src/data/create_demo_accounts.py

echo ""
echo "========================================"
echo "STEP 3: Starting Student Portal"
echo "========================================"
echo ""

echo "Student Portal will start at: http://localhost:8501"
echo ""
echo "LOGIN CREDENTIALS:"
echo "  Email: student650515@ou.ac.uk"
echo "  Password: demo123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Student Portal
streamlit run src/lms_portal/student_app.py --server.port 8501

