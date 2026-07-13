from fastapi import APIRouter

from procedures.dashboard import obtener_dashboard

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def dashboard():

    return obtener_dashboard()