from fastapi import HTTPException
from mysql.connector import Error
from database.conexion import get_connection

def obtener_bitacora(page: int = 1, limit: int = 20, search: str = ""):
    offset = (page - 1) * limit
    conexion = get_connection()
    cursor = None

    try:
        if conexion is None:
            raise HTTPException(status_code=500, detail="No fue posible conectar a la base de datos")

        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                b.id_bitacora AS id,
                b.fecha,
                COALESCE(u.nombre, u.usuario, 'Sistema') AS usuario,
                b.accion,
                b.tabla_afectada AS modulo,
                b.detalle
            FROM tbl_bitacora b
            LEFT JOIN tbl_usuario u ON u.id_usuario = b.id_usuario
        """

        params = []
        conditions = []

        if search.strip():
            term = f"%{search.strip()}%"
            conditions.append("(b.accion LIKE %s OR b.tabla_afectada LIKE %s OR b.detalle LIKE %s OR u.nombre LIKE %s OR u.usuario LIKE %s)")
            params.extend([term, term, term, term, term])

        if conditions:
            consulta_sql += " WHERE " + " AND ".join(conditions)

        consulta_sql += " ORDER BY b.fecha DESC LIMIT %s OFFSET %s"
        select_params = list(params)
        select_params.extend([limit, offset])

        cursor.execute(consulta_sql, tuple(select_params))
        items = cursor.fetchall()

        # Formatear fechas a string ISO para el frontend
        for item in items:
            if item.get("fecha"):
                item["fecha"] = str(item["fecha"])

        count_sql = "SELECT COUNT(*) AS total FROM tbl_bitacora b LEFT JOIN tbl_usuario u ON u.id_usuario = b.id_usuario"
        if conditions:
            count_sql += " WHERE " + " AND ".join(conditions)

        cursor.execute(count_sql, tuple(params))
        total = cursor.fetchone()["total"]

        return {
            "items": items,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "total": total
        }

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener bitácora: {str(e)}")
    finally:
        if conexion and conexion.is_connected() and cursor is not None:
            cursor.close()
            conexion.close()
