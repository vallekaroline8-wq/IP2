from fastapi import APIRouter
from procedures.asignaciones import obtener_equipos

router = APIRouter(
    prefix="/api/asignaciones",
    tags=["Asignaciones"]
)


@router.get("/equipos")
def listar_equipos():
    return obtener_equipos()