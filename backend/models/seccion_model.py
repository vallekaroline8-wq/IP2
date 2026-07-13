from pydantic import BaseModel


class SeccionCreate(BaseModel):
    nombre: str
    id_departamento: int