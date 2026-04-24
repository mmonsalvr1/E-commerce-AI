"""Pruebas unitarias para entidades y value objects del dominio."""

from datetime import datetime

import pytest

from src.domain.entities import ChatContext, ChatMessage, Product


def make_product(**overrides):
    """Crea un producto válido para reutilizarlo en los tests."""
    data = {
        "id": 1,
        "name": "Air Zoom Pegasus",
        "brand": "Nike",
        "category": "Running",
        "size": "42",
        "color": "Negro",
        "price": 120.0,
        "stock": 5,
        "description": "Zapatilla para correr con amortiguación",
    }
    data.update(overrides)
    return Product(**data)


def make_message(**overrides):
    """Crea un mensaje de chat válido para reutilizarlo en los tests."""
    data = {
        "id": 1,
        "session_id": "user123",
        "role": "user",
        "message": "Hola, busco zapatos para correr",
        "timestamp": datetime(2024, 1, 15, 10, 30, 0),
    }
    data.update(overrides)
    return ChatMessage(**data)


class TestProduct:
    """Pruebas para la entidad Product."""

    def test_product_validations_accept_valid_data(self):
        """Verifica que un producto valido se construye sin errores."""
        product = make_product()

        assert product.name == "Air Zoom Pegasus"
        assert product.price == 120.0
        assert product.stock == 5

    @pytest.mark.parametrize(
        "field, value, error_message",
        [
            ("price", 0, "El precio debe ser mayor a 0"),
            ("price", -10, "El precio debe ser mayor a 0"),
            ("stock", -1, "El stock no puede ser negativo"),
            ("name", "", "El nombre no puede estar vacío"),
        ],
    )
    def test_product_validations_raise_value_error(self, field, value, error_message):
        """Verifica validaciones de negocio invalidas en Product."""
        kwargs = {field: value}

        with pytest.raises(ValueError, match=error_message):
            make_product(**kwargs)

    def test_is_available_returns_true_when_stock_exists(self):
        """Confirma disponibilidad cuando el stock es mayor a cero."""
        product = make_product(stock=2)

        assert product.is_available() is True

    def test_is_available_returns_false_when_stock_is_zero(self):
        """Confirma no disponibilidad cuando no hay stock."""
        product = make_product(stock=0)

        assert product.is_available() is False

    def test_reduce_stock_decreases_stock(self):
        """Comprueba que reduce_stock descuenta inventario correctamente."""
        product = make_product(stock=5)

        product.reduce_stock(3)

        assert product.stock == 2

    @pytest.mark.parametrize(
        "quantity, error_message",
        [
            (0, "La cantidad a reducir debe ser positiva"),
            (-1, "La cantidad a reducir debe ser positiva"),
            (6, "No hay suficiente stock disponible"),
        ],
    )
    def test_reduce_stock_raises_value_error_for_invalid_quantity(
        self, quantity, error_message
    ):
        """Comprueba errores al reducir stock con cantidades invalidas."""
        product = make_product(stock=5)

        with pytest.raises(ValueError, match=error_message):
            product.reduce_stock(quantity)


class TestChatMessage:
    """Pruebas para la entidad ChatMessage."""

    def test_chat_message_validations_accept_valid_data(self):
        """Verifica que un mensaje valido se crea correctamente."""
        message = make_message()

        assert message.session_id == "user123"
        assert message.role == "user"
        assert message.is_from_user() is True
        assert message.is_from_assistant() is False

    @pytest.mark.parametrize(
        "field, value, error_message",
        [
            ("role", "admin", "El rol debe ser 'user' o 'assistant'"),
            ("message", "", "El mensaje no puede estar vacío"),
            ("session_id", "", "El ID de sesión no puede estar vacío"),
        ],
    )
    def test_chat_message_validations_raise_value_error(
        self, field, value, error_message
    ):
        """Verifica validaciones invalidas para mensajes de chat."""
        kwargs = {field: value}

        with pytest.raises(ValueError, match=error_message):
            make_message(**kwargs)

    def test_is_from_assistant_returns_true_for_assistant_role(self):
        """Confirma los predicados de rol para mensajes del asistente."""
        message = make_message(role="assistant")

        assert message.is_from_user() is False
        assert message.is_from_assistant() is True


class TestChatContext:
    """Pruebas para el value object ChatContext."""

    def test_get_recent_messages_returns_last_messages(self):
        """Verifica que se retornen solo los mensajes mas recientes."""
        messages = [
            make_message(id=1, message="Mensaje 1"),
            make_message(id=2, role="assistant", message="Mensaje 2"),
            make_message(id=3, message="Mensaje 3"),
            make_message(id=4, role="assistant", message="Mensaje 4"),
        ]
        context = ChatContext(messages=messages, max_messages=2)

        recent_messages = context.get_recent_messages()

        assert recent_messages == messages[-2:]

    def test_format_for_prompt_formats_messages_with_roles(self):
        """Valida formato de contexto para prompt con roles legibles."""
        messages = [
            make_message(id=1, message="Hola"),
            make_message(id=2, role="assistant", message="Hola, ¿en qué te ayudo?"),
            make_message(id=3, message="Busco zapatos para correr"),
        ]
        context = ChatContext(messages=messages, max_messages=3)

        prompt = context.format_for_prompt()

        assert prompt == (
            "Usuario: Hola\n"
            "Asistente: Hola, ¿en qué te ayudo?\n"
            "Usuario: Busco zapatos para correr"
        )

    def test_format_for_prompt_uses_only_recent_messages(self):
        """Asegura que el prompt use el limite de mensajes configurado."""
        messages = [
            make_message(id=1, message="Mensaje 1"),
            make_message(id=2, role="assistant", message="Mensaje 2"),
            make_message(id=3, message="Mensaje 3"),
            make_message(id=4, role="assistant", message="Mensaje 4"),
        ]
        context = ChatContext(messages=messages, max_messages=2)

        prompt = context.format_for_prompt()

        assert prompt == "Usuario: Mensaje 3\nAsistente: Mensaje 4"
