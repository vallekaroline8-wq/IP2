"""
SIGIP - Sistema de Gestión de Direcciones IP (Hospital Militar)
Backend FastAPI + MongoDB. API REST tipo IPAM.
"""
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response, Query
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import io

from database import db, client
from auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    get_current_user, require_roles,
)
from exports import build_excel, build_pdf
from seed import seed_all

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sigip")

app = FastAPI(title="SIGIP API")
api = APIRouter(prefix="/api")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


async def log_bitacora(usuario: str, accion: str, modulo: str, detalle: str = ""):
    await db.bitacora.insert_one({
        "id": new_id(), "usuario": usuario, "accion": accion,
        "modulo": modulo, "detalle": detalle, "fecha": now_iso(),
    })


def clean(doc: dict) -> dict:
    doc.pop("_id", None)
    doc.pop("password_hash", None)
    return doc


# ==================== MODELOS ====================
class LoginInput(BaseModel):
    username: str
    password: str


class Departamento(BaseModel):
    nombre: str
    descripcion: Optional[str] = ""


class Seccion(BaseModel):
    nombre: str
    departamento_id: str


class Segmento(BaseModel):
    nombre: str
    direccion_red: str
    mascara: str = "255.255.255.0"
    gateway: Optional[str] = ""


class TipoDispositivo(BaseModel):
    nombre: str


class Equipo(BaseModel):
    nombre: str
    marca: Optional[str] = ""
    modelo: Optional[str] = ""
    tipo_id: str
    departamento_id: str
    seccion_id: Optional[str] = ""
    es_telefono_ip: bool = False


class DepSegInput(BaseModel):
    departamento_id: str
    segmento_ids: List[str]


class EstadoIPInput(BaseModel):
    estado: str


class AsignacionInput(BaseModel):
    ip_id: str
    equipo_id: str


class UsuarioInput(BaseModel):
    nombre: str
    username: str
    password: Optional[str] = None
    role: str
    activo: bool = True


class PasswordInput(BaseModel):
    password: str


