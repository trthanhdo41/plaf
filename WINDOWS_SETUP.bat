@echo off
REM PLAF Setup Script for Windows
REM Quick setup for customers on Windows machines

echo ================================================================
echo PLAF - Prescriptive Learning Analytics Framework
echo Windows Setup Script
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python found!
python --version
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists!
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo [4/5] Installing dependencies (this may take a few minutes)...
pip install --upgrade pip --quiet
pip install streamlit sqlalchemy google-generativeai scikit-learn plotly python-dotenv scipy joblib pandas numpy faiss-cpu werkzeug catboost xgboost --quiet
echo Dependencies installed!
echo.

REM Create necessary directories
echo [5/5] Creating directories...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist models mkdir models
if not exist results mkdir results
if not exist plots mkdir plots
if not exist plots\shap mkdir plots\shap
echo Directories created!
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file...
    echo GEMINI_API_KEY=AIzaSyBxqH7HXGHGFcdBz13GBPN8BrnEj5hf3R0 > .env
    echo .env file created!
)
echo.

echo ================================================================
echo Setup Complete!
echo ================================================================
echo.
echo OULAD Dataset is already included in the "OULAD dataset" folder!
echo.
echo Next steps:
echo.
echo 1. Load FULL OULAD data (32K students, 10M+ interactions):
echo    python src\data\load_full_oulad.py
echo.
echo 2. Create test user:
echo    python create_test_user.py
echo.
echo 3. Run Student Portal:
echo    streamlit run src\lms_portal\student_app.py
echo.
echo 4. Run Advisor Dashboard (in new terminal):
echo    streamlit run src\dashboard\app.py --server.port 8502
echo.
echo 5. Run Benchmarks (optional):
echo    python run_all_benchmarks.py
echo.
echo ================================================================
echo Press any key to exit...
pause >nul

