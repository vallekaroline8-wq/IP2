from fastapi import HTTPException
from mysql.connector import Error

from database.conexion import get_connection


def obtener_equipos(search=""):
    """
    Obtiene todos los equipos que no han sido eliminados.
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
                est.id_estado,
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

        cursor.execute(consulta_sql, (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"))

        return cursor.fetchall()

    except Error as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener equipos: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()


def obtener_equipo(id_equipo):
    """
    Obtiene un equipo por su ID.
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
                e.id_estado,
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

        cursor.execute(
            consulta_sql,
            (id_equipo,)
        )

        equipo = cursor.fetchone()

        if not equipo:

            raise HTTPException(
                status_code=404,
                detail="Equipo no encontrado."
            )

        return equipo

    except HTTPException:
        raise

    except Error as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener equipo: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()
def crear_equipo(datos):
    """
    Crea un nuevo equipo.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista el tipo
        cursor.execute("""
            SELECT id_tipo
            FROM tbl_tipo_dispositivo
            WHERE id_tipo = %s
        """, (datos.id_tipo,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El tipo de dispositivo no existe."
            )

        # Verificar que exista el departamento
        cursor.execute("""
            SELECT id_departamento
            FROM tbl_departamento
            WHERE id_departamento = %s
            AND id_estado = 1
        """, (datos.id_departamento,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El departamento no existe."
            )

        # Verificar nombre duplicado
        cursor.execute("""
            SELECT id_equipo
            FROM tbl_equipo
            WHERE nombre_equipo = %s
            AND id_estado <> 6
        """, (datos.nombre_equipo.strip(),))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un equipo con ese nombre."
            )

        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO tbl_equipo
            (
                id_tipo,
                id_departamento,
                nombre_equipo,
                marca,
                modelo,
                id_estado
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                1
            )
        """,
        (
            datos.id_tipo,
            datos.id_departamento,
            datos.nombre_equipo.strip(),
            datos.marca,
            datos.modelo
        ))

        conexion.commit()

        return {
            "mensaje": "Equipo creado correctamente.",
            "id_equipo": cursor.lastrowid
        }

    except HTTPException:
        raise

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al crear equipo: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()


def actualizar_equipo(id_equipo, datos):
    """
    Actualiza un equipo.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        # Verificar existencia
        cursor.execute("""
            SELECT id_equipo
            FROM tbl_equipo
            WHERE id_equipo=%s
            AND id_estado<>6
        """, (id_equipo,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Equipo no encontrado."
            )

        # Verificar duplicado
        cursor.execute("""
            SELECT id_equipo
            FROM tbl_equipo
            WHERE nombre_equipo=%s
            AND id_equipo<>%s
            AND id_estado<>6
        """,
        (
            datos.nombre_equipo.strip(),
            id_equipo
        ))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Ya existe un equipo con ese nombre."
            )

        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE tbl_equipo
            SET
                id_tipo=%s,
                id_departamento=%s,
                nombre_equipo=%s,
                marca=%s,
                modelo=%s
            WHERE id_equipo=%s
        """,
        (
            datos.id_tipo,
            datos.id_departamento,
            datos.nombre_equipo.strip(),
            datos.marca,
            datos.modelo,
            id_equipo
        ))

        conexion.commit()

        return {
            "mensaje": "Equipo actualizado correctamente."
        }

    except HTTPException:
        raise

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar equipo: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()


def eliminar_equipo(id_equipo):
    """
    Eliminación lógica del equipo.
    """

    conexion = get_connection()

    try:

        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_equipo
            FROM tbl_equipo
            WHERE id_equipo=%s
            AND id_estado<>6
        """, (id_equipo,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Equipo no encontrado."
            )

        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE tbl_equipo
            SET id_estado=6
            WHERE id_equipo=%s
        """, (id_equipo,))

        conexion.commit()

        return {
            "mensaje": "Equipo eliminado correctamente."
        }

    except HTTPException:
        raise

    except Error as e:

        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar equipo: {str(e)}"
        )

    finally:

        if conexion.is_connected():
            cursor.close()
            conexion.close()