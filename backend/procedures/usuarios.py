from database.conexion import get_connection


def login_usuario(username):

    conexion = get_connection()

    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT
            id_usuario,
            nombre,
            usuario,
            contrasena,
            rol,
            estado
        FROM tbl_usuario
        WHERE usuario = %s
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
            id_usuario,
            nombre,
            usuario,
            rol,
            estado
        FROM tbl_usuario
        WHERE id_usuario = %s
    """

    cursor.execute(sql, (id_usuario,))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario