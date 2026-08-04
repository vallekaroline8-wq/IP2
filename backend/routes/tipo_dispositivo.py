from fastapi import APIRouter

from procedures.tipo_dispositivo import (
    obtener_tipos_dispositivo
)

router = APIRouter(
    prefix="/api/tipo_dispositivo",
    tags=["Tipo de Dispositivo"]
)


@router.get(
    "",
    summary="Listar Tipos de Dispositivo",
    description="Obtiene el catálogo de tipos de dispositivo."
)
def listar_tipos_dispositivo():
    return obtener_tipos_dispositivo()