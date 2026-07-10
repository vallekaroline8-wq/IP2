import bcrypt
import jwt
import os
from datetime import datetime, timedelta

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"


def verificar_password(password, password_hash):
    return bcrypt.checkpw(
        password.encode(),
        password_hash.encode()
    )


def crear_token(usuario):

    payload = {
        "id_usuario": usuario["id_usuario"],
        "usuario": usuario["usuario"],
        "rol": usuario["rol"],
        "exp": datetime.utcnow() + timedelta(hours=8)
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)