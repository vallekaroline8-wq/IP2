from fastapi import APIRouter

from procedures.asignaciones import (
    obtener_asignaciones,
    obtener_equipos,
    obtener_segmentos,
    liberar_asignacion
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

