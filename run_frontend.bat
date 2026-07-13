@echo off
REM Script para levantar el servidor Frontend React
cd /d "%~dp0frontend"
echo ========================================
echo Levantando servidor FRONTEND (React)...
echo Puerto: http://localhost:3000
echo ========================================
npm start
pause
