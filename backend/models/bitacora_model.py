from pydantic import BaseModel


class BitacoraCreate(BaseModel):
    id_usuario: int
    accion: str
    tabla_afectada: str
    registro_id: int
    detalle: str