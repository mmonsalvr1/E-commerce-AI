"""Aplicación FastAPI para el e-commerce con chat inteligente."""

from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.application.chat_service import ChatService
from src.application.dtos import (
    ChatHistoryDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ProductDTO,
)
from src.application.product_service import ProductService
from src.domain.exceptions import ChatServiceError, ProductNotFoundError
from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.repositories.product_repository import SQLProductRepository

app = FastAPI(
    title="E-commerce con Chat IA",
    description=(
        "API REST de e-commerce de zapatos con chat inteligente usando Clean Architecture."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    """Ejecuta inicializacion de base de datos al iniciar la API.

    Returns:
        None
    """
    init_db()


def _build_product_service(db: Session) -> ProductService:
    """Construye una instancia de ProductService.

    Args:
        db (Session): Sesion de base de datos activa.

    Returns:
        ProductService: Servicio de productos listo para uso.
    """
    return ProductService(SQLProductRepository(db))


def _build_chat_service(db: Session) -> ChatService:
    """Construye una instancia de ChatService con dependencias concretas.

    Args:
        db (Session): Sesion de base de datos activa.

    Returns:
        ChatService: Servicio de chat listo para procesar mensajes.
    """
    product_repository = SQLProductRepository(db)
    chat_repository = SQLChatRepository(db)
    ai_service = GeminiService()
    return ChatService(product_repository, chat_repository, ai_service)


@app.get("/", summary="Información básica de la API")
def root() -> dict:
    """Retorna informacion general de la API y endpoints disponibles.

    Returns:
        dict: Metadatos basicos del servicio y rutas principales.
    """
    return {
        "name": "E-commerce con Chat IA",
        "version": app.version,
        "description": app.description,
        "endpoints": [
            "GET /products",
            "GET /products/{product_id}",
            "POST /chat",
            "GET /chat/history/{session_id}",
            "DELETE /chat/history/{session_id}",
            "GET /health",
        ],
    }


@app.get(
    "/products",
    response_model=List[ProductDTO],
    summary="Listar productos",
)
def get_products(db: Session = Depends(get_db)) -> List[ProductDTO]:
    """Obtiene la lista completa de productos registrados.

    Args:
        db (Session): Sesion inyectada por dependencia de FastAPI.

    Returns:
        List[ProductDTO]: Coleccion de productos disponibles en catalogo.

    Raises:
        HTTPException: Si ocurre un error inesperado en infraestructura.
    """
    try:
        product_service = _build_product_service(db)
        return product_service.get_all_products()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo productos: {exc}",
        ) from exc


@app.get(
    "/products/{product_id}",
    response_model=ProductDTO,
    summary="Obtener producto por ID",
)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
    """Obtiene un producto por su identificador unico.

    Args:
        product_id (int): Identificador del producto.
        db (Session): Sesion inyectada por dependencia de FastAPI.

    Returns:
        ProductDTO: Producto encontrado.

    Raises:
        HTTPException: Con codigo 404 cuando el producto no existe.
    """
    product_service = _build_product_service(db)

    try:
        return product_service.get_product_by_id(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@app.post(
    "/chat",
    response_model=ChatMessageResponseDTO,
    summary="Procesar mensaje de chat",
)
async def process_chat(
    request: ChatMessageRequestDTO,
    db: Session = Depends(get_db),
) -> ChatMessageResponseDTO:
    """Procesa un mensaje de chat y retorna respuesta del asistente.

    Args:
        request (ChatMessageRequestDTO): Payload con session_id y mensaje.
        db (Session): Sesion inyectada por dependencia de FastAPI.

    Returns:
        ChatMessageResponseDTO: Resultado del intercambio conversacional.

    Raises:
        HTTPException: Si falla el servicio de chat o ocurre un error interno.
    """
    chat_service = _build_chat_service(db)

    try:
        return await chat_service.process_message(request)
    except ChatServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado procesando el chat: {exc}",
        ) from exc


@app.get(
    "/chat/history/{session_id}",
    response_model=List[ChatHistoryDTO],
    summary="Obtener historial de chat",
)
def get_chat_history(
    session_id: str,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db),
) -> List[ChatHistoryDTO]:
    """Obtiene historial conversacional de una sesion.

    Args:
        session_id (str): Identificador de la sesion.
        limit (Optional[int]): Maximo de mensajes a retornar.
        db (Session): Sesion inyectada por dependencia de FastAPI.

    Returns:
        List[ChatHistoryDTO]: Mensajes historicos de la sesion.

    Raises:
        HTTPException: Si ocurre un error al consultar el historial.
    """
    try:
        chat_service = _build_chat_service(db)
        return chat_service.get_session_history(session_id, limit=limit)
    except ChatServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@app.delete(
    "/chat/history/{session_id}",
    summary="Eliminar historial de chat",
)
def delete_chat_history(session_id: str, db: Session = Depends(get_db)) -> dict:
    """Elimina todo el historial de una sesion de chat.

    Args:
        session_id (str): Identificador de la sesion.
        db (Session): Sesion inyectada por dependencia de FastAPI.

    Returns:
        dict: Identificador de sesion y numero de mensajes eliminados.

    Raises:
        HTTPException: Si ocurre un error durante la eliminacion.
    """
    try:
        chat_service = _build_chat_service(db)
        deleted_messages = chat_service.clear_session_history(session_id)
        return {
            "session_id": session_id,
            "deleted_messages": deleted_messages,
        }
    except ChatServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@app.get("/health", summary="Health check")
def health_check() -> dict:
    """Retorna estado de salud de la API.

    Returns:
        dict: Estado operacional y timestamp UTC en formato ISO.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }
