"""Domain exceptions. Each maps to an HTTP status in app.main."""


class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ProductNotFoundError(AppError):
    status_code = 404
    code = "product_not_found"

    def __init__(self, product_id: int) -> None:
        super().__init__(f"Product with ID {product_id} not found.")


class DuplicateProductError(AppError):
    status_code = 409
    code = "duplicate_product_id"

    def __init__(self, product_id: int) -> None:
        super().__init__(f"A product with ID {product_id} already exists.")
