from fastapi import APIRouter
from fastapi.responses import FileResponse

from procedures.export_ips_pdf import exportar_ips_pdf

router = APIRouter(
    prefix="/api/ips/export",
    tags=["Exportación PDF"]
)


@router.get(
    "/pdf",
    summary="Exportar Direcciones IP a PDF",
    description="Genera un reporte PDF de las direcciones IP registradas."
)
def exportar_pdf():

    archivo = exportar_ips_pdf()

    return FileResponse(
        path=archivo,
        filename="Reporte_Direcciones_IP.pdf",
        media_type="application/pdf"
    )