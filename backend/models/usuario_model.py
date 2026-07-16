from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    nombre: str
    usuario: str
    contrasena: str
    rol: str
    id_estado: int


class UsuarioUpdate(BaseModel):
    nombre: str
    usuario: str
    rol: str
    id_estado: int


class PasswordUpdate(BaseModel):
    contrasena: str