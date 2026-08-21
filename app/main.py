from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.ai import router as ia_router
from app.categories import router as categorias_router
from app.database import comprobar_conexion
from app.products import router as productos_router
from app.s3_service import subir_imagen



app = FastAPI(
    title="E-commerce PC Colombia API",
    version="0.1.0",
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(directory="app/templates")

app.include_router(categorias_router)
app.include_router(productos_router)
app.include_router(ia_router)

@app.get("/", response_class=HTMLResponse)
def mostrar_inicio(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/health")
def verificar_salud():
    return {"estado": "ok"}

@app.get("/health/database")
def verificar_base_de_datos():
    try:
        comprobar_conexion()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no disponible",
        )

    return {
        "estado": "ok",
        "base_de_datos": "conectada",
    }

@app.post("/imagenes")
def cargar_imagen(archivo: UploadFile = File(...)):
    tipos_permitidos = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if archivo.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imágenes JPG, PNG o WebP",
        )

    try:
        clave_s3 = subir_imagen(archivo)
    except Exception as error:
        print(f"ERROR S3: {type(error).name}: {error}")
        raise HTTPException(
            status_code=500,
            detail="No fue posible subir la imagen a S3",
        ) from error

    return {
        "mensaje": "Imagen subida correctamente",
        "clave_s3": clave_s3,
    }