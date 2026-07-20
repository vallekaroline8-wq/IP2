from fastapi import HTTPException
from mysql.connector import Error

from database.conexion import get_connection


def obtener_segmentos(all: bool = False):
    """Obtiene los segmentos desde tbl_segmento."""

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
        """

        if not all:
            consulta_sql += "\n            WHERE id_estado = 1"

        consulta_sql += "\n            ORDER BY nombre ASC"

        cursor.execute(consulta_sql)
        return cursor.fetchall()

    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener segmentos: {str(e)}"
        )

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


def crear_segmento(nombre, direccion_red, mascara, gateway=""):
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


def actualizar_segmento(id_segmento, nombre, direccion_red, mascara, gateway=""):
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
            WHERE id_segmento = %s
            AND id_estado = 1
        """

        cursor.execute(consulta_sql, (id_segmento,))

        if not cursor.fetchone():
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


def eliminar_segmento(id_segmento):
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT id_segmento
            FROM tbl_segmento
            WHERE id_segmento = %s
            AND id_estado = 1
        """

        cursor.execute(consulta_sql, (id_segmento,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Segmento no encontrado."
            )

        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_segmento
            SET id_estado = 2
            WHERE id_segmento = %s
        """

        cursor.execute(consulta_sql, (id_segmento,))
        conexion.commit()

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
