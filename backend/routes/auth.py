from fastapi import APIRouter, HTTPException

from models.login_model import LoginRequest
from procedures.usuarios import login_usuario
from auth import verificar_password, crear_token

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/login")
def login(datos: LoginRequest):

    usuario = login_usuario(datos.username)

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if usuario["estado"] != "ACTIVO":
        raise HTTPException(status_code=401, detail="Usuario inactivo")

    if not verificar_password(datos.password, usuario["contrasena"]):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token = crear_token(usuario)

    return {
        "token": token,
        "user": {
            "id_usuario": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "usuario": usuario["usuario"],
            "rol": usuario["rol"]
        }
    }