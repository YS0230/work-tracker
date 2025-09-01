@echo off
echo Setting up Work Tracker System...
echo.

cd backend

echo Checking virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo === Frontend Build Process ===
cd ..\frontend

echo Installing frontend dependencies...
if exist "node_modules" (
    echo Frontend dependencies already exist. Updating...
) else (
    echo Installing frontend dependencies...
)
call npm install

echo Building frontend for production...
call npm run build

echo Copying frontend build to backend static folder...
if exist "dist" (
    echo Cleaning old static files...
    if exist "..\backend\static\*" del /q "..\backend\static\*"
    if exist "..\backend\static\css" rmdir /s /q "..\backend\static\css"
    if exist "..\backend\static\js" rmdir /s /q "..\backend\static\js"
    if exist "..\backend\static\img" rmdir /s /q "..\backend\static\img"
    
    echo Copying new build files...
    xcopy /s /e "dist\*" "..\backend\static\"
    echo Frontend build copied to backend successfully!
) else (
    echo ERROR: Frontend build failed - dist folder not found!
    pause
    exit /b 1
)

echo.
echo === Setup Completed! ===
echo Frontend has been built and packaged into backend.
echo You can now run start.bat to launch the integrated application.
echo.
pause