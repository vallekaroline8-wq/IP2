from database.conexion import get_connection
from fastapi import HTTPException
from mysql.connector import Error


def obtener_bitacora(search="", page=1):
    conexion = get_connection()

    try:
        cursor = conexion.cursor(dictionary=True)

        page_size = 10
        offset = (page - 1) * page_size
        search_term = f"%{search.strip()}%" if search else "%"

        consulta_sql = """
            SELECT
                b.id_bitacora AS id,
                u.usuario,
                b.accion,
                b.tabla_afectada AS modulo,
                b.registro_id,
                b.detalle,
                b.fecha
            FROM tbl_bitacora b
            LEFT JOIN tbl_usuario u
                ON b.id_usuario = u.id_usuario
            WHERE
                u.usuario LIKE %s
                OR b.accion LIKE %s
                OR b.tabla_afectada LIKE %s
                OR b.detalle LIKE %s
            ORDER BY b.fecha DESC
            LIMIT %s OFFSET %s
        """

        cursor.execute(
            consulta_sql,
            (
                search_term,
                search_term,
                search_term,
                search_term,
                page_size,
                offset
            )
        )

        items = cursor.fetchall()

        consulta_total = """
            SELECT COUNT(*) AS total
            FROM tbl_bitacora b
            LEFT JOIN tbl_usuario u
                ON b.id_usuario = u.id_usuario
            WHERE
                u.usuario LIKE %s
                OR b.accion LIKE %s
                OR b.tabla_afectada LIKE %s
                OR b.detalle LIKE %s
        """

        cursor.execute(
            consulta_total,
            (
                search_term,
                search_term,
                search_term,
                search_term
            )
        )

        total = cursor.fetchone()["total"]

        return {
            "items": items,
            "pages": max(1, (total + page_size - 1) // page_size),
            "total": total
        }

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def registrar_bitacora(
    id_usuario,
    accion,
    tabla_afectada,
    registro_id,
    detalle
):
    conexion = get_connection()

    try:
        cursor = conexion.cursor()

        consulta_sql = """
            INSERT INTO tbl_bitacora
            (
                id_usuario,
                accion,
                tabla_afectada,
                registro_id,
                detalle
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        cursor.execute(
            consulta_sql,
            (
                id_usuario,
                accion,
                tabla_afectada,
                registro_id,
                detalle
            )
        )

        conexion.commit()

    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar la bitácora: {str(e)}"
        )

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()