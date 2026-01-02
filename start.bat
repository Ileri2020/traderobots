@echo off
echo Starting Traderobots Project Locally...

:: Navigate to root directory (just in case)
cd /d "%~dp0"

echo [1/2] Starting Backend Server (Django)...
start cmd /k "cd backend && venv\Scripts\activate && python manage.py runserver"

echo [2/2] Starting Frontend Server (Vite)...
start cmd /k "cd frontend && npm run dev"

echo Project is launching!
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:5173 
pause
