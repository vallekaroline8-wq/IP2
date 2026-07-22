from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router
from routes.dashboard import router as dashboard_router
from routes.departamentos import router as departamentos_router
from routes.segmentos import router as segmentos_router
from routes.usuariosmodulo import router as usuarios_router
from routes.ips import router as ips_router
from routes.equipos import router as equipos_router
from routes.tipo_dispositivo import router as tipo_dispositivo_router
from routes.export_equipos import router as export_equipos_router
from routes.bitacora import router as bitacora_router
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
app.include_router(segmentos_router)
app.include_router(usuarios_router)
app.include_router(ips_router)
app.include_router(equipos_router)
app.include_router(tipo_dispositivo_router)
app.include_router(export_equipos_router)
app.include_router(bitacora_router)
app.include_router(asignaciones_router)

@app.get("/")
def inicio():
    return {
        "mensaje": "SIGIP Backend MySQL funcionando"
    }