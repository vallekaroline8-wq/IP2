import sys
from database.conexion import get_connection

def limpiar():
    conexion = get_connection()
    if not conexion:
        print("❌ No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conexion.cursor(dictionary=True)

        # Mostrar segmentos
        cursor.execute("SELECT id_segmento, nombre, direccion_red, gateway FROM tbl_segmento")
        segmentos = cursor.fetchall()
        print("--- SEGMENTOS ---")
        for s in segmentos:
            print(s)

        # Mostrar muestra de IPs actuales
        cursor.execute("SELECT id_ip, direccion_ip, id_segmento, id_estado FROM tbl_ip LIMIT 15")
        ips = cursor.fetchall()
        print("\n--- MUESTRA DE IPs ANTES DE LIMPIAR ---")
        for ip in ips:
            print(ip)

        cursor.execute("SELECT COUNT(*) AS total FROM tbl_ip")
        total_antes = cursor.fetchone()["total"]
        print(f"\nTotal de IPs en tbl_ip antes: {total_antes}")

        # Limpiar registros de tbl_ip que no estén asignados en tbl_asignacion_ip (o todos si no hay asignaciones)
        # O si el usuario quiere limpiar todas las IPs no activas / generadas:
        # Primero desactivar verificaciones de llaves foráneas si es necesario, o borrar sin asignaciones activas
        cursor.execute("DELETE FROM tbl_ip WHERE id_ip NOT IN (SELECT DISTINCT id_ip FROM tbl_asignacion_ip)")
        conexion.commit()

        cursor.execute("SELECT COUNT(*) AS total FROM tbl_ip")
        total_despues = cursor.fetchone()["total"]
        print(f"\n✅ Proceso completado. Total de IPs en tbl_ip ahora: {total_despues}")

    except Exception as e:
        print(f"❌ Error: {e}")
        if conexion:
            conexion.rollback()
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    limpiar()
