@echo off
REM PLAF Quick Start Script for Windows
REM This script runs the full pipeline and starts Student Portal

echo ========================================
echo PLAF SYSTEM - QUICK START (WINDOWS)
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
if not exist ".dependencies_installed" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo. > .dependencies_installed
    echo Dependencies installed
) else (
    echo Dependencies already installed
)

echo.
echo ========================================
echo STEP 1: Running ML Pipeline
echo ========================================
echo.

REM Run pipeline
python run_pipeline.py

echo.
echo ========================================
echo STEP 2: Creating Demo Accounts
echo ========================================
echo.

REM Create demo accounts
python src/data/create_demo_accounts.py

echo.
echo ========================================
echo STEP 3: Starting Student Portal
echo ========================================
echo.

echo Student Portal will start at: http://localhost:8501
echo.
echo LOGIN CREDENTIALS:
echo   Email: student650515@ou.ac.uk
echo   Password: demo123
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start Student Portal
streamlit run src/lms_portal/student_app.py --server.port 8501

pause

