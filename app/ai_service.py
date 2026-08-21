import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Categoria, Producto
from app.schemas import (
    RecomendacionEnsamble,
    SolicitudRecomendacion,
    ValidacionPresupuesto,
)


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "Falta GEMINI_API_KEY en el archivo .env"
    )


cliente = genai.Client(api_key=GEMINI_API_KEY)


def probar_gemini() -> str:
    respuesta = cliente.models.generate_content(
        model="gemini-3.6-flash",
        contents=(
            "Responde únicamente con esta frase: "
            "Gemini conectado correctamente"
        ),
    )

    return respuesta.text or ""


def validar_presupuesto_con_gemini(
    solicitud: SolicitudRecomendacion,
) -> ValidacionPresupuesto:
    prompt = f"""
Actúa como asesor experto en hardware para Colombia.

Analiza si el presupuesto coincide con la necesidad indicada.
Los valores monetarios están expresados en pesos colombianos (COP).

Presupuesto: {solicitud.presupuesto} COP
Necesidad: {solicitud.necesidad}
Descripción: {solicitud.descripcion}
Resolución: {solicitud.resolucion}
Juegos: {", ".join(solicitud.juegos) or "No indicados"}

Reglas:
- Sé realista con precios del mercado colombiano.
- No prometas rendimiento exacto.
- Si el presupuesto es insuficiente, explica el motivo amablemente.
- Sugiere una alternativa realista sin superar el presupuesto.
- El presupuesto mínimo estimado debe ser un entero en COP.
"""

    respuesta = cliente.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ValidacionPresupuesto,
            temperature=0.2,
        ),
    )

    if not respuesta.text:
        raise RuntimeError(
            "Gemini devolvió una respuesta vacía"
        )

    datos = json.loads(respuesta.text)
    return ValidacionPresupuesto.model_validate(datos)

def obtener_inventario_para_ia(
    db: Session,
) -> list[dict]:
    consulta = (
        select(Producto, Categoria.nombre)
        .join(
            Categoria,
            Producto.categoria_id == Categoria.id,
        )
        .where(Producto.activo.is_(True))
        .where(Producto.stock > 0)
        .order_by(Categoria.nombre, Producto.precio)
    )

    filas = db.execute(consulta).all()

    return [
        {
            "producto_id": producto.id,
            "nombre": producto.nombre,
            "categoria": categoria_nombre,
            "precio": float(producto.precio),
            "stock": producto.stock,
            "marca": producto.marca,
            "descripcion": producto.descripcion,
        }
        for producto, categoria_nombre in filas
    ]

def recomendar_ensamble_con_gemini(
    solicitud: SolicitudRecomendacion,
    db: Session,
) -> RecomendacionEnsamble:
    inventario = obtener_inventario_para_ia(db)

    if not inventario:
        raise ValueError(
            "No hay productos activos con stock disponible"
        )

    inventario_json = json.dumps(
        inventario,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
Actúa como asesor experto en ensambles de computadores
para el mercado colombiano.

Debes recomendar un ensamble usando EXCLUSIVAMENTE los productos
del inventario proporcionado. No inventes productos, precios,
IDs ni disponibilidad.

SOLICITUD:
- Presupuesto: {solicitud.presupuesto} COP
- Necesidad: {solicitud.necesidad}
- Descripción: {solicitud.descripcion}
- Resolución: {solicitud.resolucion}
- Juegos: {", ".join(solicitud.juegos) or "No indicados"}

INVENTARIO REAL:
{inventario_json}

REGLAS:
1. No superes el presupuesto solicitado.
2. Selecciona como máximo una unidad por componente,
   salvo memoria o almacenamiento cuando tenga sentido.
3. Usa solamente producto_id, nombre, categoría y precio
   presentes en el inventario.
4. Si faltan categorías esenciales, entrega el mejor ensamble
   parcial y explica lo que falta en advertencias.
5. No declares el ensamble completo si faltan piezas esenciales.
6. Para FPS, devuelve rangos prudentes, nunca cifras exactas.
7. Si no hay GPU dedicada, acláralo en las advertencias.
8. El total debe corresponder a la suma de los componentes.
9. Escribe textos claros y amables en español.
"""

    respuesta = cliente.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RecomendacionEnsamble,
            temperature=0.1,
        ),
    )

    if not respuesta.text:
        raise RuntimeError(
            "Gemini devolvió una respuesta vacía"
        )

    datos = json.loads(respuesta.text)
    return RecomendacionEnsamble.model_validate(datos)