from fastapi import HTTPException
from mysql.connector import Error

from database.conexion import get_connection


def obtener_departamentos():
    """
    Obtiene todos los departamentos ordenados alfabéticamente.
    """

    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                id_departamento,
                nombre
            FROM tbl_departamento
            ORDER BY nombre ASC
        """

        cursor.execute(consulta_sql)

        return cursor.fetchall()

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener departamentos: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def crear_departamento(nombre):
    """
    Crea un nuevo departamento.
    """

    nombre = nombre.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre del departamento es obligatorio."
        )

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar si ya existe
        consulta_sql = """
            SELECT id_departamento
            FROM tbl_departamento
            WHERE nombre = %s
        """

        cursor.execute(consulta_sql, (nombre,))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un departamento con ese nombre."
            )

        cursor = conexion.cursor()

        consulta_sql = """
            INSERT INTO tbl_departamento(nombre)
            VALUES(%s)
        """

        cursor.execute(consulta_sql, (nombre,))
        conexion.commit()

        return {
            "mensaje": "Departamento creado correctamente.",
            "id_departamento": cursor.lastrowid
        }

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al crear departamento: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def actualizar_departamento(id_departamento, nombre):
    """
    Actualiza el nombre de un departamento.
    """

    nombre = nombre.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre del departamento es obligatorio."
        )

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista
        consulta_sql = """
            SELECT id_departamento
            FROM tbl_departamento
            WHERE id_departamento = %s
        """

        cursor.execute(consulta_sql, (id_departamento,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Departamento no encontrado."
            )

        # Verificar nombre duplicado
        consulta_sql = """
            SELECT id_departamento
            FROM tbl_departamento
            WHERE nombre = %s
            AND id_departamento <> %s
        """

        cursor.execute(consulta_sql, (nombre, id_departamento))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un departamento con ese nombre."
            )

        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_departamento
            SET nombre = %s
            WHERE id_departamento = %s
        """

        cursor.execute(consulta_sql, (nombre, id_departamento))
        conexion.commit()

        return {
            "mensaje": "Departamento actualizado correctamente."
        }

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar departamento: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def eliminar_departamento(id_departamento):
    """
    Elimina un departamento.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista
        consulta_sql = """
            SELECT id_departamento
            FROM tbl_departamento
            WHERE id_departamento = %s
        """

        cursor.execute(consulta_sql, (id_departamento,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Departamento no encontrado."
            )

        cursor = conexion.cursor()

        consulta_sql = """
            DELETE FROM tbl_departamento
            WHERE id_departamento = %s
        """

        cursor.execute(consulta_sql, (id_departamento,))
        conexion.commit()

        return {
            "mensaje": "Departamento eliminado correctamente."
        }

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar departamento: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()