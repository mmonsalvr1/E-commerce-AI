"""Repositorio SQLAlchemy para el historial de chat."""

from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """Implementacion SQLAlchemy del repositorio de mensajes de chat.

    Attributes:
            db (Session): Sesion activa de SQLAlchemy.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
                db (Session): Sesion de base de datos inyectada.
        """
        self.db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje en persistencia.

        Args:
                message (ChatMessage): Mensaje de dominio a guardar.

        Returns:
                ChatMessage: Mensaje persistido con identificador asignado.
        """
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(
        self, session_id: str, limit: int | None = None
    ) -> list[ChatMessage]:
        """Obtiene historial de una sesion en orden cronologico.

        Args:
                session_id (str): Identificador de la sesion.
                limit (int | None): Limite maximo de mensajes.

        Returns:
                list[ChatMessage]: Historial completo o parcial de la sesion.
        """
        query = self.db.query(ChatMemoryModel).filter(
            ChatMemoryModel.session_id == session_id
        )

        if limit is not None:
            messages = (
                query.order_by(ChatMemoryModel.timestamp.desc()).limit(limit).all()
            )
            messages.reverse()
            return [self._model_to_entity(message) for message in messages]

        messages = query.order_by(ChatMemoryModel.timestamp.asc()).all()
        return [self._model_to_entity(message) for message in messages]

    def delete_session_history(self, session_id: str) -> int:
        """Elimina todos los mensajes de una sesion.

        Args:
                session_id (str): Identificador de la sesion.

        Returns:
                int: Cantidad de mensajes eliminados.
        """
        deleted_count = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted_count

    def get_recent_messages(self, session_id: str, count: int) -> list[ChatMessage]:
        """Obtiene los ultimos N mensajes en orden cronologico.

        Args:
                session_id (str): Identificador de la sesion.
                count (int): Cantidad maxima de mensajes.

        Returns:
                list[ChatMessage]: Mensajes recientes en orden cronologico.
        """
        messages = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(count)
            .all()
        )
        messages.reverse()
        return [self._model_to_entity(message) for message in messages]

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """Convierte un modelo ORM en una entidad ChatMessage.

        Args:
                model (ChatMemoryModel): Modelo ORM de mensaje.

        Returns:
                ChatMessage: Entidad de dominio equivalente.
        """
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """Convierte una entidad ChatMessage en modelo ORM.

        Args:
                entity (ChatMessage): Entidad de dominio.

        Returns:
                ChatMemoryModel: Modelo ORM equivalente.
        """
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp,
        )
