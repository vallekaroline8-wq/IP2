from fastapi import HTTPException
from mysql.connector import Error

from database.conexion import get_connection


def obtener_tipos_dispositivo():
    """
    Obtiene el catálogo de tipos de dispositivo.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                id_tipo,
                nombre
            FROM tbl_tipo_dispositivo
            ORDER BY nombre ASC
        """

        cursor.execute(consulta_sql)

        return cursor.fetchall()

    except Error as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tipos de dispositivo: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()