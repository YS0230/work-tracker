@echo off
echo Starting Work Tracker System...
echo.

REM Check if setup has been run
cd backend
if not exist "venv" (
    echo.
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to initialize the environment.
    echo.
    pause
    exit /b 1
)

cd ..
if not exist "frontend\node_modules" (
    echo.
    echo ERROR: Frontend dependencies not found!
    echo Please run setup.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

echo Starting integrated application (frontend built into backend)...
echo.

cd backend

echo Starting integrated service...
start cmd /k "cd /d %cd% && venv\Scripts\activate.bat && python app.py"

echo.
echo System startup completed!
echo Visit: http://localhost:5000

:end
pause