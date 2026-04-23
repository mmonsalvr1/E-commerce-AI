"""Modelos ORM de SQLAlchemy para la persistencia de la aplicación."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.database import Base


class ProductModel(Base):
    """Modelo ORM que representa un producto en el inventario.

    Attributes:
        id (int): Identificador único del producto.
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoría del producto.
        size (str): Talla del producto.
        color (str): Color del producto.
        price (float): Precio del producto.
        stock (int): Cantidad disponible en inventario.
        description (str): Descripción detallada del producto.
    """

    __tablename__ = "products"

    __table_args__ = (
        Index("ix_products_name", "name"),
        Index("ix_products_brand", "brand"),
        Index("ix_products_category", "category"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[str] = mapped_column(String(20), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        """Retorna una representación legible del modelo de producto."""
        return (
            "ProductModel("
            f"id={self.id!r}, name={self.name!r}, brand={self.brand!r}, "
            f"category={self.category!r}, size={self.size!r}, stock={self.stock!r})"
        )


class ChatMemoryModel(Base):
    """Modelo ORM que almacena el historial de mensajes de chat.

    Attributes:
        id (int): Identificador único del mensaje.
        session_id (str): Identificador de la sesión de chat.
        role (str): Rol del emisor, por ejemplo 'user' o 'assistant'.
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Momento en que se guardó el mensaje.
    """

    __tablename__ = "chat_memory"

    __table_args__ = (Index("ix_chat_memory_session_id", "session_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        """Retorna una representación legible del modelo de mensaje."""
        return (
            "ChatMemoryModel("
            f"id={self.id!r}, session_id={self.session_id!r}, role={self.role!r}, "
            f"timestamp={self.timestamp!r})"
        )
