from fastapi import HTTPException
from mysql.connector import Error
import hashlib

from database.conexion import get_connection
from procedures.bitacoramodulo import registrar_bitacora

ROLES_VALIDOS = [
    "ADMINISTRADOR",
    "TECNICO"
]


def _validar_contrasena(contrasena):
    if len(contrasena) < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres."
        )

    if not any(c.islower() for c in contrasena):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe incluir al menos una minúscula."
        )

    if not any(c.isupper() for c in contrasena):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe incluir al menos una mayúscula."
        )

    if not any(not c.isalnum() for c in contrasena):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe incluir al menos un carácter especial."
        )


def obtener_usuarios(search=""):
    """
    Obtiene únicamente los usuarios activos, opcionalmente filtrados por nombre o usuario.
    """
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)
        search_term = f"%{search.strip()}%" if search else "%"
        consulta_sql = """
            SELECT
                u.id_usuario,
                u.nombre,
                u.usuario,
                u.rol,
                u.id_estado,
                e.nombre AS estado
            FROM tbl_usuario u
            INNER JOIN tbl_estado e
                ON u.id_estado = e.id_estado
            WHERE u.id_estado IN (1, 2)
              AND (
                    u.nombre LIKE %s
                 OR u.usuario LIKE %s
              )
            ORDER BY u.nombre ASC
        """
        cursor.execute(consulta_sql, (search_term, search_term))
        return cursor.fetchall()
    except Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener usuarios: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def crear_usuario(
    nombre,
    usuario,
    contrasena,
    rol,
    id_estado,
    id_usuario_actual
):
    """
    Crea un nuevo usuario.
    """
    nombre = nombre.strip()
    usuario = usuario.strip()
    rol = rol.upper()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre es obligatorio."
        )

    if not usuario:
        raise HTTPException(
            status_code=400,
            detail="El usuario es obligatorio."
        )

    if not contrasena:
        raise HTTPException(
            status_code=400,
            detail="La contraseña es obligatoria."
        )

    _validar_contrasena(contrasena)

    if rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail="Rol inválido."
        )

    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        # Verificar usuario existente
        consulta_sql = """
            SELECT id_usuario
            FROM tbl_usuario
            WHERE usuario = %s
              AND id_estado = 1
        """
        cursor.execute(consulta_sql, (usuario,))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El usuario ya existe."
            )

        # Verificar estado
        consulta_sql = """
            SELECT id_estado
            FROM tbl_estado
            WHERE id_estado = %s
        """
        cursor.execute(consulta_sql, (id_estado,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El estado seleccionado no existe."
            )

        password_hash = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()

        # Cerramos el cursor anterior antes de abrir uno nuevo sin diccionario
        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            INSERT INTO tbl_usuario
            (
                nombre,
                usuario,
                contrasena,
                rol,
                id_estado
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """
        cursor.execute(
            consulta_sql,
            (
                nombre,
                usuario,
                password_hash,
                rol,
                id_estado
            )
        )
        conexion.commit()

        registrar_bitacora(
    id_usuario=id_usuario_actual,
    accion="CREAR",
    tabla_afectada="tbl_usuario",
    registro_id=cursor.lastrowid,
    detalle=f"Se creó el usuario '{usuario}'."
)

        return {
            "mensaje": "Usuario creado correctamente.",
            "id_usuario": cursor.lastrowid
        }
    except HTTPException:
        raise
    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear usuario: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def actualizar_usuario(
    id_usuario,
    nombre,
    usuario,
    rol,
    id_estado,
    id_usuario_actual
):
    """
    Actualiza un usuario.
    """
    nombre = nombre.strip()
    usuario = usuario.strip()
    rol = rol.upper()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre es obligatorio."
        )

    if not usuario:
        raise HTTPException(
            status_code=400,
            detail="El usuario es obligatorio."
        )

    if rol not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail="Rol inválido."
        )

    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista el usuario
        consulta_sql = """
            SELECT
            nombre,
            usuario,
            rol,
            id_estado
            FROM tbl_usuario
            WHERE id_usuario = %s
              AND id_estado = 1
        """
        cursor.execute(consulta_sql, (id_usuario,))

        usuario_anterior = cursor.fetchone()

        if not usuario_anterior:
            raise HTTPException(
            status_code=404,
            detail="El usuario no existe."
        )

        # Verificar usuario duplicado
        consulta_sql = """
            SELECT id_usuario
            FROM tbl_usuario
            WHERE usuario = %s
              AND id_usuario <> %s
              AND id_estado = 1
        """
        cursor.execute(consulta_sql, (usuario, id_usuario))

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El usuario ya existe."
            )

        # Verificar estado
        consulta_sql = """
            SELECT id_estado
            FROM tbl_estado
            WHERE id_estado = %s
        """
        cursor.execute(consulta_sql, (id_estado,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail="El estado seleccionado no existe."
            )

        # Cerramos el cursor con diccionario antes de abrir uno nuevo estándar
        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_usuario
            SET
                nombre = %s,
                usuario = %s,
                rol = %s,
                id_estado = %s
            WHERE id_usuario = %s
        """
        cursor.execute(
            consulta_sql,
            (
                nombre,
                usuario,
                rol,
                id_estado,
                id_usuario
            )
        )
        conexion.commit()

        cambios = []

        if usuario_anterior["nombre"] != nombre:
            cambios.append(
            f"Nombre: '{usuario_anterior['nombre']}' → '{nombre}'"
        )

        if usuario_anterior["usuario"] != usuario:
            cambios.append(
            f"Usuario: '{usuario_anterior['usuario']}' → '{usuario}'"
        )

        if usuario_anterior["rol"] != rol:
            cambios.append(
            f"Rol: '{usuario_anterior['rol']}' → '{rol}'"
        )

        if usuario_anterior["id_estado"] != id_estado:
            cambios.append(
            f"Estado: {usuario_anterior['id_estado']} → {id_estado}"
        )

        detalle = "; ".join(cambios)

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="EDITAR",
            tabla_afectada="tbl_usuario",
            registro_id=id_usuario,
            detalle=detalle if detalle else "No hubo cambios."
        )

        return {
            "mensaje": "Usuario actualizado correctamente."
        }
    except HTTPException:
        raise
    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar usuario: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def eliminar_usuario(id_usuario, id_usuario_actual):
    """
    Desactiva un usuario (eliminación lógica).
    """
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT 
                id_usuario,
                usuario,
                id_estado
            FROM tbl_usuario
            WHERE id_usuario = %s
              AND id_estado IN (1, 2)
        """

        cursor.execute(consulta_sql, (id_usuario,))

        usuario_bd = cursor.fetchone()

        if not usuario_bd:
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe."
            )

        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_usuario
            SET id_estado = 6
            WHERE id_usuario = %s
        """
        cursor.execute(consulta_sql, (id_usuario,))
        conexion.commit()

        registrar_bitacora(
    id_usuario=id_usuario_actual,
    accion="DESACTIVAR",
    tabla_afectada="tbl_usuario",
    registro_id=id_usuario,
    detalle=f"Se desactivó el usuario '{usuario_bd['usuario']}'."
)

        return {
            "mensaje": "Usuario desactivado correctamente."
        }
    
    except HTTPException:
        raise
    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al desactivar usuario: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def cambiar_password(id_usuario, contrasena, id_usuario_actual):
    """
    Cambia la contraseña de un usuario.
    """
    contrasena = contrasena.strip()

    if not contrasena:
        raise HTTPException(
            status_code=400,
            detail="La contraseña es obligatoria."
        )

    _validar_contrasena(contrasena)

    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        consulta_sql = """
            SELECT id_usuario,
            usuario
            FROM tbl_usuario
            WHERE id_usuario = %s
              AND id_estado = 1
        """
        cursor.execute(consulta_sql, (id_usuario,))

        usuario_bd = cursor.fetchone()

        if not usuario_bd:
                raise HTTPException(
                status_code=404,
                detail="El usuario no existe."
                )

        password_hash = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()

        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_usuario
            SET contrasena = %s
            WHERE id_usuario = %s
        """
        cursor.execute(consulta_sql, (password_hash, id_usuario))
        conexion.commit()

        registrar_bitacora(
    id_usuario=id_usuario_actual,
    accion="CAMBIAR CONTRASEÑA",
    tabla_afectada="tbl_usuario",
    registro_id=id_usuario,
    detalle=f"Se actualizó la contraseña del usuario '{usuario_bd['usuario']}'."
)

        return {
            "mensaje": "Contraseña actualizada correctamente."
        }
    
    except HTTPException:
        raise
    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar contraseña: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


def cambiar_estado_usuario(id_usuario, id_estado, id_usuario_actual):
    """
    Activa o desactiva un usuario.
    """
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        # Verificar que exista el usuario
        consulta_sql = """
            SELECT id_usuario, usuario, id_estado
            FROM tbl_usuario
            WHERE id_usuario = %s
        """
        cursor.execute(consulta_sql, (id_usuario,))

        usuario_bd = cursor.fetchone()

        if not usuario_bd:
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe."
            )
        
        consulta_sql = """
            SELECT nombre
            FROM tbl_estado
            WHERE id_estado = %s
                        """
        cursor.execute(
                consulta_sql,
                (usuario_bd["id_estado"],)
            )

        estado_anterior = cursor.fetchone()
        

        # Verificar estado
        consulta_sql = """
            SELECT id_estado,
            nombre
            FROM tbl_estado
            WHERE id_estado = %s
        """
        cursor.execute(consulta_sql, (id_estado,))

        estado_nuevo = cursor.fetchone()

        if not estado_nuevo:
            raise HTTPException(
                status_code=404,
                detail="Estado inválido."
            )
        
        

        cursor.close()
        cursor = conexion.cursor()

        consulta_sql = """
            UPDATE tbl_usuario
            SET id_estado = %s
            WHERE id_usuario = %s
        """
        cursor.execute(
            consulta_sql,
            (
                id_estado,
                id_usuario
            )
        )
        conexion.commit()

        registrar_bitacora(
            id_usuario=id_usuario_actual,
            accion="CAMBIAR ESTADO",
            tabla_afectada="tbl_usuario",
            registro_id=id_usuario,
            detalle=(
        f"Se cambió el estado del usuario "
        f"'{usuario_bd['usuario']}' "
        f"de '{estado_anterior['nombre']}' "
        f"a '{estado_nuevo['nombre']}'."
    )
)

        return {
            "mensaje": "Estado actualizado correctamente."
        }

    except HTTPException:
        raise
    except Error as e:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar estado: {str(e)}"
        )
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()