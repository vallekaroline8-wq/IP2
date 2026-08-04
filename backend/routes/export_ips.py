from fastapi import APIRouter

from procedures.export_ips import exportar_ips_excel

router = APIRouter(
    prefix="/api/ips/export",
    tags=["Exportación Direcciones IP"]
)


@router.get(
    "/excel",
    summary="Exportar Direcciones IP a Excel"
)
def exportar_excel():
    return exportar_ips_excel()