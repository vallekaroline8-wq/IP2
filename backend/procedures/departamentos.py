from database.conexion import get_connection


def obtener_departamentos():

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT
            id_departamento,
            nombre
        FROM tbl_departamento
        ORDER BY nombre
    """

    cursor.execute(sql)
    departamentos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return departamentos


def crear_departamento(nombre):

    conexion = get_connection()
    cursor = conexion.cursor()

    sql = """
        INSERT INTO tbl_departamento(nombre)
        VALUES(%s)
    """

    cursor.execute(sql, (nombre,))
    conexion.commit()

    id_generado = cursor.lastrowid

    cursor.close()
    conexion.close()

    return {
        "mensaje": "Departamento creado correctamente",
        "id_departamento": id_generado
    }