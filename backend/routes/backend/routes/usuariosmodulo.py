from fastapi import APIRouter

from models.usuario_model import UsuarioCreate
from procedures.usuariosmodulo import (
    obtener_usuarios,
    crear_usuario
)

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"]
)


@router.get(
    "",
    summary="Listar Usuarios",
    description="Obtiene todos los usuarios registrados."
)
def listar_usuarios():
    return obtener_usuarios()


@router.post(
    "",
    summary="Nuevo Usuario",
    description="Crea un nuevo usuario."
)
def nuevo_usuario(datos: UsuarioCreate):
    return crear_usuario(
        datos.nombre,
        datos.usuario,
        datos.contrasena,
        datos.rol
    )