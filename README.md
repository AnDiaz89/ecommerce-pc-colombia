## Funcionalidades implementadas

- Catálogo de productos.
- Clasificación de productos por categorías.
- Gestión de stock y precios.
- API REST con FastAPI.
- Base de datos PostgreSQL.
- Almacenamiento de imágenes en AWS S3.
- Interfaz oscura y responsiva.
- Animaciones y efectos hover.
- Menú para dispositivos móviles.
- Asistente de inteligencia artificial.
- Validación de presupuesto.
- Recomendación de ensambles de PC.
- Estimación de FPS para videojuegos.
- Carrito de compras animado tipo slide-over.
- Generación de cotizaciones mediante WhatsApp.

## Tecnologías utilizadas

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL
- Pydantic
- Boto3

### Frontend

- HTML5
- Tailwind CSS
- Alpine.js
- JavaScript

### Servicios externos

- AWS S3
- AWS RDS
- WhatsApp
- Servicio de inteligencia artificial

## Estructura del proyecto

text
ecommerce-pc-colombia/
├── app/
│   ├── static/
│   ├── templates/
│   │   └── index.html
│   ├── __init__.py
│   ├── ai.py
│   ├── ai_service.py
│   ├── categories.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── products.py
│   ├── s3_service.py
│   └── schemas.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md


> El archivo .env se utiliza solamente en el entorno local y no debe subirse al repositorio.

## Instalación local

### 1. Clonar el repositorio

bash
git clone URL_DEL_REPOSITORIO
cd ecommerce-pc-colombia


### 2. Crear el entorno virtual

En Windows:

powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1


En Linux o macOS:

bash
python3 -m venv .venv
source .venv/bin/activate


### 3. Instalar las dependencias

bash
pip install -r requirements.txt


### 4. Configurar las variables de entorno

Crea un archivo .env en la raíz del proyecto tomando como referencia .env.example.

Ejemplo:

env
DATABASE_URL=postgresql://usuario:contrasena@host:5432/base_de_datos

AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_REGION=us-east-1
AWS_BUCKET_NAME=nombre_del_bucket

WHATSAPP_NUMBER=573001234567

AI_API_KEY=tu_clave_del_servicio_de_ia


Los nombres exactos de las variables pueden variar según la configuración interna del proyecto.

Nunca publiques contraseñas, claves de AWS, tokens de IA ni credenciales de PostgreSQL.

### 5. Ejecutar el servidor

Desde la raíz del proyecto:

bash
uvicorn app.main:app --reload


La aplicación estará disponible en:

text
http://127.0.0.1:8000


Documentación interactiva de la API:

text
http://127.0.0.1:8000/docs


## Roadmap

- [x] *HITO 1:* configuración del entorno local, entorno virtual, FastAPI “Hola Mundo” y estructura de carpetas.
- [x] *HITO 2:* configuración y conexión segura con AWS S3 y AWS RDS con PostgreSQL.
- [x] *HITO 3:* modelos de base de datos para productos, categorías, stock y precios; endpoints básicos.
- [x] *HITO 4:* frontend base con Tailwind CSS, paleta tecnológica oscura, animaciones, efectos hover y menú responsivo.
- [x] *HITO 5:* módulo de IA con chatbot, animación de carga, validación de presupuesto, recomendación de ensamble y estimador de FPS.
- [x] *HITO 6:* carrito de compras tipo slide-over y generación de cotizaciones por WhatsApp.
- [ ] *HITO 7:* integración de la pasarela de pagos en entorno Sandbox.
- [ ] *HITO 8:* despliegue final.

## API

Los endpoints disponibles pueden consultarse mediante Swagger UI:

text
http://127.0.0.1:8000/docs


También está disponible la documentación ReDoc:

text
http://127.0.0.1:8000/redoc


## Seguridad

Este proyecto utiliza variables de entorno para proteger información sensible.

No deben subirse al repositorio:

- Archivo .env.
- Entorno virtual .venv.
- Credenciales de AWS.
- Contraseñas de PostgreSQL.
- Claves de APIs externas.
- Tokens de acceso.
- Archivos de configuración con secretos.

## Próximos pasos

- Corregir el detalle visual pendiente del botón del carrito.
- Integrar una pasarela de pagos en Sandbox.
- Agregar pruebas automatizadas.
- Preparar el despliegue del backend.
- Configurar la base de datos de producción.
- Realizar el despliegue final.

## Autor

Desarrollado por *Andres* como proyecto de e-commerce tecnológico.