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