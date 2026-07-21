from fastapi import APIRouter, Query

from models.equipo_model import (
    EquipoCreate,
    EquipoUpdate
)

from procedures.equipos import (
    obtener_equipos,
    obtener_equipo,
    crear_equipo,
    actualizar_equipo,
    eliminar_equipo
)

router = APIRouter(
    prefix="/api/equipos",
    tags=["Equipos"]
)


@router.get(
    "",
    summary="Listar Equipos",
    description="Obtiene todos los equipos registrados."
)
def listar_equipos(
    search: str = Query(default="")
):
    return obtener_equipos(search)


@router.get(
    "/{id_equipo}",
    summary="Obtener Equipo",
    description="Obtiene un equipo por su ID."
)
def obtener_un_equipo(id_equipo: int):
    return obtener_equipo(id_equipo)


@router.post(
    "",
    summary="Crear Equipo",
    description="Registra un nuevo equipo."
)
def nuevo_equipo(datos: EquipoCreate):
    return crear_equipo(datos)


@router.put(
    "/{id_equipo}",
    summary="Actualizar Equipo",
    description="Actualiza la información de un equipo."
)
def editar_equipo(
    id_equipo: int,
    datos: EquipoUpdate
):
    return actualizar_equipo(
        id_equipo,
        datos
    )


@router.delete(
    "/{id_equipo}",
    summary="Eliminar Equipo",
    description="Realiza una eliminación lógica del equipo."
)
def borrar_equipo(id_equipo: int):
    return eliminar_equipo(id_equipo)