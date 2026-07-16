from fastapi import APIRouter

from models.seccion_model import SeccionCreate
from procedures.secciones import (
    obtener_secciones,
    crear_seccion,
    actualizar_seccion,
    eliminar_seccion
)

router = APIRouter(
    prefix="/api/secciones",
    tags=["Secciones"]
)


@router.get(
    "",
    summary="Listar Secciones",
    description="Obtiene únicamente las secciones activas."
)
def listar_secciones():
    return obtener_secciones()


@router.post(
    "",
    summary="Nueva Sección",
    description="Crea una nueva sección."
)
def nueva_seccion(datos: SeccionCreate):
    return crear_seccion(
        datos.nombre,
        datos.id_departamento
    )


@router.put(
    "/{id_seccion}",
    summary="Editar Sección",
    description="Actualiza una sección existente."
)
def editar_seccion(
    id_seccion: int,
    datos: SeccionCreate
):
    return actualizar_seccion(
        id_seccion,
        datos.nombre,
        datos.id_departamento
    )


@router.delete(
    "/{id_seccion}",
    summary="Desactivar Sección",
    description="Realiza una eliminación lógica cambiando el estado de la sección a INACTIVO."
)
def borrar_seccion(id_seccion: int):
    return eliminar_seccion(id_seccion)