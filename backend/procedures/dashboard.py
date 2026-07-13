from database.conexion import get_connection


def obtener_dashboard():

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    dashboard = {}

    # Departamentos
    cursor.execute("SELECT COUNT(*) AS total FROM tbl_departamento")
    departamentos = cursor.fetchone()["total"]

    # Secciones
    cursor.execute("SELECT COUNT(*) AS total FROM tbl_seccion")
    secciones = cursor.fetchone()["total"]

    # Segmentos
    cursor.execute("SELECT COUNT(*) AS total FROM tbl_segmento")
    segmentos = cursor.fetchone()["total"]

    # Equipos
    cursor.execute("SELECT COUNT(*) AS total FROM tbl_equipo")
    equipos = cursor.fetchone()["total"]

    # Total IP
    cursor.execute("SELECT COUNT(*) AS total FROM tbl_ip")
    ips = cursor.fetchone()["total"]

    cursor.close()
    conexion.close()

    dashboard = {
        "cards": {
            "departamentos": departamentos,
            "secciones": secciones,
            "segmentos": segmentos,
            "equipos": equipos,
            "ips": ips,
            "disponibles": 0,
            "ocupadas": 0,
            "telefonos": 0
        },
        "pie": [],
        "por_segmento": [],
        "ultimas_asignaciones": [],
        "actividad": []
    }

    return dashboard