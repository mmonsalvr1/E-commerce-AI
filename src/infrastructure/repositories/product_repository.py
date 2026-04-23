"""Repositorio SQLAlchemy para productos."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """Implementacion SQLAlchemy del repositorio de productos.

    Attributes:
            db (Session): Sesion activa de SQLAlchemy.
    """

    def __init__(self, db: Session):
        """Inicializa el repositorio.

        Args:
                db (Session): Sesion de base de datos inyectada.
        """
        self.db = db

    def get_all(self) -> list[Product]:
        """Obtiene todos los productos persistidos.

        Returns:
                list[Product]: Coleccion completa de productos.
        """
        products = self.db.query(ProductModel).all()
        return [self._model_to_entity(product) for product in products]

    def get_by_id(self, product_id: int) -> Product | None:
        """Obtiene un producto por identificador.

        Args:
                product_id (int): Identificador del producto.

        Returns:
                Product | None: Producto encontrado o None.
        """
        product = (
            self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        )
        return self._model_to_entity(product) if product else None

    def get_by_brand(self, brand: str) -> list[Product]:
        """Obtiene productos filtrados por marca.

        Args:
                brand (str): Marca a consultar.

        Returns:
                list[Product]: Productos de la marca indicada.
        """
        products = (
            self.db.query(ProductModel)
            .filter(func.lower(ProductModel.brand) == brand.lower())
            .all()
        )
        return [self._model_to_entity(product) for product in products]

    def get_by_category(self, category: str) -> list[Product]:
        """Obtiene productos filtrados por categoria.

        Args:
                category (str): Categoria a consultar.

        Returns:
                list[Product]: Productos de la categoria indicada.
        """
        products = (
            self.db.query(ProductModel)
            .filter(func.lower(ProductModel.category) == category.lower())
            .all()
        )
        return [self._model_to_entity(product) for product in products]

    def save(self, product: Product) -> Product:
        """Guarda un producto nuevo o actualiza uno existente.

        Args:
                product (Product): Entidad a persistir.

        Returns:
                Product: Entidad persistida con valores actualizados.
        """
        if product.id is None:
            model = self._entity_to_model(product)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._model_to_entity(model)

        model = (
            self.db.query(ProductModel).filter(ProductModel.id == product.id).first()
        )
        if model is None:
            model = self._entity_to_model(product)
            self.db.add(model)
        else:
            model.name = product.name
            model.brand = product.brand
            model.category = product.category
            model.size = product.size
            model.color = product.color
            model.price = product.price
            model.stock = product.stock
            model.description = product.description

        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def delete(self, product_id: int) -> bool:
        """Elimina un producto por identificador.

        Args:
                product_id (int): Identificador del producto a eliminar.

        Returns:
                bool: True si se elimino, False si no existia.
        """
        model = (
            self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        )
        if model is None:
            return False

        self.db.delete(model)
        self.db.commit()
        return True

    def _model_to_entity(self, model: ProductModel | None) -> Product | None:
        """Convierte un modelo ORM en entidad de dominio.

        Args:
                model (ProductModel | None): Modelo ORM de producto.

        Returns:
                Product | None: Entidad equivalente o None.
        """
        if model is None:
            return None

        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """Convierte una entidad de dominio en modelo ORM.

        Args:
                entity (Product): Entidad de dominio.

        Returns:
                ProductModel: Modelo ORM equivalente.
        """
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description,
        )