# ==================== AUTENTICACIÓN ====================
@api.post("/auth/login")
async def login(data: LoginInput, response: Response):
    user = await db.usuarios.find_one({"username": data.username.lower()})
    if not user or not verify_password(data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    if not user.get("activo", True):
        raise HTTPException(status_code=403, detail="Usuario inactivo. Contacte al administrador")
    access = create_access_token(user["id"], user["username"], user["role"])
    refresh = create_refresh_token(user["id"])
    response.set_cookie("access_token", access, httponly=True, secure=False, samesite="lax", max_age=28800, path="/")
    response.set_cookie("refresh_token", refresh, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    await log_bitacora(user["username"], "Inicio de sesión", "Autenticación", "Login exitoso")
    return {"user": clean(dict(user)), "token": access}


@api.post("/auth/logout")
async def logout(response: Response, user: dict = Depends(get_current_user)):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Sesión cerrada"}


@api.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return user


# ==================== CRUD GENÉRICO ====================
def register_crud(collection: str, modulo: str, Model, write_roles=("administrador", "tecnico")):
    @api.get(f"/{collection}")
    async def list_items(search: str = "", page: int = 1, limit: int = 10,
                         all: bool = False, user: dict = Depends(get_current_user)):
        query = {"activo": True}
        if search:
            query["nombre"] = {"$regex": search, "$options": "i"}
        if all:
            docs = await db[collection].find(query).sort("nombre", 1).to_list(1000)
            return {"items": [clean(d) for d in docs], "total": len(docs)}
        total = await db[collection].count_documents(query)
        skip = (page - 1) * limit
        docs = await db[collection].find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        return {"items": [clean(d) for d in docs], "total": total, "page": page,
                "pages": max(1, (total + limit - 1) // limit)}

    @api.post(f"/{collection}")
    async def create_item(data: Model, user: dict = Depends(require_roles(*write_roles))):
        doc = data.model_dump()
        doc.update({"id": new_id(), "activo": True, "created_at": now_iso()})
        await db[collection].insert_one(doc)
        await log_bitacora(user["username"], "Alta", modulo, f"Creó: {doc.get('nombre', doc['id'])}")
        return clean(doc)

    @api.put(f"/{collection}/{{item_id}}")
    async def update_item(item_id: str, data: Model, user: dict = Depends(require_roles(*write_roles))):
        existing = await db[collection].find_one({"id": item_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        await db[collection].update_one({"id": item_id}, {"$set": data.model_dump()})
        await log_bitacora(user["username"], "Modificación", modulo, f"Editó: {data.model_dump().get('nombre', item_id)}")
        updated = await db[collection].find_one({"id": item_id})
        return clean(updated)

    @api.delete(f"/{collection}/{{item_id}}")
    async def delete_item(item_id: str, user: dict = Depends(require_roles("administrador"))):
        existing = await db[collection].find_one({"id": item_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Registro no encontrado")
        await db[collection].update_one({"id": item_id}, {"$set": {"activo": False}})
        await log_bitacora(user["username"], "Baja", modulo, f"Eliminó: {existing.get('nombre', item_id)}")
        return {"message": "Registro eliminado"}


register_crud("departamentos", "Departamentos", Departamento)
register_crud("secciones", "Secciones", Seccion)
register_crud("tipo_dispositivo", "Tipos de Dispositivo", TipoDispositivo)


# ==================== SEGMENTOS ====================
@api.get("/segmentos")
async def list_segmentos(search: str = "", page: int = 1, limit: int = 10, all: bool = False,
                        user: dict = Depends(get_current_user)):
    query = {"activo": True}
    if search:
        query["$or"] = [{"nombre": {"$regex": search, "$options": "i"}},
                        {"direccion_red": {"$regex": search, "$options": "i"}}]
    docs = await db.segmentos.find(query).sort("nombre", 1).to_list(1000)
    for d in docs:
        clean(d)
        d["total_ips"] = await db.ips.count_documents({"segmento_id": d["id"]})
        d["ocupadas"] = await db.ips.count_documents({"segmento_id": d["id"], "estado": "ocupada"})
        d["disponibles"] = await db.ips.count_documents({"segmento_id": d["id"], "estado": "disponible"})
    if all:
        return {"items": docs, "total": len(docs)}
    total = len(docs)
    skip = (page - 1) * limit
    return {"items": docs[skip:skip + limit], "total": total, "page": page,
            "pages": max(1, (total + limit - 1) // limit)}


@api.post("/segmentos")
async def create_segmento(data: Segmento, user: dict = Depends(require_roles("administrador", "tecnico"))):
    doc = data.model_dump()
    doc.update({"id": new_id(), "activo": True, "created_at": now_iso()})
    await db.segmentos.insert_one(doc)
    await log_bitacora(user["username"], "Alta", "Segmentos", f"Creó segmento: {doc['nombre']}")
    return clean(doc)


@api.put("/segmentos/{seg_id}")
async def update_segmento(seg_id: str, data: Segmento, user: dict = Depends(require_roles("administrador", "tecnico"))):
    if not await db.segmentos.find_one({"id": seg_id}):
        raise HTTPException(status_code=404, detail="Segmento no encontrado")
    await db.segmentos.update_one({"id": seg_id}, {"$set": data.model_dump()})
    await log_bitacora(user["username"], "Modificación", "Segmentos", f"Editó segmento: {data.nombre}")
    return clean(await db.segmentos.find_one({"id": seg_id}))


@api.delete("/segmentos/{seg_id}")
async def delete_segmento(seg_id: str, user: dict = Depends(require_roles("administrador"))):
    existing = await db.segmentos.find_one({"id": seg_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Segmento no encontrado")
    if await db.ips.count_documents({"segmento_id": seg_id, "estado": "ocupada"}) > 0:
        raise HTTPException(status_code=400, detail="No se puede eliminar: el segmento tiene IP ocupadas")
    await db.segmentos.update_one({"id": seg_id}, {"$set": {"activo": False}})
    await db.ips.delete_many({"segmento_id": seg_id})
    await log_bitacora(user["username"], "Baja", "Segmentos", f"Eliminó segmento: {existing['nombre']}")
    return {"message": "Segmento eliminado"}


@api.post("/segmentos/{seg_id}/generar-ips")
async def generar_ips(seg_id: str, user: dict = Depends(require_roles("administrador", "tecnico"))):
    """RN-04: genera automáticamente las 254 direcciones IP del segmento."""
    seg = await db.segmentos.find_one({"id": seg_id})
    if not seg:
        raise HTTPException(status_code=404, detail="Segmento no encontrado")
    existentes = await db.ips.count_documents({"segmento_id": seg_id})
    if existentes > 0:
        raise HTTPException(status_code=400, detail="Este segmento ya tiene direcciones IP generadas")
    partes = seg["direccion_red"].split(".")
    if len(partes) != 4:
        raise HTTPException(status_code=400, detail="Dirección de red inválida (formato esperado x.x.x.0)")
    base = ".".join(partes[:3])
    nuevas = []
    for i in range(1, 255):  # RN-04: máximo 254 direcciones (.1 a .254)
        nuevas.append({
            "id": new_id(), "direccion": f"{base}.{i}", "segmento_id": seg_id,
            "estado": "disponible", "equipo_id": None, "created_at": now_iso(),
        })
    await db.ips.insert_many(nuevas)
    await log_bitacora(user["username"], "Generación IP", "Segmentos",
                       f"Generó 254 IP para {seg['nombre']}")
    return {"message": "254 direcciones IP generadas correctamente", "total": 254}


# ==================== DEPARTAMENTO-SEGMENTO (RN-01) ====================
@api.get("/departamento-segmento/{dep_id}")
async def get_dep_segmentos(dep_id: str, user: dict = Depends(get_current_user)):
    docs = await db.departamento_segmento.find({"departamento_id": dep_id}).to_list(1000)
    return {"segmento_ids": [d["segmento_id"] for d in docs]}


@api.post("/departamento-segmento")
async def set_dep_segmentos(data: DepSegInput, user: dict = Depends(require_roles("administrador"))):
    await db.departamento_segmento.delete_many({"departamento_id": data.departamento_id})
    for sid in data.segmento_ids:
        await db.departamento_segmento.insert_one({
            "id": new_id(), "departamento_id": data.departamento_id, "segmento_id": sid,
        })
    await log_bitacora(user["username"], "Modificación", "Autorización Segmentos",
                       f"Actualizó segmentos autorizados del departamento")
    return {"message": "Autorización actualizada"}


# ==================== EQUIPOS ====================
@api.get("/equipos")
async def list_equipos(search: str = "", tipo: str = "", page: int = 1, limit: int = 10,
                      all: bool = False, user: dict = Depends(get_current_user)):
    query = {"activo": True}
    if search:
        query["nombre"] = {"$regex": search, "$options": "i"}
    if tipo == "telefono":
        query["es_telefono_ip"] = True
    docs = await db.equipos.find(query).sort("created_at", -1).to_list(2000)
    deps = {d["id"]: d["nombre"] for d in await db.departamentos.find().to_list(1000)}
    tipos = {t["id"]: t["nombre"] for t in await db.tipo_dispositivo.find().to_list(1000)}
    for d in docs:
        clean(d)
        d["departamento_nombre"] = deps.get(d.get("departamento_id"), "-")
        d["tipo_nombre"] = tipos.get(d.get("tipo_id"), "-")
        ip = await db.ips.find_one({"equipo_id": d["id"], "estado": "ocupada"})
        d["ip_activa"] = ip["direccion"] if ip else None
    if all:
        return {"items": docs, "total": len(docs)}
    total = len(docs)
    skip = (page - 1) * limit
    return {"items": docs[skip:skip + limit], "total": total, "page": page,
            "pages": max(1, (total + limit - 1) // limit)}


@api.post("/equipos")
async def create_equipo(data: Equipo, user: dict = Depends(require_roles("administrador", "tecnico"))):
    doc = data.model_dump()
    doc.update({"id": new_id(), "activo": True, "created_at": now_iso()})
    await db.equipos.insert_one(doc)
    await log_bitacora(user["username"], "Alta", "Equipos", f"Registró equipo: {doc['nombre']}")
    return clean(doc)


@api.put("/equipos/{eq_id}")
async def update_equipo(eq_id: str, data: Equipo, user: dict = Depends(require_roles("administrador", "tecnico"))):
    if not await db.equipos.find_one({"id": eq_id}):
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    await db.equipos.update_one({"id": eq_id}, {"$set": data.model_dump()})
    await log_bitacora(user["username"], "Modificación", "Equipos", f"Editó equipo: {data.nombre}")
    return clean(await db.equipos.find_one({"id": eq_id}))


@api.delete("/equipos/{eq_id}")
async def delete_equipo(eq_id: str, user: dict = Depends(require_roles("administrador"))):
    existing = await db.equipos.find_one({"id": eq_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    if await db.ips.count_documents({"equipo_id": eq_id, "estado": "ocupada"}) > 0:
        raise HTTPException(status_code=400, detail="No se puede eliminar: el equipo tiene una IP asignada. Libérela primero")
    await db.equipos.update_one({"id": eq_id}, {"$set": {"activo": False}})
    await log_bitacora(user["username"], "Baja", "Equipos", f"Eliminó equipo: {existing['nombre']}")
    return {"message": "Equipo eliminado"}


# ==================== DIRECCIONES IP ====================
@api.get("/ips")
async def list_ips(segmento_id: str = "", estado: str = "", search: str = "",
                  page: int = 1, limit: int = 15, user: dict = Depends(get_current_user)):
    query = {}
    if segmento_id:
        query["segmento_id"] = segmento_id
    if estado:
        query["estado"] = estado
    if search:
        query["direccion"] = {"$regex": search, "$options": "i"}
    total = await db.ips.count_documents(query)
    skip = (page - 1) * limit
    docs = await db.ips.find(query).skip(skip).limit(limit).to_list(limit)
    segs = {s["id"]: s["nombre"] for s in await db.segmentos.find().to_list(1000)}
    equipos = {e["id"]: e["nombre"] for e in await db.equipos.find().to_list(2000)}
    # ordenar por último octeto
    docs.sort(key=lambda d: int(d["direccion"].split(".")[-1]) if d["direccion"].split(".")[-1].isdigit() else 0)
    for d in docs:
        clean(d)
        d["segmento_nombre"] = segs.get(d.get("segmento_id"), "-")
        d["equipo_nombre"] = equipos.get(d.get("equipo_id")) if d.get("equipo_id") else None
    return {"items": docs, "total": total, "page": page, "pages": max(1, (total + limit - 1) // limit)}


@api.put("/ips/{ip_id}/estado")
async def cambiar_estado_ip(ip_id: str, data: EstadoIPInput, user: dict = Depends(require_roles("administrador", "tecnico"))):
    ip = await db.ips.find_one({"id": ip_id})
    if not ip:
        raise HTTPException(status_code=404, detail="IP no encontrada")
    if data.estado not in ["disponible", "reservada"]:
        raise HTTPException(status_code=400, detail="Solo puede cambiar a 'disponible' o 'reservada'. Use Asignaciones para ocupar")
    if ip["estado"] == "ocupada":
        raise HTTPException(status_code=400, detail="IP ocupada. Libérela desde el módulo de Asignaciones")
    await db.ips.update_one({"id": ip_id}, {"$set": {"estado": data.estado}})
    await log_bitacora(user["username"], "Modificación", "Direcciones IP",
                       f"Cambió estado de {ip['direccion']} a {data.estado}")
    return {"message": "Estado actualizado"}


@api.get("/ips/{ip_id}/historial")
async def historial_ip(ip_id: str, user: dict = Depends(get_current_user)):
    asigs = await db.asignaciones.find({"ip_id": ip_id}).sort("fecha_asignacion", -1).to_list(500)
    equipos = {e["id"]: e["nombre"] for e in await db.equipos.find().to_list(2000)}
    for a in asigs:
        clean(a)
        a["equipo_nombre"] = equipos.get(a.get("equipo_id"), "-")
    return {"items": asigs}


# ==================== ASIGNACIONES ====================
@api.get("/asignaciones")
async def list_asignaciones(activas: bool = False, page: int = 1, limit: int = 10,
                           user: dict = Depends(get_current_user)):
    query = {"activo": True} if activas else {}
    total = await db.asignaciones.count_documents(query)
    skip = (page - 1) * limit
    docs = await db.asignaciones.find(query).sort("fecha_asignacion", -1).skip(skip).limit(limit).to_list(limit)
    equipos = {e["id"]: e["nombre"] for e in await db.equipos.find().to_list(2000)}
    ips = {i["id"]: i["direccion"] for i in await db.ips.find().to_list(20000)}
    for d in docs:
        clean(d)
        d["equipo_nombre"] = equipos.get(d.get("equipo_id"), "-")
        d["ip_direccion"] = ips.get(d.get("ip_id"), "-")
    return {"items": docs, "total": total, "page": page, "pages": max(1, (total + limit - 1) // limit)}


@api.post("/asignaciones")
async def asignar_ip(data: AsignacionInput, user: dict = Depends(require_roles("administrador", "tecnico"))):
    """Asigna una IP a un equipo validando las reglas de negocio."""
    ip = await db.ips.find_one({"id": data.ip_id})
    equipo = await db.equipos.find_one({"id": data.equipo_id})
    if not ip:
        raise HTTPException(status_code=404, detail="IP no encontrada")
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    # RN-02: una IP solo a un equipo
    if ip["estado"] == "ocupada":
        raise HTTPException(status_code=400, detail="RN-02: Esta IP ya está asignada a otro equipo")
    if ip["estado"] == "reservada":
        raise HTTPException(status_code=400, detail="Esta IP está reservada")
    # RN-05: cada equipo solo una IP activa
    if await db.ips.count_documents({"equipo_id": data.equipo_id, "estado": "ocupada"}) > 0:
        raise HTTPException(status_code=400, detail="RN-05: El equipo ya tiene una IP activa. Libérela o use Reasignar")
    # RN-01: el segmento debe estar autorizado para el departamento del equipo
    autorizado = await db.departamento_segmento.find_one({
        "departamento_id": equipo.get("departamento_id"), "segmento_id": ip["segmento_id"]})
    if not autorizado:
        raise HTTPException(status_code=400, detail="RN-01: El segmento no está autorizado para el departamento del equipo")
    await db.ips.update_one({"id": data.ip_id}, {"$set": {"estado": "ocupada", "equipo_id": data.equipo_id}})
    asig = {
        "id": new_id(), "ip_id": data.ip_id, "equipo_id": data.equipo_id,
        "fecha_asignacion": now_iso(), "fecha_liberacion": None, "activo": True,
        "usuario": user["username"],
    }
    await db.asignaciones.insert_one(asig)
    await log_bitacora(user["username"], "Asignación IP", "Asignaciones",
                       f"Asignó {ip['direccion']} a {equipo['nombre']}")
    return {"message": "IP asignada correctamente"}


@api.post("/asignaciones/{asig_id}/liberar")
async def liberar_ip(asig_id: str, user: dict = Depends(require_roles("administrador", "tecnico"))):
    asig = await db.asignaciones.find_one({"id": asig_id, "activo": True})
    if not asig:
        raise HTTPException(status_code=404, detail="Asignación activa no encontrada")
    ip = await db.ips.find_one({"id": asig["ip_id"]})
    await db.ips.update_one({"id": asig["ip_id"]}, {"$set": {"estado": "disponible", "equipo_id": None}})
    await db.asignaciones.update_one({"id": asig_id}, {"$set": {"activo": False, "fecha_liberacion": now_iso()}})
    await log_bitacora(user["username"], "Liberación IP", "Asignaciones",
                       f"Liberó {ip['direccion'] if ip else asig['ip_id']}")
    return {"message": "IP liberada correctamente"}


@api.post("/asignaciones/reasignar")
async def reasignar_ip(data: AsignacionInput, user: dict = Depends(require_roles("administrador", "tecnico"))):
    """Libera la IP activa del equipo (si existe) y asigna la nueva."""
    activa = await db.ips.find_one({"equipo_id": data.equipo_id, "estado": "ocupada"})
    if activa:
        asig = await db.asignaciones.find_one({"ip_id": activa["id"], "activo": True})
        if asig:
            await liberar_ip(asig["id"], user)
    return await asignar_ip(data, user)


# ==================== USUARIOS ====================
@api.get("/usuarios")
async def list_usuarios(search: str = "", page: int = 1, limit: int = 10, user: dict = Depends(require_roles("administrador"))):
    query = {}
    if search:
        query["$or"] = [{"nombre": {"$regex": search, "$options": "i"}},
                        {"username": {"$regex": search, "$options": "i"}}]
    total = await db.usuarios.count_documents(query)
    skip = (page - 1) * limit
    docs = await db.usuarios.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"items": [clean(d) for d in docs], "total": total, "page": page,
            "pages": max(1, (total + limit - 1) // limit)}


@api.post("/usuarios")
async def create_usuario(data: UsuarioInput, user: dict = Depends(require_roles("administrador"))):
    if not data.password:
        raise HTTPException(status_code=400, detail="La contraseña es obligatoria")
    if data.role not in ["administrador", "tecnico", "consulta"]:
        raise HTTPException(status_code=400, detail="Rol inválido")
    if await db.usuarios.find_one({"username": data.username.lower()}):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    doc = {
        "id": new_id(), "nombre": data.nombre, "username": data.username.lower(),
        "password_hash": hash_password(data.password), "role": data.role,
        "activo": data.activo, "created_at": now_iso(),
    }
    await db.usuarios.insert_one(doc)
    await log_bitacora(user["username"], "Alta", "Usuarios", f"Creó usuario: {data.username}")
    return clean(dict(doc))


@api.put("/usuarios/{uid}")
async def update_usuario(uid: str, data: UsuarioInput, user: dict = Depends(require_roles("administrador"))):
    existing = await db.usuarios.find_one({"id": uid})
    if not existing:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    update = {"nombre": data.nombre, "role": data.role, "activo": data.activo}
    if data.password:
        update["password_hash"] = hash_password(data.password)
    await db.usuarios.update_one({"id": uid}, {"$set": update})
    await log_bitacora(user["username"], "Modificación", "Usuarios", f"Editó usuario: {data.username}")
    return clean(await db.usuarios.find_one({"id": uid}))


@api.put("/usuarios/{uid}/password")
async def change_password(uid: str, data: PasswordInput, user: dict = Depends(get_current_user)):
    if user["role"] != "administrador" and user["id"] != uid:
        raise HTTPException(status_code=403, detail="No puede cambiar la contraseña de otro usuario")
    if not await db.usuarios.find_one({"id": uid}):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await db.usuarios.update_one({"id": uid}, {"$set": {"password_hash": hash_password(data.password)}})
    await log_bitacora(user["username"], "Modificación", "Usuarios", "Cambió contraseña")
    return {"message": "Contraseña actualizada"}


@api.delete("/usuarios/{uid}")
async def delete_usuario(uid: str, user: dict = Depends(require_roles("administrador"))):
    existing = await db.usuarios.find_one({"id": uid})
    if not existing:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if existing["username"] == "admin":
        raise HTTPException(status_code=400, detail="No se puede eliminar el administrador principal")
    await db.usuarios.update_one({"id": uid}, {"$set": {"activo": False}})
    await log_bitacora(user["username"], "Baja", "Usuarios", f"Desactivó usuario: {existing['username']}")
    return {"message": "Usuario desactivado"}


# ==================== BITÁCORA ====================
@api.get("/bitacora")
async def list_bitacora(search: str = "", modulo: str = "", page: int = 1, limit: int = 15,
                       user: dict = Depends(require_roles("administrador", "tecnico"))):
    query = {}
    if modulo:
        query["modulo"] = modulo
    if search:
        query["$or"] = [{"usuario": {"$regex": search, "$options": "i"}},
                        {"accion": {"$regex": search, "$options": "i"}},
                        {"detalle": {"$regex": search, "$options": "i"}}]
    total = await db.bitacora.count_documents(query)
    skip = (page - 1) * limit
    docs = await db.bitacora.find(query).sort("fecha", -1).skip(skip).limit(limit).to_list(limit)
    return {"items": [clean(d) for d in docs], "total": total, "page": page,
            "pages": max(1, (total + limit - 1) // limit)}


# ==================== DASHBOARD ====================
@api.get("/dashboard")
async def dashboard(user: dict = Depends(get_current_user)):
    total_segmentos = await db.segmentos.count_documents({"activo": True})
    total_departamentos = await db.departamentos.count_documents({"activo": True})
    total_equipos = await db.equipos.count_documents({"activo": True})
    total_ips = await db.ips.count_documents({})
    disponibles = await db.ips.count_documents({"estado": "disponible"})
    ocupadas = await db.ips.count_documents({"estado": "ocupada"})
    reservadas = await db.ips.count_documents({"estado": "reservada"})
    telefonos = await db.equipos.count_documents({"activo": True, "es_telefono_ip": True})

    segmentos = await db.segmentos.find({"activo": True}).to_list(1000)
    por_segmento = []
    for s in segmentos:
        tot = await db.ips.count_documents({"segmento_id": s["id"]})
        occ = await db.ips.count_documents({"segmento_id": s["id"], "estado": "ocupada"})
        disp = await db.ips.count_documents({"segmento_id": s["id"], "estado": "disponible"})
        por_segmento.append({
            "nombre": s["nombre"], "total": tot, "ocupadas": occ, "disponibles": disp,
            "porcentaje": round((occ / tot * 100), 1) if tot else 0,
        })

    equipos = {e["id"]: e["nombre"] for e in await db.equipos.find().to_list(2000)}
    ips = {i["id"]: i["direccion"] for i in await db.ips.find().to_list(20000)}
    ultimas = await db.asignaciones.find().sort("fecha_asignacion", -1).limit(5).to_list(5)
    for a in ultimas:
        clean(a)
        a["equipo_nombre"] = equipos.get(a.get("equipo_id"), "-")
        a["ip_direccion"] = ips.get(a.get("ip_id"), "-")
    actividad = [clean(b) for b in await db.bitacora.find().sort("fecha", -1).limit(8).to_list(8)]

    return {
        "cards": {
            "segmentos": total_segmentos, "departamentos": total_departamentos,
            "equipos": total_equipos, "ips": total_ips, "disponibles": disponibles,
            "ocupadas": ocupadas, "reservadas": reservadas, "telefonos": telefonos,
        },
        "pie": [
            {"name": "Disponibles", "value": disponibles, "color": "#10B981"},
            {"name": "Ocupadas", "value": ocupadas, "color": "#EF4444"},
            {"name": "Reservadas", "value": reservadas, "color": "#F59E0B"},
        ],
        "por_segmento": por_segmento,
        "ultimas_asignaciones": ultimas,
        "actividad": actividad,
    }


# ==================== EXPORTACIÓN ====================
async def _build_report_data(recurso: str):
    if recurso == "ips":
        segs = {s["id"]: s["nombre"] for s in await db.segmentos.find().to_list(1000)}
        equipos = {e["id"]: e["nombre"] for e in await db.equipos.find().to_list(2000)}
        docs = await db.ips.find().to_list(20000)
        rows = [{"Dirección IP": d["direccion"], "Segmento": segs.get(d.get("segmento_id"), "-"),
                 "Estado": d["estado"].capitalize(),
                 "Equipo": equipos.get(d.get("equipo_id"), "-") if d.get("equipo_id") else "-"} for d in docs]
        return "Reporte de Direcciones IP", ["Dirección IP", "Segmento", "Estado", "Equipo"], rows
    if recurso == "equipos":
        deps = {d["id"]: d["nombre"] for d in await db.departamentos.find().to_list(1000)}
        tipos = {t["id"]: t["nombre"] for t in await db.tipo_dispositivo.find().to_list(1000)}
        docs = await db.equipos.find({"activo": True}).to_list(2000)
        rows = [{"Nombre": d["nombre"], "Marca": d.get("marca", ""), "Modelo": d.get("modelo", ""),
                 "Tipo": tipos.get(d.get("tipo_id"), "-"), "Departamento": deps.get(d.get("departamento_id"), "-")} for d in docs]
        return "Reporte de Equipos", ["Nombre", "Marca", "Modelo", "Tipo", "Departamento"], rows
    if recurso == "asignaciones":
        equipos = {e["id"]: e["nombre"] for e in await db.equipos.find().to_list(2000)}
        ips = {i["id"]: i["direccion"] for i in await db.ips.find().to_list(20000)}
        docs = await db.asignaciones.find().sort("fecha_asignacion", -1).to_list(2000)
        rows = [{"IP": ips.get(d.get("ip_id"), "-"), "Equipo": equipos.get(d.get("equipo_id"), "-"),
                 "Asignación": d.get("fecha_asignacion", "")[:19].replace("T", " "),
                 "Estado": "Activa" if d.get("activo") else "Liberada",
                 "Usuario": d.get("usuario", "-")} for d in docs]
        return "Reporte de Asignaciones", ["IP", "Equipo", "Asignación", "Estado", "Usuario"], rows
    if recurso == "bitacora":
        docs = await db.bitacora.find().sort("fecha", -1).to_list(5000)
        rows = [{"Fecha": d.get("fecha", "")[:19].replace("T", " "), "Usuario": d.get("usuario", "-"),
                 "Acción": d.get("accion", ""), "Módulo": d.get("modulo", ""),
                 "Detalle": d.get("detalle", "")} for d in docs]
        return "Bitácora de Auditoría", ["Fecha", "Usuario", "Acción", "Módulo", "Detalle"], rows
    raise HTTPException(status_code=400, detail="Recurso no válido")


@api.get("/export/{recurso}/{formato}")
async def export_report(recurso: str, formato: str, user: dict = Depends(get_current_user)):
    title, columns, rows = await _build_report_data(recurso)
    if formato == "excel":
        content = build_excel(title, columns, rows)
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"SIGIP_{recurso}.xlsx"
    elif formato == "pdf":
        content = build_pdf(title, columns, rows)
        media = "application/pdf"
        filename = f"SIGIP_{recurso}.pdf"
    else:
        raise HTTPException(status_code=400, detail="Formato no válido")
    await log_bitacora(user["username"], "Exportación", recurso.capitalize(), f"Exportó reporte {formato.upper()}")
    return StreamingResponse(io.BytesIO(content), media_type=media,
                             headers={"Content-Disposition": f"attachment; filename={filename}"})


app.include_router(api)
app.add_middleware(
    CORSMiddleware, allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"], allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.usuarios.create_index("username", unique=True)
    await db.ips.create_index("direccion")
    await seed_all()


@app.on_event("shutdown")
async def shutdown():
    client.close()
