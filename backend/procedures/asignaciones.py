from database.conexion import get_connection
from fastapi import HTTPException
from mysql.connector import Error


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
                ai.id_asignacion AS id,
                ip.direccion_ip AS ip_direccion,
                e.nombre_equipo AS equipo_nombre,
                ai.fecha_asignacion,
                ai.fecha_liberacion,
                ai.estado_asignacion,

                CASE
                    WHEN ai.estado_asignacion = 'ACTIVA' THEN TRUE
                    ELSE FALSE
                END AS activo

            FROM tbl_asignacion_ip ai

            INNER JOIN tbl_ip ip
                ON ai.id_ip = ip.id_ip

            INNER JOIN tbl_equipo e
                ON ai.id_equipo = e.id_equipo

            ORDER BY ai.id_asignacion DESC

            LIMIT %s, %s
        """

        cursor.execute(
            consulta_sql,
            (
                offset,
                page_size
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
# LIBERAR ASIGNACIÓN DE IP
# ==========================================

def liberar_asignacion(id_asignacion: int):
    """
    Libera una dirección IP asignada.
    Cambia el estado de la asignación a LIBERADA
    y el estado de la IP a DISPONIBLE.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # ======================================
        # Verificar que exista la asignación
        # ======================================

        cursor.execute("""
            SELECT
                id_asignacion,
                id_ip,
                estado_asignacion
            FROM tbl_asignacion_ip
            WHERE id_asignacion = %s
        """, (id_asignacion,))

        asignacion = cursor.fetchone()

        if not asignacion:
            raise HTTPException(
                status_code=404,
                detail="La asignación no existe."
            )

        # ======================================
        # Verificar si ya fue liberada
        # ======================================

        if asignacion["estado_asignacion"] == "LIBERADA":
            raise HTTPException(
                status_code=400,
                detail="La dirección IP ya fue liberada."
            )

        # ======================================
        # Actualizar asignación
        # ======================================

        cursor.execute("""
            UPDATE tbl_asignacion_ip
            SET
                estado_asignacion = 'LIBERADA',
                fecha_liberacion = NOW()
            WHERE id_asignacion = %s
        """, (id_asignacion,))

        # ======================================
        # Cambiar la IP a DISPONIBLE
        # id_estado = 3
        # ======================================

        cursor.execute("""
            UPDATE tbl_ip
            SET id_estado = 3
            WHERE id_ip = %s
        """, (asignacion["id_ip"],))

        conexion.commit()

        return {
            "mensaje": "Dirección IP liberada correctamente."
        }

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al liberar la dirección IP: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()

# ==========================================
# COMBO EQUIPOS
# ==========================================

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

        return cursor.fetchall()

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        cursor.close()
        conexion.close()


# ==========================================
# COMBO SEGMENTOS
# ==========================================

def obtener_segmentos():

    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_segmento AS id,
                nombre
            FROM tbl_segmento
            WHERE id_estado = 1
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
