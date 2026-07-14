@echo off
REM Script para levantar el servidor Backend FastAPI
cd /d "%~dp0backend"
echo ========================================
echo Levantando servidor BACKEND (FastAPI)...
echo Puerto: http://localhost:8000
echo ========================================
python -m uvicorn server:app --reload --port 8000 --host 0.0.0.0
pause
