#!/bin/bash

echo "================================"
echo "PLAF Quick Setup Script"
echo "================================"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install --quiet pandas numpy scikit-learn python-dotenv google-generativeai streamlit plotly faiss-cpu 2>/dev/null || pip install --quiet pandas numpy scikit-learn python-dotenv google-generativeai streamlit plotly faiss-cpu

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    echo "GEMINI_API_KEY=AIzaSyBxqH7HXGHGFcdBz13GBPN8BrnEj5hf3R0" > .env
    echo "✓ .env created with API key"
fi

# Create necessary directories
mkdir -p data logs plots/shap models results

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Test the system:"
echo "  python3 test_lms_system.py"
echo ""
echo "Run Student Portal:"
echo "  streamlit run src/lms_portal/student_app.py"
echo ""
echo "Run Advisor Dashboard:"
echo "  streamlit run src/dashboard/app.py"
echo ""

