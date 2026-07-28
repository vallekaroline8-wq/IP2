from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from procedures.export_bitacora import exportar_bitacora_excel, exportar_bitacora_pdf

router = APIRouter(
    prefix="/api/bitacora/export",
    tags=["Exportación Bitácora"]
)


@router.get(
    "/excel",
    summary="Exportar Bitácora a Excel"
)
def exportar_excel():
    data = exportar_bitacora_excel()
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Reporte_Bitacora_SIGIP.xlsx"},
    )


@router.get(
    "/pdf",
    summary="Exportar Bitácora a PDF"
)
def exportar_pdf():
    data = exportar_bitacora_pdf()
    return StreamingResponse(
        iter([data]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Reporte_Bitacora_SIGIP.pdf"},
    )
