from fastapi import APIRouter
from fastapi.responses import FileResponse

from procedures.export_equipos_pdf import exportar_equipos_pdf

router = APIRouter(
    prefix="/api/equipos/export",
    tags=["Exportación PDF"]
)


@router.get(
    "/pdf",
    summary="Exportar equipos a PDF",
    description="Genera un reporte PDF de los equipos registrados."
)
def exportar_pdf():

    archivo = exportar_equipos_pdf()

    return FileResponse(
        path=archivo,
        filename="Reporte_Equipos.pdf",
        media_type="application/pdf"
    )