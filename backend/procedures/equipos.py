from fastapi import HTTPException
from mysql.connector import Error
from procedures.bitacoramodulo import registrar_bitacora
from database.conexion import get_connection


def obtener_equipos(search=""):
    """
    Obtiene todos los equipos que no han sido eliminados (id_estado <> 6).
    """
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                e.id_equipo,
                e.nombre_equipo,
                e.id_tipo,
                td.nombre AS tipo,
                e.id_departamento,
                d.nombre AS departamento,
                e.marca,
                e.modelo,
                e.ubicacion,
                e.area,
                e.extension,
                e.id_estado,
                est.nombre AS estado
            FROM tbl_equipo e
            INNER JOIN tbl_tipo_dispositivo td
                ON td.id_tipo = e.id_tipo
            INNER JOIN tbl_departamento d
                ON d.id_departamento = e.id_departamento
            INNER JOIN tbl_estado est
                ON est.id_estado = e.id_estado
            WHERE
                e.id_estado <> 6
                AND (
                    e.nombre_equipo LIKE %s
                    OR td.nombre LIKE %s
                    OR d.nombre LIKE %s
                    OR IFNULL(e.marca, '') LIKE %s
                    OR IFNULL(e.modelo, '') LIKE %s
                )
            ORDER BY e.nombre_equipo ASC
        """

        termino_busqueda = f"%{search}%"
        cursor.execute(
            consulta_sql,
            (
                termino_busqueda,
                termino_busqueda,
                termino_busqueda,
                termino_busqueda,
                termino_busqueda,
            ),
        )

        return cursor.fetchall()

    except Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener equipos: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def obtener_equipo(id_equipo):
    """
    Obtiene un equipo específico por su ID.
    """
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                e.id_equipo,
                e.nombre_equipo,
                td.id_tipo,
                td.nombre AS tipo,
                d.id_departamento,
                d.nombre AS departamento,
                e.marca,
                e.modelo,
                e.ubicacion,
                e.area,
                e.extension,
                est.id_estado,
                est.nombre AS estado
            FROM tbl_equipo e
            INNER JOIN tbl_tipo_dispositivo td
                ON td.id_tipo = e.id_tipo
            INNER JOIN tbl_departamento d
                ON d.id_departamento = e.id_departamento
            INNER JOIN tbl_estado est
                ON est.id_estado = e.id_estado
            WHERE e.id_equipo = %s
              AND e.id_estado <> 6
        """

        cursor.execute(consulta_sql, (id_equipo,))
        equipo = cursor.fetchone()

        if not equipo:
            raise HTTPException(
                status_code=404, detail="Equipo no encontrado."
            )

        return equipo

    except HTTPException:
        raise

    except Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener equipo: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def crear_equipo(datos, id_usuario_actual):
    """
    Crea un nuevo equipo en la base de datos.
    """
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista el tipo de dispositivo
        cursor.execute(
            "SELECT id_tipo FROM tbl_tipo_dispositivo WHERE id_tipo = %s",
            (datos.id_tipo,),
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404, detail="El tipo de dispositivo no existe."
            )

        # Verificar que exista el departamento y esté activo
        cursor.execute(
            """
            SELECT id_departamento
            FROM tbl_departamento
            WHERE id_departamento = %s AND id_estado = 1
        """,
            (datos.id_departamento,),
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404, detail="El departamento no existe o está inactivo."
            )

        # Verificar nombre duplicado
        nombre_limpio = datos.nombre_equipo.strip()
        cursor.execute(
            """
            SELECT id_equipo
            FROM tbl_equipo
            WHERE nombre_equipo = %s AND id_estado <> 6
        """,
            (nombre_limpio,),
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=400, detail="Ya existe un equipo con ese nombre."
            )

        cursor.close()
        cursor = conexion.cursor()

        consulta_insert = """
            INSERT INTO tbl_equipo (
                id_tipo,
                id_departamento,
                nombre_equipo,
                marca,
                modelo,
                ubicacion,
                area,
                extension,
                id_estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
        """

        cursor.execute(
            consulta_insert,
            (
                datos.id_tipo,
                datos.id_departamento,
                nombre_limpio,
                getattr(datos, "marca", None),
                getattr(datos, "modelo", None),
                getattr(datos, "ubicacion", None),
                getattr(datos, "area", None),
                getattr(datos, "extension", None),
            ),
        )

        id_creado = cursor.lastrowid
        conexion.commit()

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="CREAR",
            tabla_afectada="tbl_equipo",
            registro_id=id_creado,
            detalle=(
                f"Se creó el equipo '{nombre_limpio}'. "
                f"Marca: '{getattr(datos, 'marca', '')}', "
                f"Modelo: '{getattr(datos, 'modelo', '')}'."
            ),
        )

        return {
            "mensaje": "Equipo creado correctamente.",
            "id_equipo": id_creado,
        }

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al crear equipo: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def actualizar_equipo(id_equipo, datos, id_usuario_actual):
    """
    Actualiza los datos de un equipo existente.
    """
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        # Verificar existencia
        cursor.execute(
            """
            SELECT
                id_equipo,
                id_tipo,
                id_departamento,
                nombre_equipo,
                marca,
                modelo,
                ubicacion,
                area,
                extension,
                id_estado
            FROM tbl_equipo
            WHERE id_equipo = %s AND id_estado <> 6
        """,
            (id_equipo,),
        )

        equipo_anterior = cursor.fetchone()

        if not equipo_anterior:
            raise HTTPException(
                status_code=404, detail="Equipo no encontrado."
            )

        # Verificar duplicado de nombre
        nombre_nuevo = datos.nombre_equipo.strip()
        cursor.execute(
            """
            SELECT id_equipo
            FROM tbl_equipo
            WHERE nombre_equipo = %s
              AND id_equipo <> %s
              AND id_estado <> 6
        """,
            (nombre_nuevo, id_equipo),
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400, detail="Ya existe un equipo con ese nombre."
            )

        cursor.close()
        cursor = conexion.cursor()

        # Extraer valores nuevos
        marca_nueva = getattr(datos, "marca", None)
        modelo_nuevo = getattr(datos, "modelo", None)
        ubicacion_nueva = getattr(datos, "ubicacion", None)
        area_nueva = getattr(datos, "area", None)
        extension_nueva = getattr(datos, "extension", None)

        cursor.execute(
            """
            UPDATE tbl_equipo
            SET
                id_tipo = %s,
                id_departamento = %s,
                nombre_equipo = %s,
                marca = %s,
                modelo = %s,
                ubicacion = %s,
                area = %s,
                extension = %s
            WHERE id_equipo = %s
        """,
            (
                datos.id_tipo,
                datos.id_departamento,
                nombre_nuevo,
                marca_nueva,
                modelo_nuevo,
                ubicacion_nueva,
                area_nueva,
                extension_nueva,
                id_equipo,
            ),
        )

        conexion.commit()

        # Detección de cambios para auditoría en Bitácora
        cambios = []

        if equipo_anterior["nombre_equipo"] != nombre_nuevo:
            cambios.append(
                f"Nombre: '{equipo_anterior['nombre_equipo']}' → '{nombre_nuevo}'"
            )

        if (equipo_anterior["marca"] or "") != (marca_nueva or ""):
            cambios.append(
                f"Marca: '{equipo_anterior['marca'] or ''}' → '{marca_nueva or ''}'"
            )

        if (equipo_anterior["modelo"] or "") != (modelo_nuevo or ""):
            cambios.append(
                f"Modelo: '{equipo_anterior['modelo'] or ''}' → '{modelo_nuevo or ''}'"
            )

        if (equipo_anterior["ubicacion"] or "") != (ubicacion_nueva or ""):
            cambios.append(
                f"Ubicación: '{equipo_anterior['ubicacion'] or ''}' → '{ubicacion_nueva or ''}'"
            )

        if (equipo_anterior["area"] or "") != (area_nueva or ""):
            cambios.append(
                f"Área: '{equipo_anterior['area'] or ''}' → '{area_nueva or ''}'"
            )

        if (equipo_anterior["extension"] or "") != (extension_nueva or ""):
            cambios.append(
                f"Extensión: '{equipo_anterior['extension'] or ''}' → '{extension_nueva or ''}'"
            )

        if equipo_anterior["id_tipo"] != datos.id_tipo:
            cambios.append(
                f"Tipo: {equipo_anterior['id_tipo']} → {datos.id_tipo}"
            )

        if equipo_anterior["id_departamento"] != datos.id_departamento:
            cambios.append(
                f"Departamento: {equipo_anterior['id_departamento']} → {datos.id_departamento}"
            )

        detalle_bitacora = (
            f"Se actualizaron los siguientes campos del equipo '{nombre_nuevo}': "
            + "; ".join(cambios)
            if cambios
            else "No se detectaron cambios en el registro."
        )

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="EDITAR",
            tabla_afectada="tbl_equipo",
            registro_id=id_equipo,
            detalle=detalle_bitacora,
        )

        return {"mensaje": "Equipo actualizado correctamente."}

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar equipo: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def eliminar_equipo(id_equipo, id_usuario_actual):
    """
    Realiza la eliminación lógica de un equipo (marca id_estado = 6).
    """
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id_equipo, nombre_equipo
            FROM tbl_equipo
            WHERE id_equipo = %s AND id_estado <> 6
        """,
            (id_equipo,),
        )

        equipo = cursor.fetchone()

        if not equipo:
            raise HTTPException(
                status_code=404, detail="Equipo no encontrado."
            )

        cursor.close()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE tbl_equipo
            SET id_estado = 6
            WHERE id_equipo = %s
        """,
            (id_equipo,),
        )

        conexion.commit()

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="ELIMINAR",
            tabla_afectada="tbl_equipo",
            registro_id=id_equipo,
            detalle=f"Se eliminó el equipo '{equipo['nombre_equipo']}'.",
        )

        return {"mensaje": "Equipo eliminado correctamente."}

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar equipo: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()