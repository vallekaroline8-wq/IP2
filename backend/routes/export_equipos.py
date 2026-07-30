from fastapi import APIRouter

from procedures.export_equipos import exportar_equipos_excel

router = APIRouter(
    prefix="/api/equipos/export",
    tags=["Exportación Equipos"]
)


@router.get(
    "/excel",
    summary="Exportar Equipos a Excel"
)
def exportar_excel():
    return exportar_equipos_excel()