from fastapi import APIRouter, Body, Query, Depends
from dependencies.auth_dependency import obtener_usuario_actual

from procedures.ips import obtener_ips, actualizar_estado_ip, obtener_historial_ip

router = APIRouter(prefix="/api/ips", tags=["IPs"])


@router.get("", summary="Listar IPs", description="Obtiene las IPs desde tbl_ip.")
def listar_ips(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=5000),
    search: str = Query("", description="Texto a buscar en la dirección IP"),
    segmento_id: int | None = Query(None),
    estado: str | None = Query(None),
):
    return obtener_ips(page=page, limit=limit, search=search, segmento_id=segmento_id, estado=estado)


@router.put("/{id_ip}/estado", summary="Cambiar estado de IP", description="Actualiza el estado de una IP en tbl_ip.")
def cambiar_estado_ip(id_ip: int, estado: str = Body(..., embed=True), usuario_actual: dict = Depends(obtener_usuario_actual)):
    return actualizar_estado_ip(id_ip, estado, usuario_actual["id_usuario"])


@router.get("/{id_ip}/historial", summary="Historial de IP", description="Obtiene el historial de asignaciones de una IP.")
def historial_ip(id_ip: int):
    return obtener_historial_ip(id_ip)
