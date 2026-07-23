from fastapi import HTTPException
from mysql.connector import Error
from procedures.bitacoramodulo import registrar_bitacora


from database.conexion import get_connection


def obtener_segmentos(page: int = 1, limit: int = 10, all: bool = False, search: str = ""):
    """Obtiene los segmentos desde tbl_segmento con paginación e información de IPs."""
    
    offset = (page - 1) * limit
    conexion = get_connection()
    cursor = None

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                s.id_segmento,
                s.nombre,
                s.direccion_red,
                s.mascara,
                s.gateway,
                COUNT(i.id_ip) AS total_ips,
                COALESCE(SUM(CASE WHEN i.id_estado = 4 THEN 1 ELSE 0 END), 0) AS ocupadas,
                COALESCE(SUM(CASE WHEN i.id_estado = 3 THEN 1 ELSE 0 END), 0) AS disponibles
            FROM tbl_segmento s
            LEFT JOIN tbl_ip i ON i.id_segmento = s.id_segmento AND i.id_estado IN (3, 4, 5)
        """

        conditions = []
        params = []

        if not all:
            conditions.append("s.id_estado = 1")

        if search.strip():
            conditions.append("s.nombre LIKE %s")
            params.append(f"%{search.strip()}%")

        if conditions:
            consulta_sql += "\n            WHERE " + " AND ".join(conditions)

        consulta_sql += "\n            GROUP BY s.id_segmento, s.nombre, s.direccion_red, s.mascara, s.gateway"

        # Ordenar por el número del segmento (primeros números, luego alfabéticamente)
        # Extrae el primer número del nombre si existe
        consulta_sql += """
            ORDER BY 
                CASE 
                    WHEN s.nombre REGEXP '^[0-9]' THEN 0
                    ELSE 1
                END ASC,
                CAST(REGEXP_SUBSTR(s.nombre, '^[0-9]+') AS UNSIGNED) ASC,
                s.nombre ASC
        """
        
        # Agregar paginación
        consulta_sql += "\n            LIMIT %s OFFSET %s"
        select_params = list(params)
        select_params.extend([limit, offset])

        cursor.execute(consulta_sql, tuple(select_params))
        items = cursor.fetchall()

        for item in items:
            item["total_ips"] = int(item.get("total_ips") or 0)
            item["ocupadas"] = int(item.get("ocupadas") or 0)
            item["disponibles"] = int(item.get("disponibles") or 0)

        # Contar el total de registros
        count_sql = "SELECT COUNT(*) AS total FROM tbl_segmento s"
        if conditions:
            count_sql += "\n            WHERE " + " AND ".join(conditions)
        
        cursor.execute(count_sql, tuple(params))
        total = cursor.fetchone()["total"]

        return {
            "items": items,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "total": total,
        }

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener segmentos: {str(e)}"
        )

    finally:
        if conexion and conexion.is_connected() and cursor is not None:
            cursor.close()
            conexion.close()


def crear_segmento(nombre, direccion_red, mascara, gateway="", id_usuario_actual=None):
    nombre = nombre.strip()
    direccion_red = direccion_red.strip()
    mascara = mascara.strip()
    gateway = gateway.strip()

    if not nombre or not direccion_red or not mascara:
        raise HTTPException(
            status_code=400,
            detail="Nombre, dirección de red y máscara son obligatorios."
        )

    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT id_segmento
            FROM tbl_segmento
            WHERE nombre = %s
            AND id_estado = 1
        """

        cursor.execute(consulta_sql, (nombre,))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un segmento con ese nombre."
            )

        # Validar duplicado por dirección de red + máscara (solo activos)
        cursor.execute("""
            SELECT id_segmento
            FROM tbl_segmento
            WHERE direccion_red = %s
              AND mascara = %s
              AND id_estado = 1
        """, (direccion_red, mascara))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un segmento con esa dirección de red y máscara."
            )

        # Validar duplicado por gateway (si fue proporcionado) (solo activos)
        if gateway:
            cursor.execute("""
                SELECT id_segmento
                FROM tbl_segmento
                WHERE gateway = %s
                  AND id_estado = 1
            """, (gateway,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe un segmento con ese gateway."
                )
        # Si existe un registro inactivo con igual nombre/dirección+mascara/gateway, reactivar
        # Priorizar búsqueda por nombre, luego por direccion+mascara, luego por gateway
        cursor.execute("""
            SELECT id_segmento
            FROM tbl_segmento
            WHERE nombre = %s
              AND id_estado = 2
            LIMIT 1
        """, (nombre,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("""
                SELECT id_segmento
                FROM tbl_segmento
                WHERE direccion_red = %s
                  AND mascara = %s
                  AND id_estado = 2
                LIMIT 1
            """, (direccion_red, mascara))
            row = cursor.fetchone()

        if not row and gateway:
            cursor.execute("""
                SELECT id_segmento
                FROM tbl_segmento
                WHERE gateway = %s
                  AND id_estado = 2
                LIMIT 1
            """, (gateway,))
            row = cursor.fetchone()

        if row:
            id_reactivar = row["id_segmento"]
            upd = conexion.cursor()
            upd.execute("""
                UPDATE tbl_segmento
                SET nombre = %s,
                    direccion_red = %s,
                    mascara = %s,
                    gateway = %s,
                    id_estado = 1
                WHERE id_segmento = %s
            """, (nombre, direccion_red, mascara, gateway, id_reactivar))
            conexion.commit()

            registrar_bitacora(
                id_usuario=id_usuario_actual,
                accion="REACTIVAR",
                tabla_afectada="tbl_segmento",
                registro_id=id_reactivar,
                detalle=(
                f"Se reactivó el segmento '{nombre}' "
                f"con dirección de red '{direccion_red}'."
                )
            )

            return {
                "mensaje": "Segmento reactivado correctamente.",
                "id_segmento": id_reactivar
            }

        # Si no hay inactivos a reactivar, insertar nuevo
        cursor = conexion.cursor()
        consulta_sql = """
            INSERT INTO tbl_segmento
            (
                nombre,
                direccion_red,
                mascara,
                gateway,
                id_estado
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                1
            )
        """

        cursor.execute(
            consulta_sql,
            (
                nombre,
                direccion_red,
                mascara,
                gateway
            )
        )

        conexion.commit()

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="CREAR",
            tabla_afectada="tbl_segmento",
            registro_id=cursor.lastrowid,
            detalle=(
            f"Se creó el segmento '{nombre}' "
            f"con dirección de red '{direccion_red}'."
            )
        )

        return {
            "mensaje": "Segmento creado correctamente.",
            "id_segmento": cursor.lastrowid
        }

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear segmento: {str(e)}"
        )

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


def actualizar_segmento(id_segmento, nombre, direccion_red, mascara, gateway="", id_usuario_actual=None):
    nombre = nombre.strip()
    direccion_red = direccion_red.strip()
    mascara = mascara.strip()
    gateway = gateway.strip()

    if not nombre or not direccion_red or not mascara:
        raise HTTPException(
            status_code=400,
            detail="Nombre, dirección de red y máscara son obligatorios."
        )

    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                id_segmento,
                nombre,
                direccion_red,
                mascara,
                gateway
            FROM tbl_segmento
            WHERE id_segmento = %s
            AND id_estado = 1
        """

        cursor.execute(consulta_sql, (id_segmento,))
        segmento_anterior = cursor.fetchone()

        if not segmento_anterior:
            raise HTTPException(
            status_code=404,
            detail="Segmento no encontrado."
        )

        consulta_sql = """
            SELECT id_segmento
            FROM tbl_segmento
            WHERE nombre = %s
            AND id_segmento <> %s
            AND id_estado = 1
        """

        cursor.execute(consulta_sql, (nombre, id_segmento))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un segmento con ese nombre."
            )

        # Validar duplicado por dirección de red + máscara (solo activos), excluyendo el segmento actual
        cursor.execute("""
            SELECT id_segmento
            FROM tbl_segmento
            WHERE direccion_red = %s
              AND mascara = %s
              AND id_segmento <> %s
              AND id_estado = 1
        """, (direccion_red, mascara, id_segmento))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un segmento con esa dirección de red y máscara."
            )

        # Validar duplicado por gateway (si fue proporcionado) (solo activos), excluyendo el segmento actual
        if gateway:
            cursor.execute("""
                SELECT id_segmento
                FROM tbl_segmento
                WHERE gateway = %s
                  AND id_segmento <> %s
                  AND id_estado = 1
            """, (gateway, id_segmento))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe un segmento con ese gateway."
                )

        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_segmento
            SET
                nombre = %s,
                direccion_red = %s,
                mascara = %s,
                gateway = %s
            WHERE id_segmento = %s
        """

        cursor.execute(
            consulta_sql,
            (
                nombre,
                direccion_red,
                mascara,
                gateway,
                id_segmento
            )
        )

        conexion.commit()

        cambios = []
        if segmento_anterior["nombre"] != nombre:
            cambios.append(
                f"Nombre: '{segmento_anterior['nombre']}' → '{nombre}'"
            )

        if segmento_anterior["direccion_red"] != direccion_red:
            cambios.append(
                f"Dirección de red: "
                f"'{segmento_anterior['direccion_red']}' → '{direccion_red}'"
            )

        if segmento_anterior["mascara"] != mascara:
            cambios.append(
                f"Máscara: "
                f"'{segmento_anterior['mascara']}' → '{mascara}'"
            )

        if segmento_anterior["gateway"] != gateway:
            cambios.append(
                f"Gateway: "
                f"'{segmento_anterior['gateway']}' → '{gateway}'"
            )

        detalle = "; ".join(cambios)

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="EDITAR",
            tabla_afectada="tbl_segmento",
            registro_id=id_segmento,
            detalle=detalle if detalle else "No hubo cambios."
        )
          
        return {
            "mensaje": "Segmento actualizado correctamente."
        }

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar segmento: {str(e)}"
        )

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


