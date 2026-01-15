@echo off
echo ========================================
echo Schedule Notifier - Quick Setup
echo ========================================
echo.

echo [1/4] Setting up Backend...
cd backend
if not exist ".env" (
    copy .env.example .env
    echo Created backend/.env - Please edit with your Firebase credentials
) else (
    echo backend/.env already exists
)
cd ..

echo.
echo [2/4] Setting up Frontend...
cd frontend
if not exist ".env" (
    copy .env.example .env
    echo Created frontend/.env - Please edit with your Firebase config
) else (
    echo frontend/.env already exists
)
cd ..

echo.
echo [3/4] Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo [4/4] Installing Frontend Dependencies...
cd frontend
call npm install
cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit backend/.env with your Firebase credentials path
echo 2. Edit frontend/.env with your Firebase configuration
echo 3. Edit frontend/public/firebase-messaging-sw.js with Firebase config
echo 4. Run backend: cd backend ^&^& python api.py
echo 5. Run frontend: cd frontend ^&^& npm run dev
echo.
pause
