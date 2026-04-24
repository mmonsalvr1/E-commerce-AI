"""Pruebas unitarias para servicios de aplicacion."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.chat_service import ChatService
from src.application.dtos import ChatMessageRequestDTO, ProductDTO
from src.application.product_service import ProductService
from src.domain.entities import ChatMessage, Product
from src.domain.exceptions import (
    ChatServiceError,
    InvalidProductDataError,
    ProductNotFoundError,
)


@pytest.fixture
def sample_product():
    """Retorna una entidad Product valida para escenarios de prueba."""
    return Product(
        id=1,
        name="Air Zoom Pegasus",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="Zapatilla para correr con amortiguación",
    )


@pytest.fixture
def sample_product_dto():
    """Retorna un DTO de producto valido para creacion/actualizacion."""
    return ProductDTO(
        id=None,
        name="Air Zoom Pegasus",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="Zapatilla para correr con amortiguación",
    )


@pytest.fixture
def sample_chat_request():
    """Retorna un DTO de request de chat valido para pruebas."""
    return ChatMessageRequestDTO(
        session_id="session-1",
        message="Busco zapatos Nike para correr",
    )


@pytest.fixture
def product_repository():
    """Construye un mock de repositorio de productos."""
    repo = MagicMock()
    repo.get_all.return_value = []
    repo.get_by_id.return_value = None
    repo.get_by_brand.return_value = []
    repo.get_by_category.return_value = []
    repo.save.return_value = None
    repo.delete.return_value = True
    return repo


@pytest.fixture
def chat_repository():
    """Construye un mock de repositorio de chat."""
    repo = MagicMock()
    repo.get_recent_messages.return_value = []
    repo.get_session_history.return_value = []
    repo.save_message.return_value = None
    repo.delete_session_history.return_value = 0
    return repo


@pytest.fixture
def ai_service():
    """Construye un mock asincrono del servicio de IA."""
    service = MagicMock()
    service.generate_response = AsyncMock(
        return_value="Tengo opciones ideales para running"
    )
    return service


@pytest.fixture
def product_service(product_repository):
    """Crea ProductService con dependencias mockeadas."""
    return ProductService(product_repository)


@pytest.fixture
def chat_service(product_repository, chat_repository, ai_service):
    """Crea ChatService con repositorios y IA simulados."""
    return ChatService(product_repository, chat_repository, ai_service)


class TestProductService:
    """Pruebas para el servicio de productos."""

    def test_get_all_products_returns_dtos(
        self, product_service, product_repository, sample_product
    ):
        """Valida conversion de entidades a DTOs al listar productos."""
        product_repository.get_all.return_value = [sample_product]

        result = product_service.get_all_products()

        assert len(result) == 1
        assert result[0].name == sample_product.name
        assert result[0].price == sample_product.price
        product_repository.get_all.assert_called_once()

    def test_get_product_by_id_returns_dto(
        self, product_service, product_repository, sample_product
    ):
        """Valida busqueda exitosa de producto por identificador."""
        product_repository.get_by_id.return_value = sample_product

        result = product_service.get_product_by_id(1)

        assert result.id == 1
        assert result.name == sample_product.name
        product_repository.get_by_id.assert_called_once_with(1)

    def test_get_product_by_id_raises_when_not_found(
        self, product_service, product_repository
    ):
        """Valida excepcion cuando no existe el producto solicitado."""
        product_repository.get_by_id.return_value = None

        with pytest.raises(
            ProductNotFoundError, match="Producto con ID 99 no encontrado"
        ):
            product_service.get_product_by_id(99)

    def test_search_products_without_filters_returns_all(
        self, product_service, product_repository, sample_product
    ):
        """Comprueba que sin filtros se retornen todos los productos."""
        product_repository.get_all.return_value = [sample_product]

        result = product_service.search_products()

        assert len(result) == 1
        product_repository.get_all.assert_called_once()

    def test_search_products_by_brand(
        self, product_service, product_repository, sample_product
    ):
        """Comprueba filtrado de productos por marca."""
        product_repository.get_by_brand.return_value = [sample_product]

        result = product_service.search_products({"brand": "Nike"})

        assert len(result) == 1
        product_repository.get_by_brand.assert_called_once_with("Nike")

    def test_search_products_by_category(
        self, product_service, product_repository, sample_product
    ):
        """Comprueba filtrado de productos por categoria."""
        product_repository.get_by_category.return_value = [sample_product]

        result = product_service.search_products({"category": "Running"})

        assert len(result) == 1
        product_repository.get_by_category.assert_called_once_with("Running")

    def test_search_products_by_brand_and_category_filters_results(
        self, product_service, product_repository
    ):
        """Valida combinacion de filtros por marca y categoria."""
        matching_product = Product(
            id=1,
            name="Air Zoom Pegasus",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=5,
            description="Zapatilla para correr con amortiguación",
        )
        non_matching_product = Product(
            id=2,
            name="Court Vision",
            brand="Nike",
            category="Casual",
            size="41",
            color="Blanco",
            price=95.0,
            stock=4,
            description="Zapatilla casual",
        )
        product_repository.get_by_brand.return_value = [
            matching_product,
            non_matching_product,
        ]

        result = product_service.search_products(
            {"brand": "Nike", "category": "Running"}
        )

        assert len(result) == 1
        assert result[0].id == 1
        product_repository.get_by_brand.assert_called_once_with("Nike")

    def test_create_product_returns_saved_product(
        self, product_service, product_repository, sample_product_dto, sample_product
    ):
        """Verifica creacion de producto y retorno del DTO persistido."""
        product_repository.save.return_value = sample_product

        result = product_service.create_product(sample_product_dto)

        assert result.id == sample_product.id
        assert result.name == sample_product.name
        product_repository.save.assert_called_once()

    def test_create_product_wraps_value_error(
        self, product_service, product_repository, sample_product_dto
    ):
        """Verifica mapeo de ValueError a InvalidProductDataError."""
        product_repository.save.side_effect = ValueError("Datos inválidos")

        with pytest.raises(InvalidProductDataError, match="Datos inválidos"):
            product_service.create_product(sample_product_dto)

    def test_update_product_returns_updated_product(
        self,
        product_service,
        product_repository,
        sample_product_dto,
        sample_product,
    ):
        """Verifica actualizacion exitosa de un producto existente."""
        product_repository.get_by_id.return_value = sample_product
        product_repository.save.return_value = sample_product

        result = product_service.update_product(1, sample_product_dto)

        assert result.id == 1
        product_repository.get_by_id.assert_called_once_with(1)
        product_repository.save.assert_called_once()

    def test_update_product_raises_when_not_found(
        self, product_service, product_repository, sample_product_dto
    ):
        """Verifica error al actualizar un producto inexistente."""
        product_repository.get_by_id.return_value = None

        with pytest.raises(
            ProductNotFoundError, match="Producto con ID 404 no encontrado"
        ):
            product_service.update_product(404, sample_product_dto)

    def test_update_product_wraps_value_error(
        self,
        product_service,
        product_repository,
        sample_product_dto,
        sample_product,
    ):
        """Verifica mapeo de error de repositorio durante actualizacion."""
        product_repository.get_by_id.return_value = sample_product
        product_repository.save.side_effect = ValueError("No se pudo actualizar")

        with pytest.raises(InvalidProductDataError, match="No se pudo actualizar"):
            product_service.update_product(1, sample_product_dto)

    def test_delete_product_returns_true_when_deleted(
        self, product_service, product_repository, sample_product
    ):
        """Verifica eliminacion exitosa cuando el producto existe."""
        product_repository.get_by_id.return_value = sample_product
        product_repository.delete.return_value = True

        result = product_service.delete_product(1)

        assert result is True
        product_repository.delete.assert_called_once_with(1)

    def test_delete_product_raises_when_not_found(
        self, product_service, product_repository
    ):
        """Verifica error al eliminar producto inexistente."""
        product_repository.get_by_id.return_value = None

        with pytest.raises(
            ProductNotFoundError, match="Producto con ID 7 no encontrado"
        ):
            product_service.delete_product(7)

    def test_delete_product_raises_when_repository_reports_failure(
        self, product_service, product_repository, sample_product
    ):
        """Verifica error cuando repositorio no logra eliminar el registro."""
        product_repository.get_by_id.return_value = sample_product
        product_repository.delete.return_value = False

        with pytest.raises(
            ProductNotFoundError, match="Producto con ID 1 no encontrado"
        ):
            product_service.delete_product(1)

    def test_get_available_products_filters_stock(
        self, product_service, product_repository, sample_product
    ):
        """Verifica que solo se devuelvan productos con stock disponible."""
        unavailable_product = Product(
            id=2,
            name="Ultraboost 21",
            brand="Adidas",
            category="Running",
            size="41",
            color="Blanco",
            price=150.0,
            stock=0,
            description="Zapatilla premium",
        )
        product_repository.get_all.return_value = [sample_product, unavailable_product]

        result = product_service.get_available_products()

        assert len(result) == 1
        assert result[0].id == 1


class TestChatService:
    """Pruebas para el servicio de chat."""

    def test_process_message_saves_messages_and_returns_response(
        self,
        chat_service,
        product_repository,
        chat_repository,
        ai_service,
        sample_chat_request,
        sample_product,
    ):
        """Valida flujo principal de chat: IA, guardado y respuesta final."""
        recent_history = [
            ChatMessage(
                id=1,
                session_id="session-1",
                role="user",
                message="Hola",
                timestamp=datetime(2024, 1, 15, 10, 0, 0),
            )
        ]
        product_repository.get_all.return_value = [sample_product]
        chat_repository.get_recent_messages.return_value = recent_history

        response = asyncio.run(chat_service.process_message(sample_chat_request))

        assert response.session_id == "session-1"
        assert response.user_message == sample_chat_request.message
        assert response.assistant_message == "Tengo opciones ideales para running"
        assert response.timestamp is not None
        product_repository.get_all.assert_called_once()
        chat_repository.get_recent_messages.assert_called_once_with(
            "session-1", count=6
        )
        ai_service.generate_response.assert_awaited_once()
        assert chat_repository.save_message.call_count == 2

        saved_user_message = chat_repository.save_message.call_args_list[0].args[0]
        saved_assistant_message = chat_repository.save_message.call_args_list[1].args[0]
        assert saved_user_message.role == "user"
        assert saved_assistant_message.role == "assistant"

    def test_process_message_wraps_ai_errors(
        self,
        chat_service,
        product_repository,
        chat_repository,
        ai_service,
        sample_chat_request,
        sample_product,
    ):
        """Valida encapsulamiento de fallos de IA en ChatServiceError."""
        product_repository.get_all.return_value = [sample_product]
        chat_repository.get_recent_messages.return_value = []
        ai_service.generate_response = AsyncMock(side_effect=RuntimeError("API caída"))

        with pytest.raises(
            ChatServiceError, match="Error procesando mensaje de chat: API caída"
        ):
            asyncio.run(chat_service.process_message(sample_chat_request))

    def test_process_message_accepts_async_response_from_ai(
        self,
        chat_service,
        product_repository,
        chat_repository,
        sample_chat_request,
        sample_product,
    ):
        """Verifica soporte de respuestas asincronas del proveedor de IA."""
        product_repository.get_all.return_value = [sample_product]
        chat_repository.get_recent_messages.return_value = []

        async def fake_generate_response(*args, **kwargs):
            """Simula respuesta asincrona del proveedor de IA."""
            return "Respuesta asíncrona"

        chat_service.ai_service.generate_response = fake_generate_response

        response = asyncio.run(chat_service.process_message(sample_chat_request))

        assert response.assistant_message == "Respuesta asíncrona"

    def test_get_session_history_returns_dtos(self, chat_service, chat_repository):
        """Valida obtencion de historial y conversion a DTOs."""
        chat_repository.get_session_history.return_value = [
            ChatMessage(
                id=1,
                session_id="session-1",
                role="user",
                message="Hola",
                timestamp=datetime(2024, 1, 15, 10, 0, 0),
            ),
            ChatMessage(
                id=2,
                session_id="session-1",
                role="assistant",
                message="Hola, ¿en qué te ayudo?",
                timestamp=datetime(2024, 1, 15, 10, 0, 1),
            ),
        ]

        result = chat_service.get_session_history("session-1", limit=10)

        assert len(result) == 2
        assert result[0].role == "user"
        assert result[1].role == "assistant"
        chat_repository.get_session_history.assert_called_once_with(
            "session-1", limit=10
        )

    def test_get_session_history_wraps_errors(self, chat_service, chat_repository):
        """Valida encapsulamiento de errores al consultar historial."""
        chat_repository.get_session_history.side_effect = RuntimeError(
            "falló historial"
        )

        with pytest.raises(
            ChatServiceError,
            match="Error obteniendo historial de sesión: falló historial",
        ):
            chat_service.get_session_history("session-1", limit=10)

    def test_clear_session_history_returns_deleted_count(
        self, chat_service, chat_repository
    ):
        """Verifica retorno de cantidad de mensajes eliminados."""
        chat_repository.delete_session_history.return_value = 3

        result = chat_service.clear_session_history("session-1")

        assert result == 3
        chat_repository.delete_session_history.assert_called_once_with("session-1")

    def test_clear_session_history_wraps_errors(self, chat_service, chat_repository):
        """Valida encapsulamiento de errores al eliminar historial."""
        chat_repository.delete_session_history.side_effect = RuntimeError(
            "falló borrado"
        )

        with pytest.raises(
            ChatServiceError,
            match="Error eliminando historial de sesión: falló borrado",
        ):
            chat_service.clear_session_history("session-1")
