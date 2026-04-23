"""
Excepciones específicas del dominio.
Representan errores de negocio, no errores técnicos.
"""


class ProductNotFoundError(Exception):
    """Excepcion para indicar que un producto no existe en el sistema."""

    def __init__(self, product_id: int = None):
        """Construye la excepcion con mensaje contextual.

        Args:
            product_id (int, optional): Identificador del producto buscado.
        """
        if product_id:
            self.message = f"Producto con ID {product_id} no encontrado"
        else:
            self.message = "Producto no encontrado"
        super().__init__(self.message)


class InvalidProductDataError(Exception):
    """Excepcion para errores de validacion de datos de producto."""

    def __init__(self, message: str = "Datos de producto inválidos"):
        """Construye la excepcion con mensaje personalizado.

        Args:
            message (str): Descripcion del error de validacion.
        """
        self.message = message
        super().__init__(self.message)


class ChatServiceError(Exception):
    """Excepcion para fallas funcionales del servicio de chat."""

    def __init__(self, message: str = "Error en el servicio de chat"):
        """Construye la excepcion con mensaje personalizado.

        Args:
            message (str): Descripcion de la falla detectada.
        """
        self.message = message
        super().__init__(self.message)
