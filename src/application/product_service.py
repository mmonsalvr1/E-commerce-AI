"""Servicios de aplicacion para casos de uso de productos."""

from typing import Dict, List, Optional

from src.application.dtos import ProductDTO
from src.domain.entities import Product
from src.domain.exceptions import InvalidProductDataError, ProductNotFoundError
from src.domain.repositories import IProductRepository


class ProductService:
    """Servicio de aplicacion para orquestar operaciones de productos.

    Attributes:
            product_repository (IProductRepository): Repositorio inyectado para
                    persistencia y consulta de productos.
    """

    def __init__(self, product_repository: IProductRepository):
        """Inicializa el servicio con dependencias inyectadas.

        Args:
                product_repository (IProductRepository): Implementacion concreta del
                        contrato de repositorio de productos.
        """
        self.product_repository = product_repository

    def get_all_products(self) -> List[ProductDTO]:
        """Lista todos los productos disponibles en persistencia.

        Returns:
                List[ProductDTO]: Coleccion de productos convertidos a DTO.
        """
        products = self.product_repository.get_all()
        return [self._entity_to_dto(product) for product in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """Obtiene un producto por su identificador.

        Args:
                product_id (int): Identificador del producto.

        Returns:
                ProductDTO: Producto encontrado convertido a DTO.

        Raises:
                ProductNotFoundError: Si no existe un producto con ese ID.
        """
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        return self._entity_to_dto(product)

    def search_products(
        self, filters: Optional[Dict[str, str]] = None
    ) -> List[ProductDTO]:
        """Busca productos usando filtros opcionales de marca y categoria.

        Args:
                filters (Optional[Dict[str, str]]): Diccionario con claves como
                        brand y category.

        Returns:
                List[ProductDTO]: Productos que cumplen los criterios de busqueda.
        """
        filters = filters or {}
        brand = filters.get("brand")
        category = filters.get("category")

        if brand and category:
            products = [
                product
                for product in self.product_repository.get_by_brand(brand)
                if product.category.lower() == category.lower()
            ]
        elif brand:
            products = self.product_repository.get_by_brand(brand)
        elif category:
            products = self.product_repository.get_by_category(category)
        else:
            products = self.product_repository.get_all()

        return [self._entity_to_dto(product) for product in products]

    def create_product(self, product_dto: ProductDTO) -> ProductDTO:
        """Crea y persiste un nuevo producto.

        Args:
                product_dto (ProductDTO): Datos del producto a crear.

        Returns:
                ProductDTO: Producto creado con sus datos persistidos.

        Raises:
                InvalidProductDataError: Si la entidad generada no cumple reglas de
                        negocio.
        """
        try:
            product_entity = self._dto_to_entity(product_dto, product_id=None)
            saved_product = self.product_repository.save(product_entity)
            return self._entity_to_dto(saved_product)
        except ValueError as exc:
            raise InvalidProductDataError(str(exc)) from exc

    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """Actualiza un producto existente.

        Args:
                product_id (int): Identificador del producto a actualizar.
                product_dto (ProductDTO): Datos actualizados del producto.

        Returns:
                ProductDTO: Producto actualizado.

        Raises:
                ProductNotFoundError: Si el producto no existe.
                InvalidProductDataError: Si los datos no cumplen reglas de negocio.
        """
        existing_product = self.product_repository.get_by_id(product_id)
        if not existing_product:
            raise ProductNotFoundError(product_id)

        try:
            product_entity = self._dto_to_entity(product_dto, product_id=product_id)
            updated_product = self.product_repository.save(product_entity)
            return self._entity_to_dto(updated_product)
        except ValueError as exc:
            raise InvalidProductDataError(str(exc)) from exc

    def delete_product(self, product_id: int) -> bool:
        """Elimina un producto por identificador.

        Args:
                product_id (int): Identificador del producto.

        Returns:
                bool: True cuando la eliminacion se realiza correctamente.

        Raises:
                ProductNotFoundError: Si el producto no existe o no puede eliminarse.
        """
        existing_product = self.product_repository.get_by_id(product_id)
        if not existing_product:
            raise ProductNotFoundError(product_id)

        deleted = self.product_repository.delete(product_id)
        if not deleted:
            raise ProductNotFoundError(product_id)
        return True

    def get_available_products(self) -> List[ProductDTO]:
        """Obtiene solo los productos con stock disponible.

        Returns:
                List[ProductDTO]: Productos disponibles para venta.
        """
        products = self.product_repository.get_all()
        available_products = [product for product in products if product.is_available()]
        return [self._entity_to_dto(product) for product in available_products]

    def _dto_to_entity(
        self, product_dto: ProductDTO, product_id: Optional[int]
    ) -> Product:
        """Convierte un DTO en entidad de dominio.

        Args:
                product_dto (ProductDTO): Datos de entrada del producto.
                product_id (Optional[int]): ID a usar en la entidad.

        Returns:
                Product: Entidad de dominio construida.
        """
        return Product(
            id=product_id,
            name=product_dto.name,
            brand=product_dto.brand,
            category=product_dto.category,
            size=product_dto.size,
            color=product_dto.color,
            price=product_dto.price,
            stock=product_dto.stock,
            description=product_dto.description,
        )

    def _entity_to_dto(self, product: Product) -> ProductDTO:
        """Convierte una entidad de dominio en DTO.

        Args:
                product (Product): Entidad de dominio.

        Returns:
                ProductDTO: DTO listo para capa de presentacion.
        """
        return ProductDTO(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description,
        )