def eliminar_segmento(id_segmento, id_usuario_actual):
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                id_segmento,
                nombre
            FROM tbl_segmento
            WHERE id_segmento = %s
            AND id_estado = 1
        """

        cursor.execute(consulta_sql, (id_segmento,))

        segmento = cursor.fetchone()

        if not segmento:
            raise HTTPException(
                status_code=404,
                detail="Segmento no encontrado."
            )

        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_segmento
            SET id_estado = 2
            WHERE id_segmento = %s
        """

        cursor.execute(consulta_sql, (id_segmento,))
        conexion.commit()

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="ELIMINAR",
            tabla_afectada="tbl_segmento",
            registro_id=id_segmento,
            detalle=f"Se eliminó el segmento '{segmento['nombre']}'."
        )

        return {
            "mensaje": "Segmento eliminado correctamente."
        }

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar segmento: {str(e)}"
        )

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


def generar_ips_segmento(id_segmento: int, id_usuario_actual):
    """Genera las 254 direcciones IP disponibles para el segmento especificado."""
    conexion = get_connection()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No fue posible conectar a la base de datos")

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_segmento, nombre, direccion_red, gateway FROM tbl_segmento WHERE id_segmento = %s AND id_estado = 1",
            (id_segmento,)
        )
        segmento = cursor.fetchone()
        if not segmento:
            raise HTTPException(status_code=404, detail="Segmento no encontrado.")

        # Limpiar notaciones CIDR como /24 si vienen en direccion_red
        direccion_red = (segmento.get("direccion_red") or "").strip().split("/")[0].strip()
        gateway = (segmento.get("gateway") or "").strip().split("/")[0].strip()

        partes = direccion_red.split(".")
        if len(partes) < 3:
            raise HTTPException(status_code=400, detail="La dirección de red del segmento no es válida.")

        prefix = ".".join(partes[:3])

        cursor.execute("SELECT direccion_ip FROM tbl_ip WHERE id_segmento = %s", (id_segmento,))
        existentes = {row["direccion_ip"] for row in cursor.fetchall()}

        nuevas_ips = []
        for i in range(1, 255):
            ip_str = f"{prefix}.{i}"
            if ip_str not in existentes:
                id_estado = 5 if (gateway and ip_str == gateway) else 3
                nuevas_ips.append((ip_str, id_segmento, id_estado))

        if nuevas_ips:
            cursor.executemany(
                "INSERT INTO tbl_ip (direccion_ip, id_segmento, id_estado) VALUES (%s, %s, %s)",
                nuevas_ips
            )
            conexion.commit()
            

        total_generadas = len(nuevas_ips)
        return {
            "mensaje": f"Se generaron {total_generadas} direcciones IP para el segmento '{segmento['nombre']}'.",
            "generadas": total_generadas
        }

    except HTTPException:
        raise
    except Error as e:
        if conexion:
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al generar IPs: {str(e)}")
    finally:
        if conexion and conexion.is_connected() and cursor is not None:
            cursor.close()
            conexion.close()


