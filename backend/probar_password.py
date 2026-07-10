from procedures.usuarios import login_usuario
from auth import verificar_password

usuario = login_usuario("admin")

if verificar_password("admin123", usuario["contrasena"]):
    print("LOGIN CORRECTO")
else:
    print("LOGIN INCORRECTO")