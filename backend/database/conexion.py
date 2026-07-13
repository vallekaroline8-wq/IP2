import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        if conexion.is_connected():
            print("✅ Conectado a MySQL")

        return conexion

    except mysql.connector.Error as err:
        print(f"❌ Error de conexión: {err}")
        return None