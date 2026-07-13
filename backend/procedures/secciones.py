from fastapi import HTTPException
from mysql.connector import Error

from database.conexion import get_connection


def obtener_secciones():
    """
    Obtiene todas las secciones junto con su departamento.
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

        # Verificar que exista el departamento
        cursor.execute(
            """
            SELECT id_departamento
            FROM tbl_departamento
            WHERE id_departamento = %s
            """,
            (id_departamento,)
        )

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El departamento no existe."
            )

        # Verificar que no exista otra sección igual
        cursor.execute(
            """
            SELECT id_seccion
            FROM tbl_seccion
            WHERE nombre = %s
            AND id_departamento = %s
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
            INSERT INTO tbl_seccion(nombre, id_departamento)
            VALUES(%s, %s)
            """,
            (nombre, id_departamento)
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

        # Verificar que exista la sección
        cursor.execute(
            """
            SELECT id_seccion
            FROM tbl_seccion
            WHERE id_seccion = %s
            """,
            (id_seccion,)
        )

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="La sección no existe."
            )

        # Verificar que exista el departamento
        cursor.execute(
            """
            SELECT id_departamento
            FROM tbl_departamento
            WHERE id_departamento = %s
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
            """,
            (nombre, id_departamento, id_seccion)
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
            SET nombre = %s,
                id_departamento = %s
            WHERE id_seccion = %s
            """,
            (nombre, id_departamento, id_seccion)
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
        cursor.close()
        conexion.close()


def eliminar_seccion(id_seccion):
    """
    Elimina una sección.
    """

    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista
        cursor.execute(
            """
            SELECT id_seccion
            FROM tbl_seccion
            WHERE id_seccion = %s
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
            DELETE
            FROM tbl_seccion
            WHERE id_seccion = %s
            """,
            (id_seccion,)
        )

        conexion.commit()

        return {
            "mensaje": "Sección eliminada correctamente."
        }

    except HTTPException:
        raise

    except Error as e:
        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar sección: {str(e)}"
        )

    finally:
        cursor.close()
        conexion.close()