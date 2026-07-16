from database.conexion import get_connection


def login_usuario(username):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT
            u.id_usuario,
            u.nombre,
            u.usuario,
            u.contrasena,
            u.rol,
            e.nombre AS estado
        FROM tbl_usuario u
        INNER JOIN tbl_estado e
            ON u.id_estado = e.id_estado
        WHERE u.usuario = %s
    """

    cursor.execute(sql, (username,))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario


def obtener_usuario_por_id(id_usuario):

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT
            u.id_usuario,
            u.nombre,
            u.usuario,
            u.rol,
            e.nombre AS estado
        FROM tbl_usuario u
        INNER JOIN tbl_estado e
            ON u.id_estado = e.id_estado
        WHERE u.id_usuario = %s
    """

    cursor.execute(sql, (id_usuario,))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario