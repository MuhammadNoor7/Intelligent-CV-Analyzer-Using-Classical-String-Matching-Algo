@echo off
REM Use Python 3.13 where packages are installed
set PYTHON_PATH=C:\Users\Muhammad Noor\AppData\Local\Programs\Python\Python313\python.exe

echo ========================================
echo CV Analyzer - Flask Application
echo ========================================
echo.

echo Checking Python...
"%PYTHON_PATH%" --version
echo.

echo Installing dependencies...
"%PYTHON_PATH%" -m pip install -r requirements.txt
echo.

echo ========================================
echo Starting Flask development server...
echo ========================================
echo.
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

"%PYTHON_PATH%" app.py

pause
