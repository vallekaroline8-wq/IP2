from fastapi import HTTPException
from mysql.connector import Error

from database.conexion import get_connection


def obtener_asignaciones(page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                a.id_asignacion AS id,
                ip.direccion AS ip_direccion,
                eq.nombre AS equipo_nombre,
                a.fecha_asignacion,
                a.fecha_liberacion,
                a.activo
            FROM tbl_asignacion_ip a
            LEFT JOIN tbl_ip ip ON ip.id_ip = a.id_ip
            LEFT JOIN tbl_equipo eq ON eq.id_equipo = a.id_equipo
            ORDER BY a.fecha_asignacion DESC
            LIMIT %s OFFSET %s
        """

        cursor.execute(consulta_sql, (limit, offset))
        items = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) AS total FROM tbl_asignacion_ip")
        total = cursor.fetchone()["total"]

        return {
            "items": items,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "total": total
        }

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener asignaciones: {str(e)}"
        )

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


def crear_asignacion(equipo_id: int, ip_id: int):
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            "SELECT id_ip, estado FROM tbl_ip WHERE id_ip = %s",
            (ip_id,)
        )
        ip = cursor.fetchone()

        if not ip:
            raise HTTPException(status_code=404, detail="IP no encontrada")

        if ip["estado"] != "disponible":
            raise HTTPException(status_code=400, detail="La IP no está disponible")

        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_equipo FROM tbl_equipo WHERE id_equipo = %s AND id_estado = 1",
            (equipo_id,)
        )
        equipo = cursor.fetchone()

        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")

        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO tbl_asignacion_ip (id_equipo, id_ip, fecha_asignacion, activo) VALUES (%s, %s, NOW(), 1)",
            (equipo_id, ip_id)
        )

        cursor.execute(
            "UPDATE tbl_ip SET estado = 'ocupada' WHERE id_ip = %s",
            (ip_id,)
        )

        conexion.commit()

        return {
            "mensaje": "IP asignada correctamente.",
            "id_asignacion": cursor.lastrowid
        }

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear asignación: {str(e)}")

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


def liberar_asignacion(id_asignacion: int):
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_ip, activo FROM tbl_asignacion_ip WHERE id_asignacion = %s",
            (id_asignacion,)
        )
        asignacion = cursor.fetchone()

        if not asignacion:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")

        if not asignacion["activo"]:
            raise HTTPException(status_code=400, detail="La asignación ya está liberada")

        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE tbl_asignacion_ip SET fecha_liberacion = NOW(), activo = 0 WHERE id_asignacion = %s",
            (id_asignacion,)
        )

        cursor.execute(
            "UPDATE tbl_ip SET estado = 'disponible' WHERE id_ip = %s",
            (asignacion["id_ip"],)
        )

        conexion.commit()

        return {"mensaje": "IP liberada correctamente."}

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al liberar asignación: {str(e)}")

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