def limpiar_ips_segmento(id_segmento: int):
    """Elimina las IPs no asignadas del segmento especificado."""
    conexion = get_connection()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No fue posible conectar a la base de datos")

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            DELETE FROM tbl_ip 
            WHERE id_segmento = %s 
              AND id_ip NOT IN (SELECT DISTINCT id_ip FROM tbl_asignacion_ip)
        """, (id_segmento,))
        conexion.commit()
        afectados = cursor.rowcount
        return {
            "mensaje": f"Se limpiaron {afectados} registros de IP no asignados del segmento.",
            "eliminados": afectados
        }
    except Error as e:
        if conexion:
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al limpiar IPs del segmento: {str(e)}")
    finally:
        if conexion and conexion.is_connected() and cursor is not None:
            cursor.close()
            conexion.close()


def limpiar_todas_ips():
    """Elimina todas las IPs de tbl_ip que no tengan asignaciones activas."""
    conexion = get_connection()
    if conexion is None:
        raise HTTPException(status_code=500, detail="No fue posible conectar a la base de datos")

    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            DELETE FROM tbl_ip 
            WHERE id_ip NOT IN (SELECT DISTINCT id_ip FROM tbl_asignacion_ip)
        """)
        conexion.commit()
        afectados = cursor.rowcount
        return {
            "mensaje": f"Se limpiaron {afectados} registros de IP de la tabla tbl_ip.",
            "eliminados": afectados
        }
    except Error as e:
        if conexion:
            conexion.rollback()
        raise HTTPException(status_code=500, detail=f"Error al limpiar la tabla tbl_ip: {str(e)}")
    finally:
        if conexion and conexion.is_connected() and cursor is not None:
            cursor.close()
            conexion.close()


