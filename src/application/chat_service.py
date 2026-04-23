"""Servicio de aplicacion para gestionar conversaciones con IA."""

from datetime import datetime
from typing import Any, List, Optional
import inspect

from src.application.dtos import (
    ChatHistoryDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
)
from src.domain.entities import ChatContext, ChatMessage
from src.domain.exceptions import ChatServiceError
from src.domain.repositories import IChatRepository, IProductRepository


class ChatService:
    """Servicio de aplicacion para el caso de uso de chat inteligente.

    Esta clase orquesta productos, historial y proveedor de IA para
    construir respuestas contextuales.

    Attributes:
        product_repository (IProductRepository): Repositorio de productos.
        chat_repository (IChatRepository): Repositorio de historial de chat.
        ai_service (Any): Adaptador del proveedor de IA.
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service: Any,
    ):
        """Inicializa el servicio con dependencias inyectadas.

        Args:
            product_repository (IProductRepository): Repositorio de productos.
            chat_repository (IChatRepository): Repositorio de chat.
            ai_service (Any): Servicio de IA para generacion de respuesta.
        """
        self.product_repository = product_repository
        self.chat_repository = chat_repository
        self.ai_service = ai_service

    async def process_message(
        self, request: ChatMessageRequestDTO
    ) -> ChatMessageResponseDTO:
        """Procesa un mensaje de usuario y retorna respuesta contextualizada.

        Flujo principal:
            1. Obtiene productos disponibles.
            2. Recupera historial reciente de la sesion.
            3. Construye contexto conversacional.
            4. Solicita respuesta al proveedor de IA.
            5. Persiste mensaje de usuario y respuesta.

        Args:
            request (ChatMessageRequestDTO): Mensaje de entrada del usuario.

        Returns:
            ChatMessageResponseDTO: Resultado del intercambio de chat.

        Raises:
            ChatServiceError: Si ocurre un error durante el proceso.
        """
        try:
            products = self.product_repository.get_all()
            history = self.chat_repository.get_recent_messages(
                request.session_id, count=6
            )
            context = ChatContext(messages=history, max_messages=6)

            assistant_response = self.ai_service.generate_response(
                request.message,
                products,
                context,
            )
            if inspect.isawaitable(assistant_response):
                assistant_response = await assistant_response

            timestamp = datetime.utcnow()

            user_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=timestamp,
            )
            assistant_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=assistant_response,
                timestamp=timestamp,
            )

            self.chat_repository.save_message(user_message)
            self.chat_repository.save_message(assistant_message)

            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=assistant_response,
                timestamp=timestamp,
            )
        except Exception as exc:
            raise ChatServiceError(f"Error procesando mensaje de chat: {exc}") from exc

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatHistoryDTO]:
        """Obtiene historial de una sesion y lo mapea a DTOs.

        Args:
            session_id (str): Identificador de la sesion.
            limit (Optional[int]): Limite de mensajes a retornar.

        Returns:
            List[ChatHistoryDTO]: Historial conversacional para la sesion.

        Raises:
            ChatServiceError: Si falla la consulta del historial.
        """
        try:
            history = self.chat_repository.get_session_history(session_id, limit=limit)
            return [
                ChatHistoryDTO(
                    id=message.id if message.id is not None else 0,
                    role=message.role,
                    message=message.message,
                    timestamp=message.timestamp,
                )
                for message in history
            ]
        except Exception as exc:
            raise ChatServiceError(
                f"Error obteniendo historial de sesión: {exc}"
            ) from exc

    def clear_session_history(self, session_id: str) -> int:
        """Elimina todo el historial asociado a una sesion.

        Args:
            session_id (str): Identificador de la sesion.

        Returns:
            int: Cantidad de mensajes eliminados.

        Raises:
            ChatServiceError: Si falla la eliminacion del historial.
        """
        try:
            return self.chat_repository.delete_session_history(session_id)
        except Exception as exc:
            raise ChatServiceError(
                f"Error eliminando historial de sesión: {exc}"
            ) from exc
