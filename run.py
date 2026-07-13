import subprocess
import sys
import os

def run_services():
    # Ajusta los nombres de tus carpetas si son diferentes
    backend_folder = "backend" 
    frontend_folder = "frontend"

    # 🔥 IMPORTANTE: Si tu archivo principal en el backend NO se llama main.py,
    # cambia "main:app" por "el_nombre_de_tu_archivo:app"
    backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"]
    
    # Comando para el frontend
    frontend_cmd = ["npm", "start"]
    
    print("🚀 Iniciando el ecosistema (FastAPI + React)...")
    
    # Lanzamos el backend
    backend_proc = subprocess.Popen(backend_cmd, cwd=backend_folder)
    
    # 🔥 SOLUCIÓN AL WINERROR 2: Agregamos shell=True para que Windows reconozca "npm"
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_folder, shell=True)

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Apagando FastAPI y React limpiamente...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    run_services()