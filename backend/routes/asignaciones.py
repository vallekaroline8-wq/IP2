from fastapi import APIRouter

from models.asignacion_model import AsignacionCreate
from procedures.asignaciones import (
    asignar_ip,
    obtener_asignaciones,
    obtener_equipos,
    obtener_ips_disponibles,
    obtener_segmentos,
    liberar_asignacion,
    exportar_asignaciones_excel,
    exportar_asignaciones_pdf
)

router = APIRouter(
    prefix="/api/asignaciones",
    tags=["Asignaciones"]
)


# ==========================================
# LISTAR ASIGNACIONES
# ==========================================

@router.get(
    "",
    summary="Listar Asignaciones",
    description="Obtiene todas las asignaciones de direcciones IP."
)
def listar_asignaciones(page: int = 1):
    return obtener_asignaciones(page)


# ==========================================
# COMBO EQUIPOS
# ==========================================

@router.get(
    "/equipos",
    summary="Listar Equipos",
    description="Obtiene los equipos activos."
)
def listar_equipos():
    return obtener_equipos()


# ==========================================
# COMBO SEGMENTOS
# ==========================================

@router.get(
    "/segmentos",
    summary="Listar Segmentos",
    description="Obtiene los segmentos activos."
)
def listar_segmentos():
    return obtener_segmentos()

# ==========================================
# LIBERAR ASIGNACIÓN
# ==========================================

@router.post("/{id_asignacion}/liberar")
def liberar(id_asignacion: int):
    return liberar_asignacion(id_asignacion)

# ==========================================
# COMBO IPS DISPONIBLES
# ==========================================

@router.get("/ips")
def listar_ips_disponibles(id_segmento: int):
    return obtener_ips_disponibles(id_segmento)

# ==========================================
# EXPORTAR ASIGNACIONES A EXCEL
# ==========================================

@router.get("/export/excel")
def exportar_excel():
    return exportar_asignaciones_excel()

# ==========================================# EXPORTAR ASIGNACIONES A PDF
# ==========================================

@router.get("/export/pdf")
def exportar_pdf():
    return exportar_asignaciones_pdf()

# ==========================================# ASIGNAR DIRECCIÓN IP
# ==========================================

@router.post("/")
def crear_asignacion(data: AsignacionCreate):
    return asignar_ip(
        data.id_ip,
        data.id_equipo,
        data.id_usuario
    )