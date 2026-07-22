from pydantic import BaseModel, Field
from typing import Optional


class EquipoCreate(BaseModel):
    id_tipo: int = Field(..., gt=0)
    id_departamento: int = Field(..., gt=0)

    nombre_equipo: str = Field(..., min_length=1, max_length=100)

    marca: Optional[str] = Field(default=None, max_length=100)
    modelo: Optional[str] = Field(default=None, max_length=100)


class EquipoUpdate(BaseModel):
    id_tipo: int = Field(..., gt=0)
    id_departamento: int = Field(..., gt=0)

    nombre_equipo: str = Field(..., min_length=1, max_length=100)

    marca: Optional[str] = Field(default=None, max_length=100)
    modelo: Optional[str] = Field(default=None, max_length=100)


class EstadoEquipo(BaseModel):
    id_estado: int = Field(..., gt=0)