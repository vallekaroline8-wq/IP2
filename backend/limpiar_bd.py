"""
Script para vaciar los datos de la base de datos de SIGIP
y reiniciar todos los contadores de IDs (AUTO_INCREMENT = 1),
conservando la estructura de las tablas, relaciones (Foreign Keys) y catálogo de estados.
"""
from database.conexion import get_connection

def limpiar_base_datos():
    conexion = get_connection()
    if not conexion:
        print("❌ No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conexion.cursor()
        print("⚡ Desactivando verificación de llaves foráneas...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        tablas = [
            "tbl_asignacion_ip",
            "tbl_ip",
            "tbl_equipo",
            "tbl_departamento_segmento",
            "tbl_segmento",
            "tbl_departamento"
        ]

        for tabla in tablas:
            try:
                cursor.execute(f"TRUNCATE TABLE {tabla};")
                cursor.execute(f"ALTER TABLE {tabla} AUTO_INCREMENT = 1;")
                print(f"  ✓ Tabla '{tabla}' vaciada y contador AUTO_INCREMENT reiniciado a 1.")
            except Exception as e:
                try:
                    cursor.execute(f"DELETE FROM {tabla};")
                    cursor.execute(f"ALTER TABLE {tabla} AUTO_INCREMENT = 1;")
                    print(f"  ✓ Registros de '{tabla}' eliminados y contador reiniciado.")
                except Exception as ex:
                    print(f"  ⚠ Omisión en '{tabla}': {ex}")

        print("⚡ Reactivando verificación de llaves foráneas...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conexion.commit()

        print("\n✅ Base de datos vaciada y contadores de IDs reiniciados a 1 correctamente.")

    except Exception as e:
        print(f"❌ Error durante el vaciado de datos: {e}")
        if conexion:
            conexion.rollback()
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    limpiar_base_datos()
