"""Contratos de repositorio del dominio para productos y chat."""

from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage


class IProductRepository(ABC):
    """Contrato para operaciones de persistencia de productos."""

    @abstractmethod
    def get_all(self) -> List[Product]:
        """Obtiene todos los productos registrados.

        Returns:
            List[Product]: Lista de entidades de producto.
        """
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Busca un producto por identificador unico.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            Optional[Product]: Producto encontrado o None.
        """
        pass

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """Obtiene productos que pertenecen a una marca.

        Args:
            brand (str): Nombre de la marca.

        Returns:
            List[Product]: Productos que coinciden con la marca.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """Obtiene productos de una categoria especifica.

        Args:
            category (str): Nombre de la categoria.

        Returns:
            List[Product]: Productos de la categoria solicitada.
        """
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        """Guarda o actualiza un producto.

        Args:
            product (Product): Entidad a persistir.

        Returns:
            Product: Entidad persistida con datos actualizados.
        """
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """Elimina un producto por su identificador.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            bool: True si se elimino, False si no existia.
        """
        pass


class IChatRepository(ABC):
    """Contrato para persistencia y consulta de historial conversacional."""

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """Guarda un mensaje en el historial de chat.

        Args:
            message (ChatMessage): Mensaje a persistir.

        Returns:
            ChatMessage: Mensaje persistido con identificador asignado.
        """
        pass

    @abstractmethod
    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Obtiene mensajes de una sesion en orden cronologico.

        Args:
            session_id (str): Identificador de la sesion.
            limit (Optional[int]): Numero maximo de mensajes a retornar.

        Returns:
            List[ChatMessage]: Historial total o parcial de la sesion.
        """
        pass

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """Elimina todos los mensajes de una sesion.

        Args:
            session_id (str): Identificador de la sesion.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        pass

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """Obtiene los ultimos mensajes de una sesion.

        Args:
            session_id (str): Identificador de la sesion.
            count (int): Cantidad maxima de mensajes recientes.

        Returns:
            List[ChatMessage]: Mensajes recientes en orden cronologico.
        """
        pass
