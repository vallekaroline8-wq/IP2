from pydantic import BaseModel

class DepartamentoCreate(BaseModel):
    nombre: str