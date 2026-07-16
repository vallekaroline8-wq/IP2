from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    nombre: str
    usuario: str
    contrasena: str
    rol: str


class UsuarioUpdate(BaseModel):
    nombre: str
    usuario: str
    rol: str
    estado: str