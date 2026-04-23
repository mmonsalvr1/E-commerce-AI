"""Entidades y value objects del dominio de e-commerce con chat."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """Entidad que representa un producto del inventario.

    Esta clase encapsula reglas de negocio basicas para precio, stock
    y operaciones de disponibilidad.

    Attributes:
        id (Optional[int]): Identificador unico del producto.
        name (str): Nombre comercial del producto.
        brand (str): Marca del producto.
        category (str): Categoria funcional, por ejemplo Running o Casual.
        size (str): Talla del producto.
        color (str): Color principal del producto.
        price (float): Precio unitario, debe ser mayor a 0.
        stock (int): Inventario disponible, no puede ser negativo.
        description (str): Descripcion comercial del producto.
    """

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self):
        """Valida reglas basicas de consistencia al crear la entidad.

        Raises:
            ValueError: Si el precio no es positivo, el stock es negativo o
                el nombre esta vacio.
        """
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")
        if not self.name:
            raise ValueError("El nombre no puede estar vacío")

    def is_available(self) -> bool:
        """Indica si el producto esta disponible para venta.

        Returns:
            bool: True cuando el stock es mayor que cero.
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """Reduce el stock del producto en una cantidad especifica.

        Args:
            quantity (int): Cantidad a descontar del inventario.

        Raises:
            ValueError: Si la cantidad no es positiva o supera el stock
                disponible.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva")
        if quantity > self.stock:
            raise ValueError("No hay suficiente stock disponible")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """Incrementa el stock del producto.

        Args:
            quantity (int): Cantidad a sumar al inventario.

        Raises:
            ValueError: Si la cantidad no es positiva.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva")
        self.stock += quantity


@dataclass
class ChatMessage:
    """Entidad que representa un mensaje en una sesion de chat.

    Attributes:
        id (Optional[int]): Identificador unico del mensaje.
        session_id (str): Identificador de la sesion conversacional.
        role (str): Rol del emisor, puede ser user o assistant.
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Fecha y hora en que se genero el mensaje.
    """

    id: Optional[int]
    session_id: str
    role: str  # 'user' o 'assistant'
    message: str
    timestamp: datetime

    def __post_init__(self):
        """Valida el contenido minimo de un mensaje de chat.

        Raises:
            ValueError: Si el rol no es valido, el mensaje esta vacio o no
                existe session_id.
        """
        if self.role not in ["user", "assistant"]:
            raise ValueError("El rol debe ser 'user' o 'assistant'")
        if not self.message:
            raise ValueError("El mensaje no puede estar vacío")
        if not self.session_id:
            raise ValueError("El ID de sesión no puede estar vacío")

    def is_from_user(self) -> bool:
        """Verifica si el mensaje fue enviado por el usuario.

        Returns:
            bool: True si el rol es user.
        """
        return self.role == "user"

    def is_from_assistant(self) -> bool:
        """Verifica si el mensaje fue enviado por el asistente.

        Returns:
            bool: True si el rol es assistant.
        """
        return self.role == "assistant"


@dataclass
class ChatContext:
    """Value object que encapsula contexto conversacional reciente.

    Attributes:
        messages (list[ChatMessage]): Historial completo o parcial de la
            sesion.
        max_messages (int): Numero maximo de mensajes a incluir en contexto.
    """

    messages: list[ChatMessage]
    max_messages: int = 6

    def get_recent_messages(self) -> list[ChatMessage]:
        """Retorna los ultimos mensajes segun el limite configurado.

        Returns:
            list[ChatMessage]: Subconjunto de mensajes recientes.
        """
        return self.messages[-self.max_messages :]

    def format_for_prompt(self) -> str:
        """Formatea el historial reciente en texto para prompts de IA.

        Returns:
            str: Texto multilinea con prefijos Usuario o Asistente.
        """
        formatted_messages = []
        for msg in self.get_recent_messages():
            role = "Usuario" if msg.is_from_user() else "Asistente"
            formatted_messages.append(f"{role}: {msg.message}")
        return "\n".join(formatted_messages)
