import re

from fastapi import HTTPException
from mysql.connector import Error

from database.conexion import get_connection


def resolver_id_estado(estado: str) -> int:
    clave = str(estado).strip().lower()
    mapa = {
        "disponible": 3,
        "ocupada": 4,
        "reservada": 5,
        "asignada": 4,
        "reserva": 5,
    }
    if clave not in mapa:
        raise ValueError("Estado inválido")
    return mapa[clave]


def extraer_segmento_por_nombre(nombre: str | None) -> str | None:
    if not nombre:
        return None

    match = re.match(r"^\s*(\d+)\s*[-]?.*$", nombre)
    if match:
        return match.group(1)
    return None


def map_estado_frontend(estado_db: str | None) -> str:
    if not estado_db:
        return "desconocido"

    clave = str(estado_db).strip().upper()
    mapa = {
        "DISPONIBLE": "disponible",
        "ASIGNADA": "ocupada",
        "OCUPADA": "ocupada",
        "RESERVADA": "reservada",
        "ACTIVO": "disponible",
        "INACTIVO": "inactivo",
    }
    return mapa.get(clave, clave.lower())


def map_estado_db(estado: str | None) -> str | None:
    if estado is None:
        return None

    clave = str(estado).strip().lower()
    mapa = {
        "disponible": "DISPONIBLE",
        "ocupada": "ASIGNADA",
        "asignada": "ASIGNADA",
        "reservada": "RESERVADA",
        "reserva": "RESERVADA",
    }
    return mapa.get(clave, clave.upper())


def obtener_ips(page: int = 1, limit: int = 20, search: str = "", segmento_id: int | None = None, estado: str | None = None):
    offset = (page - 1) * limit
    conexion = get_connection()
    cursor = None

    try:
        if conexion is None:
            raise HTTPException(status_code=500, detail="No fue posible conectar a la base de datos")

        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                ip.id_ip AS id,
                ip.direccion_ip AS direccion,
                ip.id_segmento,
                seg.nombre AS segmento_nombre,
                ip.id_estado,
                est.nombre AS estado_db,
                (
                    SELECT eq.nombre_equipo
                    FROM tbl_asignacion_ip asig
                    LEFT JOIN tbl_equipo eq ON eq.id_equipo = asig.id_equipo
                    WHERE asig.id_ip = ip.id_ip
                      AND asig.estado_asignacion = 'ACTIVA'
                    ORDER BY asig.fecha_asignacion DESC
                    LIMIT 1
                ) AS equipo_nombre
            FROM tbl_ip ip
            LEFT JOIN tbl_segmento seg ON seg.id_segmento = ip.id_segmento AND seg.id_estado = 1
            LEFT JOIN tbl_estado est ON est.id_estado = ip.id_estado
            WHERE ip.id_estado IN (3, 4, 5)
        """

        params = []
        conditions = []

        if search.strip():
            conditions.append("ip.direccion_ip LIKE %s")
            params.append(f"%{search.strip()}%")

        if segmento_id is not None:
            cursor.execute(
                "SELECT nombre FROM tbl_segmento WHERE id_segmento = %s",
                (segmento_id,)
            )
            segmento = cursor.fetchone()
            third_octet = extraer_segmento_por_nombre(segmento.get("nombre") if segmento else None)
            if third_octet:
                conditions.append("(ip.id_segmento = %s OR SUBSTRING_INDEX(SUBSTRING_INDEX(ip.direccion_ip, '.', 3), '.', -1) = %s)")
                params.extend([segmento_id, third_octet])
            else:
                conditions.append("ip.id_segmento = %s")
                params.append(segmento_id)

        if estado is not None and estado != "all":
            db_estado = map_estado_db(estado)
            conditions.append("est.nombre = %s")
            params.append(db_estado)

        if conditions:
            consulta_sql += " AND " + " AND ".join(conditions)

        consulta_sql += " ORDER BY ip.direccion_ip ASC LIMIT %s OFFSET %s"
        select_params = list(params)
        select_params.extend([limit, offset])

        cursor.execute(consulta_sql, tuple(select_params))
        items = cursor.fetchall()

        count_sql = """
            SELECT COUNT(*) AS total
            FROM tbl_ip ip
            LEFT JOIN tbl_estado est ON est.id_estado = ip.id_estado
            WHERE ip.id_estado IN (3, 4, 5)
        """
        if conditions:
            count_sql += " AND " + " AND ".join(conditions)

        cursor.execute(count_sql, tuple(params))
        total = cursor.fetchone()["total"]

        for item in items:
            item["estado"] = map_estado_frontend(item.get("estado_db"))
            item["equipo_nombre"] = item.get("equipo_nombre") or None
            item.pop("estado_db", None)

        return {
            "items": items,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "total": total,
        }

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener IPs: {str(e)}")
    finally:
        if conexion and conexion.is_connected() and cursor is not None:
            cursor.close()
            conexion.close()


def actualizar_estado_ip(id_ip: int, estado: str):
    try:
        id_estado = resolver_id_estado(estado)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Estado inválido") from exc

    conexion = get_connection()
    cursor = None

    try:
        if conexion is None:
            raise HTTPException(status_code=500, detail="No fue posible conectar a la base de datos")

        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_ip FROM tbl_ip WHERE id_ip = %s", (id_ip,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="IP no encontrada")

        cursor.execute("UPDATE tbl_ip SET id_estado = %s WHERE id_ip = %s", (id_estado, id_ip))
        conexion.commit()

        return {"mensaje": "Estado actualizado correctamente."}

    except HTTPException:
        raise
    except Error as e:
        if conexion is not None:
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar estado: {str(e)}")
    finally:
        if conexion and conexion.is_connected() and cursor is not None:
            cursor.close()
            conexion.close()


def obtener_historial_ip(id_ip: int):
    conexion = get_connection()
    cursor = None

    try:
        if conexion is None:
            raise HTTPException(status_code=500, detail="No fue posible conectar a la base de datos")

        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                a.id_asignacion AS id,
                a.fecha_asignacion,
                a.fecha_liberacion,
                a.estado_asignacion,
                a.estado_asignacion = 'ACTIVA' AS activo,
                eq.nombre_equipo AS equipo_nombre
            FROM tbl_asignacion_ip a
            LEFT JOIN tbl_equipo eq ON eq.id_equipo = a.id_equipo
            WHERE a.id_ip = %s
            ORDER BY a.fecha_asignacion DESC
        """, (id_ip,))

        items = cursor.fetchall()
        for item in items:
            item["activo"] = bool(item.get("activo"))

        return {"items": items}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")
    finally:
        if conexion and conexion.is_connected() and cursor is not None:
            cursor.close()
            conexion.close()
