from database.conexion import get_connection

def inspect():
    conn = get_connection()
    c = conn.cursor(dictionary=True)
    with open("inspect_out.txt", "w", encoding="utf-8") as f:
        c.execute("DESCRIBE tbl_tipo_dispositivo")
        f.write("--- tbl_tipo_dispositivo columns ---\n")
        for col in c.fetchall():
            f.write(f"{col['Field']} | {col['Type']}\n")
    conn.close()

if __name__ == "__main__":
    inspect()
