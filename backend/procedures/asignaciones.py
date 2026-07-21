from database.conexion import get_connection
from fastapi import HTTPException
from mysql.connector import Error


# ==========================================
# LISTAR ASIGNACIONES
# ==========================================

def obtener_asignaciones(page: int = 1):
    """
    Obtiene únicamente las direcciones IP que se encuentran asignadas.
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
                ai.id_estado,
                est.nombre AS estado,

                CASE
                    WHEN ai.id_estado = 4 THEN TRUE
                    ELSE FALSE
                END AS activo

            FROM tbl_asignacion_ip ai

            INNER JOIN tbl_ip ip
                ON ai.id_ip = ip.id_ip

            INNER JOIN tbl_equipo e
                ON ai.id_equipo = e.id_equipo

            INNER JOIN tbl_estado est
                ON ai.id_estado = est.id_estado

            WHERE ai.id_estado = 4

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
            WHERE id_estado = 4
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
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Buscar asignación
        cursor.execute("""
            SELECT
                id_ip,
                id_estado
            FROM tbl_asignacion_ip
            WHERE id_asignacion = %s
        """, (id_asignacion,))

        asignacion = cursor.fetchone()

        if not asignacion:
            raise HTTPException(
                status_code=404,
                detail="La asignación no existe."
            )

        # Verificar si ya está liberada
        if asignacion["id_estado"] == 3:
            raise HTTPException(
                status_code=400,
                detail="La asignación ya fue liberada."
            )

        # Actualizar asignación
        cursor.execute("""
            UPDATE tbl_asignacion_ip
            SET
                id_estado = 3,
                fecha_liberacion = NOW()
            WHERE id_asignacion = %s
        """, (id_asignacion,))

        # Actualizar IP
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

# ==========================================
# IPS DISPONIBLES
# ==========================================

def obtener_ips_disponibles(id_segmento):
    """
    Obtiene las IP disponibles de un segmento.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        print("ID SEGMENTO RECIBIDO:", id_segmento)

        cursor.execute("""
            SELECT
                id_ip AS id,
                direccion_ip AS direccion
            FROM tbl_ip
            WHERE id_segmento = %s
              AND id_estado = 3
            ORDER BY direccion_ip
        """, (id_segmento,))

        return cursor.fetchall()

    except Error as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener las IP disponibles: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()

# ==========================================
# ASIGNAR DIRECCIÓN IP
# ==========================================

def asignar_ip(id_ip: int, id_equipo: int, id_usuario: int):
    """
    Asigna una dirección IP a un equipo.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # ======================================
        # Verificar que la IP exista
        # ======================================

        cursor.execute("""
            SELECT
                id_ip,
                id_estado
            FROM tbl_ip
            WHERE id_ip = %s
        """, (id_ip,))

        ip = cursor.fetchone()

        if not ip:
            raise HTTPException(
                status_code=404,
                detail="La dirección IP no existe."
            )

        # Debe estar DISPONIBLE
        if ip["id_estado"] != 3:
            raise HTTPException(
                status_code=400,
                detail="La dirección IP no está disponible."
            )

        # ======================================
        # Verificar equipo
        # ======================================

        cursor.execute("""
            SELECT id_equipo
            FROM tbl_equipo
            WHERE id_equipo = %s
        """, (id_equipo,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="El equipo no existe."
            )

        # ======================================
        # Verificar usuario
        # ======================================

        cursor.execute("""
            SELECT id_usuario
            FROM tbl_usuario
            WHERE id_usuario = %s
        """, (id_usuario,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe."
            )

        # ======================================
        # Registrar asignación
        # ======================================

        cursor.execute("""
            INSERT INTO tbl_asignacion_ip
            (
                id_ip,
                id_equipo,
                id_usuario,
                fecha_asignacion,
                id_estado
            )
            VALUES
            (
                %s,
                %s,
                %s,
                NOW(),
                %s
            )
        """, (
            id_ip,
            id_equipo,
            id_usuario,
            4
        ))

        # ======================================
        # Cambiar estado de la IP
        # ======================================

        cursor.execute("""
            UPDATE tbl_ip
            SET id_estado = 4
            WHERE id_ip = %s
        """, (id_ip,))

        conexion.commit()

        return {
            "mensaje": "Dirección IP asignada correctamente."
        }

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al asignar la dirección IP: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()
    """
    Asigna una dirección IP a un equipo.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # ======================================
        # Verificar que la IP exista
        # ======================================

        cursor.execute("""
            SELECT
                id_ip,
                id_estado
            FROM tbl_ip
            WHERE id_ip = %s
        """, (id_ip,))

        ip = cursor.fetchone()

        if not ip:
            raise HTTPException(
                status_code=404,
                detail="La dirección IP no existe."
            )

        # id_estado = 3 -> DISPONIBLE
        if ip["id_estado"] != 3:
            raise HTTPException(
                status_code=400,
                detail="La dirección IP no está disponible."
            )

        # ======================================
        # Verificar que exista el equipo
        # ======================================

        cursor.execute("""
            SELECT id_equipo
            FROM tbl_equipo
            WHERE id_equipo = %s
        """, (id_equipo,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="El equipo no existe."
            )

        # ======================================
        # Verificar que exista el usuario
        # ======================================

        cursor.execute("""
            SELECT id_usuario
            FROM tbl_usuario
            WHERE id_usuario = %s
        """, (id_usuario,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe."
            )

        # ======================================
        # Registrar asignación
        # ======================================

        cursor.execute("""
            INSERT INTO tbl_asignacion_ip
            (
                id_ip,
                id_equipo,
                id_usuario,
                fecha_asignacion,
                estado_asignacion
            )
            VALUES
            (
                %s,
                %s,
                %s,
                NOW(),
                'ACTIVA'
            )
        """, (
            id_ip,
            id_equipo,
            id_usuario
        ))

        # ======================================
        # Cambiar estado de la IP
        # id_estado = 4 -> ASIGNADA
        # ======================================

        cursor.execute("""
            UPDATE tbl_ip
            SET id_estado = 4
            WHERE id_ip = %s
        """, (id_ip,))

        conexion.commit()

        return {
            "mensaje": "Dirección IP asignada correctamente."
        }

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al asignar la dirección IP: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()