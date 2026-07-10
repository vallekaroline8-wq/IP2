import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

print("ADMIN")
print(hash_password("admin123"))

print()

print("TECNICO")
print(hash_password("tecnico123"))

print()

print("CONSULTA")
print(hash_password("consulta123"))