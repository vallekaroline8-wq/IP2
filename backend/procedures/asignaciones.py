from fastapi import HTTPException
from mysql.connector import Error

from database.conexion import get_connection


# ==========================================
# LISTAR ASIGNACIONES
# ==========================================

def obtener_asignaciones(page: int = 1):
    """
    Obtiene el listado paginado de asignaciones.
    """

    if page < 1:
        page = 1

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        page_size = 10
        offset = (page - 1) * page_size

        consulta_sql = """
            SELECT
                ai.id_asignacion,
                ip.direccion_ip,
                e.nombre_equipo,
                ai.fecha_asignacion,
                ai.fecha_liberacion,
                ai.estado_asignacion
            FROM tbl_asignacion_ip ai
            INNER JOIN tbl_ip ip
                ON ip.id_ip = ai.id_ip
            INNER JOIN tbl_equipo e
                ON e.id_equipo = ai.id_equipo
            ORDER BY ai.id_asignacion DESC
            LIMIT %s OFFSET %s
        """

        cursor.execute(
            consulta_sql,
            (
                page_size,
                offset
            )
        )

        items = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM tbl_asignacion_ip
        """)

        total = cursor.fetchone()["total"]

        pages = (total + page_size - 1) // page_size

        return {
            "items": items,
            "pages": pages,
            "total": total
        }

    except Error as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener asignaciones: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()


# ==========================================
# COMBO DE EQUIPOS
# ==========================================

def obtener_equipos():
    """
    Obtiene los equipos activos.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                id_equipo AS id,
                nombre_equipo AS nombre
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


# ==========================================
# COMBO DE SEGMENTOS
# ==========================================

def obtener_segmentos():
    """
    Obtiene los segmentos activos.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                id_segmento AS id,
                nombre
            FROM tbl_segmento
            WHERE id_estado = 1
            ORDER BY nombre ASC
        """

        cursor.execute(consulta_sql)

        return cursor.fetchall()

    except Error as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener segmentos: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()
