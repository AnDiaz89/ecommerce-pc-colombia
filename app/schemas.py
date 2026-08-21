from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class CategoriaCrear(BaseModel):
    nombre: str = Field(
        min_length=2,
        max_length=100,
        examples=["Tarjetas gráficas"],
    )

    descripcion: str | None = Field(
        default=None,
        max_length=500,
        examples=["GPU para gaming, diseño y procesamiento gráfico."],
    )


class CategoriaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    creado_en: datetime

class ProductoCrear(BaseModel):
    nombre: str = Field(
        min_length=2,
        max_length=150,
        examples=["AMD Ryzen 5 5600G"],
    )

    descripcion: str | None = Field(
        default=None,
        max_length=2000,
        examples=["Procesador de 6 núcleos con gráficos integrados."],
    )

    sku: str = Field(
        min_length=3,
        max_length=50,
        examples=["CPU-RYZEN-5600G"],
    )

    precio: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=[589900],
    )

    stock: int = Field(
        default=0,
        ge=0,
        examples=[10],
    )

    marca: str = Field(
        min_length=2,
        max_length=100,
        examples=["AMD"],
    )

    categoria_id: int = Field(
        gt=0,
        examples=[1],
    )

    imagen_clave_s3: str | None = Field(
        default=None,
        max_length=500,
        examples=["productos/uuid-imagen.jpg"],
    )

    activo: bool = True


class ProductoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    sku: str
    precio: Decimal
    stock: int
    marca: str
    categoria_id: int
    imagen_clave_s3: str | None
    imagen_url: str | None = None
    activo: bool
    creado_en: datetime

class ProductoActualizar(BaseModel):
    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    descripcion: str | None = Field(
        default=None,
        max_length=2000,
    )

    sku: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    precio: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    stock: int | None = Field(
        default=None,
        ge=0,
    )

    marca: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    categoria_id: int | None = Field(
        default=None,
        gt=0,
    )

    imagen_clave_s3: str | None = Field(
        default=None,
        max_length=500,
    )

    activo: bool | None = None

class SolicitudRecomendacion(BaseModel):
    presupuesto: int = Field(
        ge=500_000,
        le=50_000_000,
        examples=[4_000_000],
    )

    necesidad: Literal[
        "gaming",
        "edicion_video",
        "ofimatica",
        "streaming",
        "diseno_3d",
    ]

    descripcion: str = Field(
        min_length=10,
        max_length=500,
        examples=[
            "Quiero jugar Warzone y Fortnite en 1080p."
        ],
    )

    resolucion: Literal[
        "1080p",
        "1440p",
        "4k",
    ] = "1080p"

    juegos: list[str] = Field(
        default_factory=list,
        max_length=10,
        examples=[["Valorant", "Fortnite", "Warzone"]],
    )


class ValidacionPresupuesto(BaseModel):
    presupuesto_viable: bool
    explicacion: str
    presupuesto_minimo_estimado: int
    alternativa_realista: str

class ComponenteEnsamble(BaseModel):
    producto_id: int
    nombre: str
    categoria: str
    precio: Decimal
    cantidad: int = Field(ge=1, le=4)


class EstimacionFPS(BaseModel):
    juego: str
    fps_minimo: int = Field(ge=0)
    fps_maximo: int = Field(ge=0)
    configuracion: str


class RecomendacionEnsamble(BaseModel):
    presupuesto_viable: bool
    explicacion: str
    presupuesto_solicitado: int
    total_estimado: Decimal
    componentes: list[ComponenteEnsamble]
    fps_estimados: list[EstimacionFPS]
    advertencias: list[str]