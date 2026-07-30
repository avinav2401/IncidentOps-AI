@echo off
echo Starting IncidentOps AI...

echo Starting Backend API (Port 8000)...
start "IncidentOps Backend" cmd /k "cd backend && python -m venv .venv && call .\.venv\Scripts\activate.bat && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000"

echo Starting Frontend UI (Port 3000)...
start "IncidentOps Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo Done! The frontend will be available at http://localhost:3000 in a few seconds.
pause
