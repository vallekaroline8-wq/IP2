from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models.login_model import LoginRequest
from procedures.usuarios import login_usuario, obtener_usuario_por_id
from auth import verificar_password, crear_token, verificar_token

router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"]
)

security = HTTPBearer(auto_error=False)


@router.post("/login")
def login(datos: LoginRequest):

    usuario = login_usuario(datos.username)

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    if usuario["estado"] != "ACTIVO":
        raise HTTPException(
            status_code=401,
            detail="Usuario inactivo"
        )

    if not verificar_password(datos.password, usuario["contrasena"]):
        raise HTTPException(
            status_code=401,
            detail="Contraseña incorrecta"
        )

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


@router.get("/me")
def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(security)
):

    if credenciales is None:
        raise HTTPException(
            status_code=401,
            detail="No se recibió el token de autenticación."
        )

    token = credenciales.credentials

    payload = verificar_token(token)

    usuario = obtener_usuario_por_id(payload["id_usuario"])

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return {
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "usuario": usuario["usuario"],
        "rol": usuario["rol"]
    }


@router.post("/logout")
def logout():

    return {
        "mensaje": "Sesión cerrada correctamente"
    }