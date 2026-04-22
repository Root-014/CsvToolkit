@echo off

echo ============================================================================
echo          CSV Analysis Web Application - Startup Script (Windows)
echo ============================================================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Node.js is not installed
    echo    Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python is not installed
    echo    Please install Python from https://python.org/
    pause
    exit /b 1
)

echo [OK] Node.js found
node --version
echo [OK] Python found
python --version
echo.

REM Install frontend dependencies if needed
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
    echo.
)

REM Install backend dependencies
echo Installing Python dependencies...
cd backend
pip install -r requirements.txt
cd ..
echo.

REM Compile TypeScript
echo Compiling TypeScript...
npm run build

if %errorlevel% neq 0 (
    echo [X] TypeScript compilation failed
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Starting CSV Analysis Web Application...
echo ============================================================================
echo.
echo Frontend: http://localhost:5000
echo Backend API: http://localhost:5000
echo.
echo Press Ctrl+C to stop
echo ============================================================================
echo.

REM Start the backend
cd backend
python app.py