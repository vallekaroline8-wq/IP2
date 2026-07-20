from pydantic import BaseModel


class SegmentoCreate(BaseModel):
    nombre: str
    direccion_red: str
    mascara: str
    gateway: str = ""
