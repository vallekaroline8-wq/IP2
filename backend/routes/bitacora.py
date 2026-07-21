from fastapi import APIRouter, Query
from procedures.bitacora import obtener_bitacora

router = APIRouter(prefix="/api/bitacora", tags=["Bitácora"])

@router.get("", summary="Listar Bitácora", description="Obtiene los registros de la bitácora de auditoría.")
def listar_bitacora(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=5000),
    search: str = Query("", description="Texto a buscar en la bitácora")
):
    return obtener_bitacora(page=page, limit=limit, search=search)
