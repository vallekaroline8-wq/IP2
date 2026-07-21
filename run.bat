@echo off
:: Iniciar Backend en una nueva ventana CMD
start cmd /k "cd backend && uvicorn server:app --reload"

:: Iniciar Frontend en la ventana actual
cd frontend
npm start