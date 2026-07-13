from database.conexion import get_connection

conexion = get_connection()

if conexion:
    print("===================================")
    print("✅ CONEXIÓN EXITOSA A MYSQL")
    print("Base de datos:", conexion.database)
    print("===================================")

    conexion.close()
else:
    print("❌ No fue posible conectarse.")