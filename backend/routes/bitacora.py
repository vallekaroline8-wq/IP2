from fastapi import APIRouter, Query

from procedures.bitacoramodulo import obtener_bitacora

router = APIRouter(
    prefix="/api/bitacora",
    tags=["Bitácora"]
)


@router.get(
    "",
    summary="Listar Bitácora",
    description="Obtiene el historial de acciones registradas en el sistema."
)
def listar_bitacora(
    search: str = Query(default=""),
    page: int = Query(default=1, ge=1)
):
    return obtener_bitacora(search, page)