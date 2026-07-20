from fastapi import APIRouter, Query

from models.asignacion_model import AsignacionCreate
from procedures.asignaciones import (
    obtener_asignaciones,
    crear_asignacion,
    liberar_asignacion
)

router = APIRouter(
    prefix="/api/asignaciones",
    tags=["Asignaciones"]
)


@router.get(
    "",
    summary="Listar Asignaciones",
    description="Obtiene las asignaciones de IP paginadas."
)
def listar_asignaciones(page: int = Query(1, ge=1)):
    return obtener_asignaciones(page)


@router.post(
    "",
    summary="Crear Asignación",
    description="Asigna una IP a un equipo."
)
def nueva_asignacion(datos: AsignacionCreate):
    return crear_asignacion(
        datos.equipo_id,
        datos.ip_id
    )


@router.post(
    "/{id_asignacion}/liberar",
    summary="Liberar Asignación",
    description="Libera una IP asignada."
)
def liberar(id_asignacion: int):
    return liberar_asignacion(id_asignacion)
