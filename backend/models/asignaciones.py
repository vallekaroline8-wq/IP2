from pydantic import BaseModel, Field


# ==========================================
# CREAR ASIGNACIÓN
# ==========================================

class AsignacionCreate(BaseModel):
    id_equipo: int = Field(
        ...,
        gt=0,
        description="ID del equipo"
    )

    id_ip: int = Field(
        ...,
        gt=0,
        description="ID de la dirección IP"
    )


# ==========================================
# REASIGNAR IP
# ==========================================

class ReasignacionCreate(BaseModel):
    id_equipo: int = Field(
        ...,
        gt=0,
        description="ID del equipo"
    )

    id_ip: int = Field(
        ...,
        gt=0,
        description="Nueva dirección IP"
    )


# ==========================================
# LIBERAR ASIGNACIÓN
# ==========================================

class LiberarAsignacion(BaseModel):
    id_asignacion: int = Field(
        ...,
        gt=0,
        description="ID de la asignación"
    )


# ==========================================
# FILTRO DE IPS DISPONIBLES
# ==========================================

class IpDisponibleFiltro(BaseModel):
    id_segmento: int = Field(
        ...,
        gt=0,
        description="ID del segmento"
    )

    estado: str = Field(
        default="disponible",
        description="Estado de las IPs a consultar"
    )

    limit: int = Field(
        default=300,
        gt=0,
        description="Cantidad máxima de registros"
    )