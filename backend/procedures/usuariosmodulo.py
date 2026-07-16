from fastapi import HTTPException
from mysql.connector import Error
from passlib.hash import bcrypt

from database.conexion import get_connection


ROLES_VALIDOS = [
    "ADMINISTRADOR",
    "TECNICO"
]


def obtener_usuarios():
    """
    Obtiene únicamente los usuarios activos.
    """
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)
        consulta_sql = """
            SELECT
                u.id_usuario,
                u.nombre,
                u.usuario,
                u.rol,
                u.id_estado,
                e.nombre AS estado
            FROM tbl_usuario u
            INNER JOIN tbl_estado e
                ON u.id_estado = e.id_estado
            WHERE u.id_estado = 1
            ORDER BY u.nombre ASC
        """
        cursor.execute(consulta_sql)
        return cursor.fetchall()
    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener usuarios: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def crear_usuario(
    nombre,
    usuario,
    contrasena,
    rol,
    id_estado
):
    """
    Crea un nuevo usuario.
    """
    nombre = nombre.strip()
    usuario = usuario.strip()
    rol = rol.upper()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre es obligatorio."
        )

    if not usuario:
        raise HTTPException(
            status_code=400,
            detail="El usuario es obligatorio."
        )

    if not contrasena:
        raise HTTPException(
            status_code=400,
            detail="La contraseña es obligatoria."
        )

    if rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail="Rol inválido."
        )

    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        # Verificar usuario existente
        consulta_sql = """
            SELECT id_usuario
            FROM tbl_usuario
            WHERE usuario = %s
              AND id_estado = 1
        """
        cursor.execute(consulta_sql, (usuario,))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El usuario ya existe."
            )

        # Verificar estado
        consulta_sql = """
            SELECT id_estado
            FROM tbl_estado
            WHERE id_estado = %s
        """
        cursor.execute(consulta_sql, (id_estado,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El estado seleccionado no existe."
            )

        password_hash = bcrypt.hash(contrasena)

        # Cerramos el cursor anterior antes de abrir uno nuevo sin diccionario
        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            INSERT INTO tbl_usuario
            (
                nombre,
                usuario,
                contrasena,
                rol,
                id_estado
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """
        cursor.execute(
            consulta_sql,
            (
                nombre,
                usuario,
                password_hash,
                rol,
                id_estado
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
            detail=f"Error al crear usuario: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close() 


# Se corrigió la indentación de esta función para que esté a nivel global
def actualizar_usuario(
    id_usuario,
    nombre,
    usuario,
    rol,
    id_estado
):
    """
    Actualiza un usuario.
    """
    nombre = nombre.strip()
    usuario = usuario.strip()
    rol = rol.upper()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre es obligatorio."
        )

    if not usuario:
        raise HTTPException(
            status_code=400,
            detail="El usuario es obligatorio."
        )

    if rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail="Rol inválido."
        )

    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista el usuario
        consulta_sql = """
            SELECT id_usuario
            FROM tbl_usuario
            WHERE id_usuario = %s
              AND id_estado = 1
        """
        cursor.execute(consulta_sql, (id_usuario,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe."
            )

        # Verificar usuario duplicado
        consulta_sql = """
            SELECT id_usuario
            FROM tbl_usuario
            WHERE usuario = %s
              AND id_usuario <> %s
              AND id_estado = 1
        """
        cursor.execute(consulta_sql, (usuario, id_usuario))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El usuario ya existe."
            )

        # Verificar estado
        consulta_sql = """
            SELECT id_estado
            FROM tbl_estado
            WHERE id_estado = %s
        """
        cursor.execute(consulta_sql, (id_estado,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El estado seleccionado no existe."
            )

        # Cerramos el cursor con diccionario antes de abrir uno nuevo estándar
        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_usuario
            SET
                nombre = %s,
                usuario = %s,
                rol = %s,
                id_estado = %s
            WHERE id_usuario = %s
        """
        cursor.execute(
            consulta_sql,
            (
                nombre,
                usuario,
                rol,
                id_estado,
                id_usuario
            )
        )
        conexion.commit()

        return {
            "mensaje": "Usuario actualizado correctamente."
        }
    except HTTPException:
        raise
    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar usuario: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def eliminar_usuario(id_usuario):
    """
    Desactiva un usuario (eliminación lógica).
    """
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT id_usuario
            FROM tbl_usuario
            WHERE id_usuario = %s
              AND id_estado = 1
        """
        cursor.execute(consulta_sql, (id_usuario,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe."
            )

        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_usuario
            SET id_estado = 2
            WHERE id_usuario = %s
        """
        cursor.execute(consulta_sql, (id_usuario,))
        conexion.commit()

        return {
            "mensaje": "Usuario desactivado correctamente."
        }
    except HTTPException:
        raise
    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar usuario: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def cambiar_password(id_usuario, contrasena):
    """
    Cambia la contraseña de un usuario.
    """
    contrasena = contrasena.strip()

    if not contrasena:
        raise HTTPException(
            status_code=400,
            detail="La contraseña es obligatoria."
        )

    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT id_usuario
            FROM tbl_usuario
            WHERE id_usuario = %s
              AND id_estado = 1
        """
        cursor.execute(consulta_sql, (id_usuario,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe."
            )

        password_hash = bcrypt.hash(contrasena)

        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_usuario
            SET contrasena = %s
            WHERE id_usuario = %s
        """
        cursor.execute(consulta_sql, (password_hash, id_usuario))
        conexion.commit()

        return {
            "mensaje": "Contraseña actualizada correctamente."
        }
    except HTTPException:
        raise
    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar contraseña: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()