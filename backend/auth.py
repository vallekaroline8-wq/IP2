import os
import bcrypt
import hashlib
import jwt

from datetime import datetime, timedelta
from fastapi import HTTPException

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"


def verificar_password(password: str, password_hash: str) -> bool:
    """
    Verifica contraseñas almacenadas tanto en bcrypt como en SHA-256.
    """

    if not password_hash:
        return False

    try:
        # Hash bcrypt
        if password_hash.startswith("$2a$") or \
           password_hash.startswith("$2b$") or \
           password_hash.startswith("$2y$"):

            return bcrypt.checkpw(
                password.encode("utf-8"),
                password_hash.encode("utf-8")
            )

        # Hash SHA-256
        sha256 = hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

        return sha256 == password_hash

    except Exception:
        return False


def crear_token(usuario):

    payload = {
        "id_usuario": usuario["id_usuario"],
        "usuario": usuario["usuario"],
        "rol": usuario["rol"],
        "exp": datetime.utcnow() + timedelta(hours=8)
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def verificar_token(token: str):

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token expirado"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )