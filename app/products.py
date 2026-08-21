from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import obtener_db
from app.models import Categoria, Producto
from app.s3_service import generar_url_prefirmada
from app.schemas import (
    ProductoActualizar,
    ProductoCrear,
    ProductoRespuesta,
)


router = APIRouter(
    prefix="/productos",
    tags=["Productos"],
)

SesionDB = Annotated[Session, Depends(obtener_db)]

def construir_respuesta_producto(
    producto: Producto,
) -> ProductoRespuesta:
    imagen_url = None

    if producto.imagen_clave_s3:
        imagen_url = generar_url_prefirmada(
            producto.imagen_clave_s3
        )

    return ProductoRespuesta(
        id=producto.id,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        sku=producto.sku,
        precio=producto.precio,
        stock=producto.stock,
        marca=producto.marca,
        categoria_id=producto.categoria_id,
        imagen_clave_s3=producto.imagen_clave_s3,
        imagen_url=imagen_url,
        activo=producto.activo,
        creado_en=producto.creado_en,
    )

@router.post(
    "",
    response_model=ProductoRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_producto(
    datos: ProductoCrear,
    db: SesionDB,
):
    categoria = db.get(Categoria, datos.categoria_id)

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La categoría indicada no existe",
        )

    producto = Producto(
        nombre=datos.nombre.strip(),
        descripcion=(
            datos.descripcion.strip()
            if datos.descripcion
            else None
        ),
        sku=datos.sku.strip().upper(),
        precio=datos.precio,
        stock=datos.stock,
        marca=datos.marca.strip(),
        categoria_id=datos.categoria_id,
        imagen_clave_s3=(
            datos.imagen_clave_s3.strip()
            if datos.imagen_clave_s3
            else None
        ),
        activo=datos.activo,
    )

    db.add(producto)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un producto con ese SKU",
        )
    db.refresh(producto)
    return construir_respuesta_producto(producto)


@router.get(
    "",
    response_model=list[ProductoRespuesta],
)
def listar_productos(
    db: SesionDB,
    categoria_id: int | None = None,
    solo_activos: bool = True,
):
    consulta = select(Producto)

    if categoria_id is not None:
        consulta = consulta.where(
            Producto.categoria_id == categoria_id
        )

    if solo_activos:  
        consulta = consulta.where(
            Producto.activo.is_(True)
        )

    consulta = consulta.order_by(Producto.nombre)

    productos = db.scalars(consulta).all()

    return [
    construir_respuesta_producto(producto)
    for producto in productos
]

@router.get(
    "/{producto_id}",
    response_model=ProductoRespuesta,
)
def obtener_producto(
    producto_id: int,
    db: SesionDB,
):
    producto = db.get(Producto, producto_id)

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    return construir_respuesta_producto(producto)

@router.patch(
    "/{producto_id}",
    response_model=ProductoRespuesta,
)
def actualizar_producto(
    producto_id: int,
    datos: ProductoActualizar,
    db: SesionDB,
):
    producto = db.get(Producto, producto_id)

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    cambios = datos.model_dump(exclude_unset=True)

    if "categoria_id" in cambios:
        categoria = db.get(
            Categoria,
            cambios["categoria_id"],
        )

        if categoria is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría indicada no existe",
            )

    campos_texto = {
        "nombre",
        "descripcion",
        "sku",
        "marca",
        "imagen_clave_s3",
    }

    for campo, valor in cambios.items():
        if campo in campos_texto and isinstance(valor, str):
            valor = valor.strip()

        if campo == "sku" and isinstance(valor, str):
            valor = valor.upper()

        setattr(producto, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un producto con ese SKU",
        )

    db.refresh(producto)
    return construir_respuesta_producto(producto)

@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_producto(
    producto_id: int,
    db: SesionDB,
):
    producto = db.get(Producto, producto_id)

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    producto.activo = False
    db.commit()

    return None