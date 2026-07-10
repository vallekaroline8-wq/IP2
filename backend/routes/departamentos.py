from fastapi import APIRouter

from models.departamento_model import DepartamentoCreate
from procedures.departamentos import (
    obtener_departamentos,
    crear_departamento
)

router = APIRouter(
    prefix="/api/departamentos",
    tags=["Departamentos"]
)


@router.get("")
def listar_departamentos():
    return obtener_departamentos()


@router.post("")
def nuevo_departamento(datos: DepartamentoCreate):
    return crear_departamento(datos.nombre)