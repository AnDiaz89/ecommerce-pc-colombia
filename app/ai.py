from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai_service import (
    recomendar_ensamble_con_gemini,
    validar_presupuesto_con_gemini,
)
from app.database import obtener_db
from app.schemas import (
    RecomendacionEnsamble,
    SolicitudRecomendacion,
    ValidacionPresupuesto,
)

router = APIRouter(
    prefix="/ia",
    tags=["Inteligencia artificial"],
)

SesionDB = Annotated[Session, Depends(obtener_db)]


@router.post(
    "/validar-presupuesto",
    response_model=ValidacionPresupuesto,
)
def validar_presupuesto(
    solicitud: SolicitudRecomendacion,
):
    try:
        return validar_presupuesto_con_gemini(solicitud)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de IA no está disponible",
        )

@router.post(
    "/recomendar-ensamble",
    response_model=RecomendacionEnsamble,
)
def recomendar_ensamble(
    solicitud: SolicitudRecomendacion,
    db: SesionDB,
):
    try:
        return recomendar_ensamble_con_gemini(
            solicitud,
            db,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No fue posible generar la recomendación",
        )