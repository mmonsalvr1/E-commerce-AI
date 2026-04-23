"""Carga datos iniciales para la base de datos de e-commerce."""

from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.models import ProductModel


def load_initial_data() -> None:
    """Carga productos de ejemplo si la tabla de productos está vacía.

    Esta función es idempotente: solo inserta datos cuando no existen
    registros previos en la tabla `products`.
    """
    db = SessionLocal()
    try:
        product_count = db.query(ProductModel).count()
        if product_count > 0:
            return

        products = [
            ProductModel(
                name="Air Zoom Pegasus 40",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=120.0,
                stock=5,
                description="Zapatilla de running con excelente amortiguación para entrenamiento diario.",
            ),
            ProductModel(
                name="Ultraboost 22",
                brand="Adidas",
                category="Running",
                size="41",
                color="Blanco",
                price=180.0,
                stock=3,
                description="Modelo premium con retorno de energía y ajuste cómodo.",
            ),
            ProductModel(
                name="Suede Classic",
                brand="Puma",
                category="Casual",
                size="40",
                color="Azul",
                price=80.0,
                stock=10,
                description="Un clásico versátil para uso diario con estilo retro.",
            ),
            ProductModel(
                name="Gel-Contend 8",
                brand="ASICS",
                category="Running",
                size="43",
                color="Gris",
                price=95.0,
                stock=6,
                description="Opción confiable para corredores que buscan estabilidad y confort.",
            ),
            ProductModel(
                name="Club C 85",
                brand="Reebok",
                category="Casual",
                size="39",
                color="Blanco",
                price=75.0,
                stock=8,
                description="Tenis casual con diseño minimalista y acabados clásicos.",
            ),
            ProductModel(
                name="Runfalcon 3",
                brand="Adidas",
                category="Running",
                size="42",
                color="Azul",
                price=65.0,
                stock=12,
                description="Zapatilla ligera para correr con buena ventilación y soporte básico.",
            ),
            ProductModel(
                name="Cortez Leather",
                brand="Nike",
                category="Casual",
                size="41",
                color="Blanco",
                price=90.0,
                stock=4,
                description="Modelo icónico de uso casual con acabado en cuero.",
            ),
            ProductModel(
                name="Roma Basic",
                brand="Puma",
                category="Formal",
                size="40",
                color="Negro",
                price=110.0,
                stock=7,
                description="Zapato de apariencia formal para combinar con atuendos elegantes.",
            ),
            ProductModel(
                name="Leather Oxford",
                brand="Clarks",
                category="Formal",
                size="43",
                color="Café",
                price=160.0,
                stock=2,
                description="Oxford de cuero para ocasiones formales y trabajo de oficina.",
            ),
            ProductModel(
                name="Wave Rider 27",
                brand="Mizuno",
                category="Running",
                size="42",
                color="Verde",
                price=150.0,
                stock=5,
                description="Modelo de alto rendimiento para corredores que buscan respuesta y estabilidad.",
            ),
        ]

        db.add_all(products)
        db.commit()
    finally:
        db.close()
