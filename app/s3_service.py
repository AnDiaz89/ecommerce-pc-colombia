import os
from uuid import uuid4

import boto3
from dotenv import load_dotenv
from fastapi import UploadFile


load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

if not AWS_REGION:
    raise RuntimeError("Falta AWS_REGION en el archivo .env")

if not S3_BUCKET_NAME:
    raise RuntimeError("Falta S3_BUCKET_NAME en el archivo .env")


s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
)


def subir_imagen(archivo: UploadFile) -> str:
    extension = os.path.splitext(archivo.filename or "")[1].lower()
    nombre_unico = f"{uuid4()}{extension}"
    clave_s3 = f"productos/{nombre_unico}"

    s3_client.upload_fileobj(
        Fileobj=archivo.file,
        Bucket=S3_BUCKET_NAME,
        Key=clave_s3,
        ExtraArgs={
            "ContentType": archivo.content_type or "application/octet-stream"
        },
    )

def generar_url_prefirmada(
    clave_s3: str,
    duracion_segundos: int = 900,
) -> str:
    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": clave_s3,
        },
        ExpiresIn=duracion_segundos,
    )

    return clave_s3