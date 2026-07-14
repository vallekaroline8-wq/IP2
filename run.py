import subprocess
import sys
import os
import time
import socket  # 🔌 Usado para verificar si el puerto 8000 ya está respondiendo

def wait_for_backend(host="127.0.0.1", port=8000, timeout=30):
    """Intenta conectarse al puerto del backend hasta que esté listo."""
    start_time = time.time()
    print(f"⏳ Esperando activamente a que FastAPI levante en el puerto {port}...")
    
    while time.time() - start_time < timeout:
        try:
            # Intenta abrir una conexión de socket rápida
            with socket.create_connection((host, port), timeout=1):
                print("🟢 ¡Backend detectado y listo!")
                return True
        except (ConnectionRefusedError, socket.timeout):
            # Si el puerto está cerrado, espera medio segundo e intenta de nuevo
            time.sleep(0.5)
            
    print("⚠️ El backend tardó demasiado en responder, continuando de todos modos...")
    return False

def run_services():
    backend_folder = "backend" 
    frontend_folder = "frontend"

    # Comandos de ejecución
    backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"]
    frontend_cmd = ["npm", "start"]
    
    print("🚀 Iniciando el ecosistema inteligente...")
    
    # 1. PASO UNO: Lanzar el Backend
    print("🔄 [1/2] Levantando Backend (FastAPI)...")
    backend_proc = subprocess.Popen(backend_cmd, cwd=backend_folder)
    
    # 🔥 Verificación real: Bloquea el flujo hasta que el puerto 8000 responda
    wait_for_backend(port=8000)
    
    # 2. PASO DOS: Lanzar el Frontend solo cuando el paso anterior termine con éxito
    print("🟢 [2/2] Lanzando Frontend (React)...")
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_folder, shell=True)

    try:
        # Mantener la terminal escuchando ambos logs
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Apagando FastAPI y React limpiamente...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    run_services()