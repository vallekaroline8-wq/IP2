from fastapi import APIRouter, Query

from models.segmento_model import SegmentoCreate
from procedures.segmentos import (
    obtener_segmentos,
    crear_segmento,
    actualizar_segmento,
    eliminar_segmento
)

router = APIRouter(
    prefix="/api/segmentos",
    tags=["Segmentos"]
)


@router.get(
    "",
    summary="Listar Segmentos",
    description="Obtiene los segmentos desde tbl_segmento."
)
def listar_segmentos(
    all: bool = Query(False, description="Incluye todos los segmentos cuando es true"),
    search: str = Query("", description="Texto a buscar en el nombre del segmento")
):
    return obtener_segmentos(all, search)


@router.post(
    "",
    summary="Nuevo Segmento",
    description="Crea un nuevo segmento en tbl_segmento."
)
def nuevo_segmento(datos: SegmentoCreate):
    return crear_segmento(
        datos.nombre,
        datos.direccion_red,
        datos.mascara,
        datos.gateway
    )


@router.put(
    "/{id_segmento}",
    summary="Editar Segmento",
    description="Actualiza un segmento existente."
)
def editar_segmento(
    id_segmento: int,
    datos: SegmentoCreate
):
    return actualizar_segmento(
        id_segmento,
        datos.nombre,
        datos.direccion_red,
        datos.mascara,
        datos.gateway
    )


@router.delete(
    "/{id_segmento}",
    summary="Eliminar Segmento",
    description="Realiza una eliminación lógica del segmento."
)
def borrar_segmento(id_segmento: int):
    return eliminar_segmento(id_segmento)
