from fastapi import HTTPException
from mysql.connector import Error

from database.conexion import get_connection


def obtener_equipos():
    """
    Obtiene únicamente los equipos activos.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                id_equipo,
                nombre_equipo
            FROM tbl_equipo
            WHERE id_estado = 1
            ORDER BY nombre_equipo ASC
        """

        cursor.execute(consulta_sql)

        return cursor.fetchall()

    except Error as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener equipos: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()