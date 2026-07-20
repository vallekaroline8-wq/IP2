from database.conexion import get_connection
from fastapi import HTTPException
from mysql.connector import Error


def obtener_equipos():
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_equipo AS id,
                nombre_equipo AS nombre
            FROM tbl_equipo
            WHERE id_estado = 1
            ORDER BY nombre_equipo
        """)

        equipos = cursor.fetchall()

        return equipos

    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conexion.close()