from fastapi import APIRouter
from procedures.equipo_procedure import obtener_equipos

router = APIRouter(
    prefix="/equipos",
    tags=["Equipos"]
)


@router.get("/")
def listar_equipos():
    return obtener_equipos()