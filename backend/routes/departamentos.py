from fastapi import APIRouter

from models.departamento_model import DepartamentoCreate

from procedures.departamentos import (
    obtener_departamentos,
    crear_departamento,
    actualizar_departamento,
    eliminar_departamento
)

router = APIRouter(
    prefix="/api/departamentos",
    tags=["Departamentos"]
)


@router.get(
    "",
    summary="Listar Departamentos",
    description="Obtiene únicamente los departamentos activos."
)
def listar_departamentos():
    return obtener_departamentos()


@router.post(
    "",
    summary="Nuevo Departamento",
    description="Crea un nuevo departamento."
)
def nuevo_departamento(datos: DepartamentoCreate):
    return crear_departamento(datos.nombre)


@router.put(
    "/{id_departamento}",
    summary="Editar Departamento",
    description="Actualiza el nombre de un departamento."
)
def editar_departamento(
    id_departamento: int,
    datos: DepartamentoCreate
):
    return actualizar_departamento(
        id_departamento,
        datos.nombre
    )


@router.delete(
    "/{id_departamento}",
    summary="Desactivar Departamento",
    description="Realiza una eliminación lógica cambiando el estado del departamento a INACTIVO."
)
def borrar_departamento(id_departamento: int):
    return eliminar_departamento(id_departamento)