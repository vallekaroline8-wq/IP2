from fastapi import HTTPException
from mysql.connector import Error
from procedures.bitacoramodulo import registrar_bitacora

from database.conexion import get_connection


def obtener_departamentos():
    """
    Obtiene únicamente los departamentos activos.
    """

    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                id_departamento,
                nombre
            FROM tbl_departamento
            WHERE id_estado = 1
            ORDER BY nombre ASC
        """

        cursor.execute(consulta_sql)

        return cursor.fetchall()

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener departamentos: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def crear_departamento(nombre, id_usuario_actual):
    """
    Crea un nuevo departamento.
    """

    nombre = nombre.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre del departamento es obligatorio."
        )

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar si ya existe un departamento ACTIVO con ese nombre
        consulta_sql = """
            SELECT id_departamento
            FROM tbl_departamento
            WHERE nombre = %s
            AND id_estado = 1
        """

        cursor.execute(consulta_sql, (nombre,))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un departamento con ese nombre."
            )

        cursor = conexion.cursor()

        consulta_sql = """
            INSERT INTO tbl_departamento
            (
                nombre,
                id_estado
            )
            VALUES
            (
                %s,
                1
            )
        """

        cursor.execute(consulta_sql, (nombre,))
        conexion.commit()

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="CREAR",
            tabla_afectada="tbl_departamento",
            registro_id=cursor.lastrowid,
            detalle=f"Se creó el departamento '{nombre}'."
        )

        return {
            "mensaje": "Departamento creado correctamente.",
            "id_departamento": cursor.lastrowid
        }

    except HTTPException:
        raise

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al crear departamento: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def actualizar_departamento(id_departamento, nombre, id_usuario_actual):
    """
    Actualiza el nombre de un departamento.
    """

    nombre = nombre.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre del departamento es obligatorio."
        )

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista y esté activo
        consulta_sql = """
            SELECT 
                id_departamento,
                nombre
            FROM tbl_departamento
            WHERE id_departamento = %s
            AND id_estado = 1
        """

        cursor.execute(consulta_sql, (id_departamento,))

        departamento_anterior = cursor.fetchone()

        if not departamento_anterior:
            raise HTTPException(
                status_code=404,
                detail="Departamento no encontrado."
            )

        # Verificar nombre duplicado
        consulta_sql = """
            SELECT
                id_departamento,
                nombre
            FROM tbl_departamento
            WHERE nombre = %s
            AND id_departamento <> %s
            AND id_estado = 1
        """
    
        cursor.execute(consulta_sql, (nombre, id_departamento))
        
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un departamento con ese nombre."
            )

        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_departamento
            SET nombre = %s
            WHERE id_departamento = %s
        """

        cursor.execute(
            consulta_sql,
            (
                nombre,
                id_departamento
            )
        )

        conexion.commit()

        cambios = []

        if departamento_anterior["nombre"] != nombre:
            cambios.append(
            f"Nombre: '{departamento_anterior['nombre']}' → '{nombre}'"
    )

        detalle = "; ".join(cambios)

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="EDITAR",
            tabla_afectada="tbl_departamento",
            registro_id=id_departamento,
            detalle=detalle if detalle else "No hubo cambios."
        )

        return {
            "mensaje": "Departamento actualizado correctamente."
        }

    except HTTPException:
        raise

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar departamento: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def eliminar_departamento(id_departamento, id_usuario_actual):
    """
    Desactiva un departamento (eliminación lógica).
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista y esté activo
        consulta_sql = """
            SELECT id_departamento,
            nombre
            FROM tbl_departamento
            WHERE id_departamento = %s
            AND id_estado = 1
        """

        cursor.execute(consulta_sql, (id_departamento,))
    
        departamento = cursor.fetchone()

        if not departamento:
            raise HTTPException(
                status_code=404,
                detail="Departamento no encontrado."
            )

        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_departamento
            SET id_estado = 2
            WHERE id_departamento = %s
        """

        cursor.execute(consulta_sql, (id_departamento,))
        
        conexion.commit()

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="DESACTIVAR",
            tabla_afectada="tbl_departamento",
            registro_id=id_departamento,
            detalle=f"Se desactivó el departamento '{departamento['nombre']}'."
            )

        return {
            "mensaje": "Departamento desactivado correctamente."
        }

    except HTTPException:
        raise

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar departamento: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()