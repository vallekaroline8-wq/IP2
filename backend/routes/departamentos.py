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


@router.get("")
def listar_departamentos():
    """
    Obtiene todos los departamentos.
    """
    return obtener_departamentos()


@router.post("")
def nuevo_departamento(datos: DepartamentoCreate):
    """
    Crea un nuevo departamento.
    """
    return crear_departamento(datos.nombre)


@router.put("/{id_departamento}")
def editar_departamento(
    id_departamento: int,
    datos: DepartamentoCreate
):
    """
    Actualiza un departamento.
    """
    return actualizar_departamento(
        id_departamento,
        datos.nombre
    )


@router.delete("/{id_departamento}")
def borrar_departamento(id_departamento: int):
    """
    Elimina un departamento.
    """
    return eliminar_departamento(id_departamento)