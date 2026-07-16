from fastapi import HTTPException
from mysql.connector import Error
from passlib.hash import bcrypt

from database.conexion import get_connection


def obtener_usuarios():

    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_usuario,
                nombre,
                usuario,
                rol,
                estado
            FROM tbl_usuario
            ORDER BY nombre
        """)

        return cursor.fetchall()

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        cursor.close()
        conexion.close()


def crear_usuario(
    nombre,
    usuario,
    contrasena,
    rol
):

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id_usuario
            FROM tbl_usuario
            WHERE usuario=%s
            """,
            (usuario,)
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El usuario ya existe."
            )

        password_hash = bcrypt.hash(contrasena)

        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO tbl_usuario
            (
                nombre,
                usuario,
                contrasena,
                rol,
                estado
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'ACTIVO'
            )
            """,
            (
                nombre,
                usuario,
                password_hash,
                rol.upper()
            )
        )

        conexion.commit()

        return {
            "mensaje": "Usuario creado correctamente.",
            "id_usuario": cursor.lastrowid
        }

    except HTTPException:
        raise

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        cursor.close()
        conexion.close()