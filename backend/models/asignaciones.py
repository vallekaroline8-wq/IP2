from pydantic import BaseModel

class AsignacionCreate(BaseModel):
    id_equipo: int
    id_ip: int


class ReasignacionCreate(BaseModel):
    id_equipo: int
    id_ip: int