@echo off
echo ============================================
echo   NSU Academic Audit System - Setup
echo ============================================
echo.

echo [1/4] Installing backend dependencies...
cd app\backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Installing frontend dependencies...
cd ..\frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Starting backend server...
cd ..\backend
start "NSU Backend" cmd /k "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [4/4] Starting frontend...
cd ..\frontend
timeout /t 3 /nobreak >nul
start "NSU Frontend" cmd /k "npm start"

echo.
echo ============================================
echo   Setup complete!
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3000
echo ============================================
pause
