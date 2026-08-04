from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth import verificar_token
from procedures.usuarios import obtener_usuario_por_id

security = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Obtiene el usuario autenticado a partir del JWT.
    Puede reutilizarse en cualquier ruta protegida.
    """

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
            detail="Usuario no encontrado."
        )

    return usuario