# E-commerce Chat IA

API REST de e-commerce de zapatos con chat inteligente, construida con Clean Architecture. (Tuve un problema con git cuando comencé el proyecto, entonces no tengo commits para cada feature implementada, tuve que crear un solo commit diciendo todo lo hecho hasta el momento, pero después de solucionar el problema, si pude continuar con las buenas prácticas de commits y ramas)

## Descripcion Del Proyecto

Este proyecto implementa una API para:
- Gestionar productos de una tienda de zapatos.
- Consultar inventario mediante endpoints REST.
- Conversar con un asistente de IA que usa contexto conversacional.

La solucion separa responsabilidades en capas para mantener el codigo mantenible, testeable y escalable.

## Caracteristicas Principales

- Gestion de productos con validaciones de negocio.
- Persistencia con SQLite y SQLAlchemy.
- Chat con memoria de sesion.
- Integracion con Google Gemini (con fallback si no hay API key).
- API HTTP con FastAPI y documentacion automatica.
- Pruebas unitarias con pytest.
- Ejecucion local y con Docker.

## Arquitectura

El proyecto sigue Clean Architecture con tres capas:

- Domain: entidades, contratos de repositorio y excepciones de negocio.
- Application: casos de uso y DTOs.
- Infrastructure: FastAPI, repositorios SQLAlchemy, base de datos y proveedor de IA.

### Diagrama

```text
Cliente HTTP
   |
   v
FastAPI (Infrastructure)
   |
   v
Services (Application)
   |
   +--> Repositories (Infrastructure -> SQLAlchemy/SQLite)
   |
   +--> AI Provider (Infrastructure -> Gemini)
   |
   v
Domain (Entities, Rules, Interfaces)
```

## Tecnologias Utilizadas

- Python 3.11
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- Google Generative AI (Gemini)
- Pytest
- Docker y Docker Compose

## Estructura Del Proyecto

```text
e-commerce-chat-ai/
├── src/
│   ├── domain/
│   ├── application/
│   └── infrastructure/
│       ├── api/
│       ├── db/
│       ├── repositories/
│       └── llm_providers/
├── tests/
├── data/
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

## Instalacion

### Requisitos

- Python 3.10 o superior (recomendado 3.11)
- pip
- Docker Desktop (opcional, para ejecucion con contenedores)

### Pasos

1. Crear y activar entorno virtual:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

## Configuracion

Crear archivo `.env` en la raiz del proyecto con:

```env
GEMINI_API_KEY=tu_api_key_aqui
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development
```

Notas:
- Si no defines `GEMINI_API_KEY`, el servicio de IA usa respuesta de fallback.
- `DATABASE_URL` por defecto apunta a SQLite local en `data/`.

## Uso

### Ejecutar En Local

```powershell
python -m uvicorn src.infrastructure.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Documentacion:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints Principales

- `GET /` informacion general de la API.
- `GET /products` lista productos.
- `GET /products/{product_id}` obtiene producto por ID.
- `POST /chat` procesa mensaje de chat.
- `GET /chat/history/{session_id}` historial por sesion.
- `DELETE /chat/history/{session_id}` elimina historial de sesion.
- `GET /health` health check.

### Ejemplos De Requests

1. Listar productos:

```bash
curl http://localhost:8000/products
```

2. Obtener producto por ID:

```bash
curl http://localhost:8000/products/1
```

3. Enviar mensaje al chat:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"user123","message":"Busco zapatos para correr"}'
```

4. Consultar historial:

```bash
curl "http://localhost:8000/chat/history/user123?limit=10"
```

## Testing

Ejecutar todos los tests:

```powershell
python -m pytest
```

Ejecutar un archivo puntual:

```powershell
python -m pytest tests/test_entities.py
python -m pytest tests/test_services.py
```

## Docker

### Construir Y Levantar

```powershell
docker compose up --build
```

### Ejecutar En Background

```powershell
docker compose up -d --build
```

### Ver Logs

```powershell
docker compose logs -f
```

### Detener Servicios

```powershell
docker compose down
```

## Estado Actual

- API FastAPI implementada.
- Persistencia SQLite con seed inicial.
- Repositorios SQLAlchemy implementados.
- ChatService y ProductService implementados.
- Tests de entidades y servicios implementados.
