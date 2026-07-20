from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router
from routes.dashboard import router as dashboard_router
from routes.departamentos import router as departamentos_router
from routes.usuariosmodulo import router as usuarios_router
from routes.asignaciones import router as asignaciones_router

app = FastAPI(
    title="SIGIP API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(departamentos_router)
app.include_router(usuarios_router)
app.include_router(asignaciones_router)

# ==========================================
# MOSTRAR RUTAS REGISTRADAS
# ==========================================

print("\n========== RUTAS REGISTRADAS ==========\n")

for ruta in app.routes:
    print(f"{ruta.methods} -> {ruta.path}")

print("\n=======================================\n")


@app.get("/")
def inicio():
    return {
        "mensaje": "SIGIP Backend MySQL funcionando"
    }


# ==========================================
# DEBUG DE RUTAS
# ==========================================

@app.get("/debug-rutas")
def debug_rutas():
    return [
        {
            "path": ruta.path,
            "methods": list(ruta.methods)
        }
        for ruta in app.routes
    ]