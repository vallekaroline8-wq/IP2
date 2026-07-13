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
    description="Obtiene todas las secciones."
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
    description="Actualiza una sección."
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
    summary="Eliminar Sección",
    description="Elimina una sección."
)
def borrar_seccion(id_seccion: int):
    return eliminar_seccion(id_seccion)