@echo off
REM Use Python 3.13 where packages should be installed
set PYTHON_PATH=C:\Users\Muhammad Noor\AppData\Local\Programs\Python\Python313\python.exe

echo ========================================
echo CV Analyzer - Installing Dependencies
echo ========================================
echo.

echo Checking Python...
"%PYTHON_PATH%" --version
echo.

echo Installing Flask and dependencies...
"%PYTHON_PATH%" -m pip install Flask==3.0.0 PyPDF2==3.0.1 python-docx==1.1.0 Werkzeug==3.0.1
echo.

echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Run the application using: run.bat
echo Or manually: "%PYTHON_PATH%" app.py
echo.
pause

