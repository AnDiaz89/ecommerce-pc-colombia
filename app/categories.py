from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import obtener_db
from app.models import Categoria
from app.schemas import CategoriaCrear, CategoriaRespuesta


router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"],
)

SesionDB = Annotated[Session, Depends(obtener_db)]


@router.post(
    "",
    response_model=CategoriaRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_categoria(
    datos: CategoriaCrear,
    db: SesionDB,
):
    categoria = Categoria(
        nombre=datos.nombre.strip(),
        descripcion=(
            datos.descripcion.strip()
            if datos.descripcion
            else None
        ),
    )

    db.add(categoria)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una categoría con ese nombre",
        )

    db.refresh(categoria)
    return categoria


@router.get(
    "",
    response_model=list[CategoriaRespuesta],
)
def listar_categorias(db: SesionDB):
    consulta = select(Categoria).order_by(Categoria.nombre)
    categorias = db.scalars(consulta).all()

    return categorias

@router.get(
    "/{categoria_id}",
    response_model=CategoriaRespuesta,
)
def obtener_categoria(
    categoria_id: int,
    db: SesionDB,
):
    categoria = db.get(Categoria, categoria_id)

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )

    return categoria