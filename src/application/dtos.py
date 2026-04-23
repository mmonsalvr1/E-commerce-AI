"""DTOs de la capa de aplicacion para requests y responses de la API."""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ProductDTO(BaseModel):
    """DTO para transportar informacion de productos entre capas.

    Attributes:
        id (Optional[int]): Identificador unico del producto.
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoria funcional.
        size (str): Talla del producto.
        color (str): Color del producto.
        price (float): Precio de venta.
        stock (int): Cantidad disponible.
        description (str): Descripcion del producto.
    """

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    @validator("price")
    def price_must_be_positive(cls, v):
        """Valida que el precio sea mayor a cero.

        Args:
            v (float): Valor de precio a validar.

        Returns:
            float: Precio validado.

        Raises:
            ValueError: Si el precio no es mayor a cero.
        """
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @validator("stock")
    def stock_must_be_non_negative(cls, v):
        """Valida que el stock no sea negativo.

        Args:
            v (int): Valor de stock a validar.

        Returns:
            int: Stock validado.

        Raises:
            ValueError: Si el stock es menor que cero.
        """
        if v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v

    class Config:
        from_attributes = True  # Permite crear desde objetos ORM


class ChatMessageRequestDTO(BaseModel):
    """DTO para requests de chat enviados por el usuario.

    Attributes:
        session_id (str): Identificador de sesion del usuario.
        message (str): Mensaje textual enviado al asistente.
    """

    session_id: str
    message: str

    @validator("message")
    def message_not_empty(cls, v):
        """Valida que el mensaje tenga contenido util.

        Args:
            v (str): Mensaje recibido.

        Returns:
            str: Mensaje validado.

        Raises:
            ValueError: Si el mensaje esta vacio o solo contiene espacios.
        """
        if not v or not v.strip():
            raise ValueError("El mensaje no puede estar vacío")
        return v

    @validator("session_id")
    def session_id_not_empty(cls, v):
        """Valida que exista un identificador de sesion.

        Args:
            v (str): Identificador de sesion recibido.

        Returns:
            str: Identificador validado.

        Raises:
            ValueError: Si el identificador esta vacio o solo contiene espacios.
        """
        if not v or not v.strip():
            raise ValueError("El ID de sesión no puede estar vacío")
        return v


class ChatMessageResponseDTO(BaseModel):
    """DTO para responses de chat retornadas por la API.

    Attributes:
        session_id (str): Identificador de sesion.
        user_message (str): Mensaje original del usuario.
        assistant_message (str): Respuesta generada por el asistente.
        timestamp (datetime): Fecha y hora de generacion de respuesta.
    """

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """DTO para representar cada item del historial de chat.

    Attributes:
        id (int): Identificador del mensaje en persistencia.
        role (str): Rol del emisor del mensaje.
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Fecha y hora del mensaje.
    """

    id: int
    role: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True
