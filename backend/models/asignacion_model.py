from pydantic import BaseModel
from typing import Optional


# ==========================================
# LISTAR ASIGNACIONES
# ==========================================

class AsignacionFiltro(BaseModel):
    page: int = 1


# ==========================================
# OBTENER IPS DISPONIBLES
# ==========================================

class SegmentoIP(BaseModel):
    id_segmento: int


# ==========================================
# ASIGNAR DIRECCIÓN IP
# ==========================================

class AsignacionCreate(BaseModel):
    id_ip: int
    id_equipo: int
    id_usuario: int


# ==========================================
# LIBERAR ASIGNACIÓN
# ==========================================

class LiberarAsignacion(BaseModel):
    id_asignacion: int


# ==========================================
# REASIGNAR DIRECCIÓN IP
# ==========================================

class ReasignacionCreate(BaseModel):
    id_ip: int
    id_equipo: int
    id_usuario: int


# ==========================================
# RESPUESTA DE ASIGNACIÓN
# ==========================================

class AsignacionResponse(BaseModel):
    id: int
    ip_direccion: str
    equipo_nombre: str
    fecha_asignacion: Optional[str] = None
    fecha_liberacion: Optional[str] = None
    estado_asignacion: str
    activo: bool