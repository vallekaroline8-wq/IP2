from fastapi import APIRouter

from models.usuario_model import (
    UsuarioCreate,
    UsuarioUpdate,
    PasswordUpdate,
    UsuarioEstado
)

from procedures.usuariosmodulo import (
    obtener_usuarios,
    crear_usuario,
    actualizar_usuario,
    eliminar_usuario,
    cambiar_password,
    cambiar_estado_usuario
)

router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios"]
)


@router.get(
    "",
    summary="Listar Usuarios",
    description="Obtiene únicamente los usuarios activos."
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
        datos.rol,
        datos.id_estado
    )


@router.put(
    "/{id_usuario}",
    summary="Editar Usuario",
    description="Actualiza la información de un usuario."
)
def editar_usuario(
    id_usuario: int,
    datos: UsuarioUpdate
):
    return actualizar_usuario(
        id_usuario,
        datos.nombre,
        datos.usuario,
        datos.rol,
        datos.id_estado
    )


@router.put(
    "/{id_usuario}/password",
    summary="Cambiar Contraseña",
    description="Actualiza la contraseña de un usuario."
)
def actualizar_password(
    id_usuario: int,
    datos: PasswordUpdate
):
    return cambiar_password(
        id_usuario,
        datos.contrasena
    )


@router.put(
    "/{id_usuario}/estado",
    summary="Cambiar Estado",
    description="Activa o desactiva un usuario."
)
def actualizar_estado(
    id_usuario: int,
    datos: UsuarioEstado
):
    return cambiar_estado_usuario(
        id_usuario,
        datos.id_estado
    )


@router.delete(
    "/{id_usuario}",
    summary="Desactivar Usuario",
    description="Realiza una eliminación lógica cambiando el estado del usuario a INACTIVO."
)
def borrar_usuario(id_usuario: int):
    return eliminar_usuario(id_usuario)