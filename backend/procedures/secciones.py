from fastapi import HTTPException
from mysql.connector import Error

from database.conexion import get_connection


def obtener_secciones():
    """
    Obtiene todas las secciones activas junto con su departamento.
    """

    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT
                s.id_seccion,
                s.nombre,
                s.id_departamento,
                d.nombre AS departamento
            FROM tbl_seccion s
            INNER JOIN tbl_departamento d
                ON s.id_departamento = d.id_departamento
            WHERE s.id_estado = 1
            ORDER BY d.nombre ASC, s.nombre ASC
        """

        cursor.execute(consulta_sql)

        return cursor.fetchall()

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener secciones: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def crear_seccion(nombre, id_departamento):
    """
    Crea una nueva sección.
    """

    nombre = nombre.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre de la sección es obligatorio."
        )

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista el departamento y esté activo
        cursor.execute(
            """
            SELECT id_departamento
            FROM tbl_departamento
            WHERE id_departamento = %s
            AND id_estado = 1
            """,
            (id_departamento,)
        )

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El departamento no existe."
            )

        # Verificar nombre repetido
        cursor.execute(
            """
            SELECT id_seccion
            FROM tbl_seccion
            WHERE nombre = %s
            AND id_departamento = %s
            AND id_estado = 1
            """,
            (nombre, id_departamento)
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe una sección con ese nombre en ese departamento."
            )

        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO tbl_seccion
            (
                nombre,
                id_departamento,
                id_estado
            )
            VALUES
            (
                %s,
                %s,
                1
            )
            """,
            (
                nombre,
                id_departamento
            )
        )

        conexion.commit()

        return {
            "mensaje": "Sección creada correctamente.",
            "id_seccion": cursor.lastrowid
        }

    except HTTPException:
        raise

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al crear sección: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def actualizar_seccion(id_seccion, nombre, id_departamento):
    """
    Actualiza una sección.
    """

    nombre = nombre.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre de la sección es obligatorio."
        )

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista la sección y esté activa
        cursor.execute(
            """
            SELECT id_seccion
            FROM tbl_seccion
            WHERE id_seccion = %s
            AND id_estado = 1
            """,
            (id_seccion,)
        )

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="La sección no existe."
            )

        # Verificar que exista el departamento y esté activo
        cursor.execute(
            """
            SELECT id_departamento
            FROM tbl_departamento
            WHERE id_departamento = %s
            AND id_estado = 1
            """,
            (id_departamento,)
        )

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El departamento no existe."
            )

        # Verificar nombre repetido
        cursor.execute(
            """
            SELECT id_seccion
            FROM tbl_seccion
            WHERE nombre = %s
            AND id_departamento = %s
            AND id_seccion <> %s
            AND id_estado = 1
            """,
            (
                nombre,
                id_departamento,
                id_seccion
            )
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe una sección con ese nombre en ese departamento."
            )

        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE tbl_seccion
            SET
                nombre = %s,
                id_departamento = %s
            WHERE id_seccion = %s
            """,
            (
                nombre,
                id_departamento,
                id_seccion
            )
        )

        conexion.commit()

        return {
            "mensaje": "Sección actualizada correctamente."
        }

    except HTTPException:
        raise

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar sección: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def eliminar_seccion(id_seccion):
    """
    Desactiva una sección (eliminación lógica).
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista y esté activa
        cursor.execute(
            """
            SELECT id_seccion
            FROM tbl_seccion
            WHERE id_seccion = %s
            AND id_estado = 1
            """,
            (id_seccion,)
        )

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="La sección no existe."
            )

        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE tbl_seccion
            SET id_estado = 2
            WHERE id_seccion = %s
            """,
            (id_seccion,)
        )

        conexion.commit()

        return {
            "mensaje": "Sección desactivada correctamente."
        }

    except HTTPException:
        raise

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar sección: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()