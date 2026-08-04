from database.conexion import get_connection


def obtener_dashboard():

    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    # ==========================
    # TARJETAS PRINCIPALES
    # ==========================

    cursor.execute("""
        SELECT COUNT(*) total
        FROM tbl_departamento
        WHERE id_estado = 1
    """)
    departamentos = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM tbl_segmento
        WHERE id_estado = 1
    """)
    segmentos = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM tbl_equipo
        WHERE id_estado = 1
    """)
    equipos = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM tbl_ip
        WHERE id_estado IN (3,4,5)
    """)
    ips = cursor.fetchone()["total"]

    # ==========================
    # ESTADOS DE IP
    # ==========================

    cursor.execute("""
        SELECT COUNT(*) total
        FROM tbl_ip
        WHERE id_estado = 3
    """)
    disponibles = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM tbl_ip
        WHERE id_estado = 4
    """)
    ocupadas = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM tbl_ip
        WHERE id_estado = 5
    """)
    reservadas = cursor.fetchone()["total"]

    # ==========================
    # USUARIOS
    # ==========================

    cursor.execute("""
        SELECT COUNT(*) total
        FROM tbl_usuario
        WHERE id_estado = 1
    """)
    usuarios_activos = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM tbl_usuario
        WHERE id_estado = 2
    """)
    usuarios_inactivos = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) total
        FROM tbl_usuario
        WHERE id_estado = 6
    """)
    usuarios_eliminados = cursor.fetchone()["total"]

    # ==========================
    # TELEFONOS
    # ==========================

    telefonos = 0

    try:

        cursor.execute("""
            SELECT COUNT(*) total
            FROM tbl_telefono
            WHERE id_estado = 1
        """)

        telefonos = cursor.fetchone()["total"]

    except:
        pass

    # ==========================
    # GRAFICO PIE (ESTADOS IP)
    # ==========================

    cursor.execute("""
        SELECT
            e.nombre,
            COUNT(*) cantidad
        FROM tbl_ip ip
        INNER JOIN tbl_estado e
            ON e.id_estado = ip.id_estado
        GROUP BY e.nombre
        ORDER BY e.id_estado
    """)

    pie = cursor.fetchall()

    # ==========================
    # EQUIPOS POR DEPARTAMENTO
    # ==========================

    cursor.execute("""
        SELECT
            d.nombre,
            COUNT(eq.id_equipo) cantidad
        FROM tbl_departamento d
        LEFT JOIN tbl_equipo eq
            ON eq.id_departamento = d.id_departamento
            AND eq.id_estado = 1
        WHERE d.id_estado = 1
        GROUP BY d.id_departamento, d.nombre
        ORDER BY d.nombre
    """)

    por_departamento = cursor.fetchall()

    # ==========================
    # ULTIMAS ASIGNACIONES
    # ==========================

    ultimas_asignaciones = []

    # ==========================
    # ACTIVIDAD
    # ==========================

    actividad = []

    cursor.close()
    conexion.close()

    return {

        "cards": {

            "departamentos": departamentos,
            "segmentos": segmentos,
            "equipos": equipos,
            "ips": ips,

            "disponibles": disponibles,
            "ocupadas": ocupadas,
            "reservadas": reservadas,

            "usuarios_activos": usuarios_activos,
            "usuarios_inactivos": usuarios_inactivos,
            "usuarios_eliminados": usuarios_eliminados,

            "telefonos": telefonos

        },

        "pie": pie,

        "por_departamento": por_departamento,

        "ultimas_asignaciones": ultimas_asignaciones,

        "actividad": actividad

    }