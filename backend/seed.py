"""Datos de ejemplo del Hospital Militar para SIGIP."""
import os
import uuid
from datetime import datetime, timezone
from database import db
from auth import hash_password


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def nid():
    return str(uuid.uuid4())


async def seed_all():
    # ---- Usuarios ----
    admin_user = os.environ.get("ADMIN_USER", "admin")
    admin_pass = os.environ.get("ADMIN_PASSWORD", "admin123")
    if not await db.usuarios.find_one({"username": admin_user}):
        await db.usuarios.insert_one({
            "id": nid(), "nombre": "Administrador del Sistema", "username": admin_user,
            "password_hash": hash_password(admin_pass), "role": "administrador",
            "activo": True, "created_at": now_iso(),
        })
    else:
        existing = await db.usuarios.find_one({"username": admin_user})
        from auth import verify_password
        if not verify_password(admin_pass, existing.get("password_hash", "")):
            await db.usuarios.update_one({"username": admin_user},
                                         {"$set": {"password_hash": hash_password(admin_pass)}})
    for uname, nombre, role in [("tecnico", "Técnico de Informática", "tecnico"),
                                ("consulta", "Usuario de Consulta", "consulta")]:
        if not await db.usuarios.find_one({"username": uname}):
            await db.usuarios.insert_one({
                "id": nid(), "nombre": nombre, "username": uname,
                "password_hash": hash_password(f"{uname}123"), "role": role,
                "activo": True, "created_at": now_iso(),
            })

    # Evitar re-sembrar datos de dominio
    if await db.segmentos.count_documents({}) > 0:
        return

    # ---- Tipos de dispositivo (RN-07 incluye Teléfono IP) ----
    tipos_def = ["Computadora de Escritorio", "Laptop", "Impresora", "Servidor",
                 "Teléfono IP", "Access Point", "Cámara IP", "Switch Administrable"]
    tipos = {}
    for t in tipos_def:
        _id = nid()
        tipos[t] = _id
        await db.tipo_dispositivo.insert_one({"id": _id, "nombre": t, "activo": True, "created_at": now_iso()})

    # ---- Departamentos ----
    deps_def = [
        ("Dirección General", "Dirección administrativa del hospital"),
        ("Informática", "Departamento de Desarrollo Institucional / Informática"),
        ("Cardiología", "Servicio de cardiología y hemodinamia"),
        ("Pediatría", "Atención pediátrica y neonatología"),
        ("Emergencias", "Servicio de urgencias médicas"),
        ("Laboratorio Clínico", "Análisis clínicos y patología"),
        ("Farmacia", "Farmacia hospitalaria"),
    ]
    deps = {}
    for nombre, desc in deps_def:
        _id = nid()
        deps[nombre] = _id
        await db.departamentos.insert_one({"id": _id, "nombre": nombre, "descripcion": desc,
                                           "activo": True, "created_at": now_iso()})

    # ---- Secciones ----
    secc_def = [
        ("Soporte Técnico", "Informática"), ("Redes y Servidores", "Informática"),
        ("Consulta Externa", "Cardiología"), ("Hospitalización", "Pediatría"),
        ("Triaje", "Emergencias"), ("Toma de Muestras", "Laboratorio Clínico"),
        ("Recepción", "Dirección General"),
    ]
    for nombre, dep in secc_def:
        await db.secciones.insert_one({"id": nid(), "nombre": nombre, "departamento_id": deps[dep],
                                       "activo": True, "created_at": now_iso()})

    # ---- Segmentos + IPs ----
    segs_def = [
        ("Segmento Administrativo", "192.168.10.0", "Dirección General"),
        ("Segmento Informática", "192.168.20.0", "Informática"),
        ("Segmento Cardiología", "192.168.30.0", "Cardiología"),
        ("Segmento Teléfonos IP", "192.168.40.0", "Emergencias"),
    ]
    seg_ids = {}
    for nombre, red, dep in segs_def:
        _id = nid()
        seg_ids[nombre] = _id
        base = ".".join(red.split(".")[:3])
        gw = f"{base}.254"
        await db.segmentos.insert_one({"id": _id, "nombre": nombre, "direccion_red": red,
                                       "mascara": "255.255.255.0", "gateway": gw,
                                       "activo": True, "created_at": now_iso()})
        ips = [{"id": nid(), "direccion": f"{base}.{i}", "segmento_id": _id,
                "estado": "disponible", "equipo_id": None, "created_at": now_iso()} for i in range(1, 255)]
        await db.ips.insert_many(ips)
        # RN-01: autorizar segmento al departamento
        await db.departamento_segmento.insert_one({"id": nid(), "departamento_id": deps[dep], "segmento_id": _id})

    # Autorizaciones extra
    await db.departamento_segmento.insert_one({"id": nid(), "departamento_id": deps["Informática"],
                                               "segmento_id": seg_ids["Segmento Administrativo"]})

    # ---- Equipos ----
    equipos_def = [
        ("PC-DIR-01", "Dell", "OptiPlex 7090", "Computadora de Escritorio", "Dirección General", False),
        ("PC-INF-01", "HP", "EliteDesk 800", "Computadora de Escritorio", "Informática", False),
        ("SRV-DATOS-01", "Dell", "PowerEdge R740", "Servidor", "Informática", False),
        ("TEL-EMER-01", "Cisco", "IP Phone 8845", "Teléfono IP", "Emergencias", True),
        ("TEL-EMER-02", "Cisco", "IP Phone 8845", "Teléfono IP", "Emergencias", True),
        ("PC-CARD-01", "Lenovo", "ThinkCentre M70", "Computadora de Escritorio", "Cardiología", False),
    ]
    eq_ids = {}
    for nombre, marca, modelo, tipo, dep, tel in equipos_def:
        _id = nid()
        eq_ids[nombre] = _id
        await db.equipos.insert_one({
            "id": _id, "nombre": nombre, "marca": marca, "modelo": modelo,
            "tipo_id": tipos[tipo], "departamento_id": deps[dep], "seccion_id": "",
            "es_telefono_ip": tel, "activo": True, "created_at": now_iso(),
        })

    # ---- Asignaciones de ejemplo ----
    async def asignar(eq_nombre, seg_nombre, octeto):
        seg_id = seg_ids[seg_nombre]
        base = ".".join([s for s in (await db.segmentos.find_one({"id": seg_id}))["direccion_red"].split(".")[:3]])
        ip = await db.ips.find_one({"segmento_id": seg_id, "direccion": f"{base}.{octeto}"})
        eq_id = eq_ids[eq_nombre]
        await db.ips.update_one({"id": ip["id"]}, {"$set": {"estado": "ocupada", "equipo_id": eq_id}})
        await db.asignaciones.insert_one({
            "id": nid(), "ip_id": ip["id"], "equipo_id": eq_id, "fecha_asignacion": now_iso(),
            "fecha_liberacion": None, "activo": True, "usuario": "admin",
        })

    await asignar("PC-DIR-01", "Segmento Administrativo", 10)
    await asignar("PC-INF-01", "Segmento Informática", 15)
    await asignar("SRV-DATOS-01", "Segmento Informática", 5)
    await asignar("TEL-EMER-01", "Segmento Teléfonos IP", 20)

    await db.bitacora.insert_one({"id": nid(), "usuario": "sistema", "accion": "Inicialización",
                                  "modulo": "Sistema", "detalle": "Datos de ejemplo cargados",
                                  "fecha": now_iso()})
