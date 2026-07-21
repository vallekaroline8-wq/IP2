from pydantic import BaseModel


class AsignacionCreate(BaseModel):
    equipo_id: int
    ip_id: int
