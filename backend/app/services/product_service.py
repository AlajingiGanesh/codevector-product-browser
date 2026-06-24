from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.cursor import CursorDecodeError, decode_cursor, encode_cursor
from app.repositories.product_repository import ProductRepository
from app.schemas.product import PRODUCT_CATEGORIES, PaginatedProducts


class ProductService:
    def __init__(self, repository: ProductRepository | None = None) -> None:
        self.repository = repository or ProductRepository()
        self.settings = get_settings()

    def list_products(
        self,
        db: Session,
        *,
        limit: int,
        category: str | None = None,
        cursor: str | None = None,
    ) -> PaginatedProducts:
        clean_category = category.strip() if category else None
        if clean_category and clean_category not in PRODUCT_CATEGORIES:
            raise ValueError("Unsupported product category.")

        safe_limit = min(max(limit, 1), self.settings.max_page_size)
        decoded_cursor = decode_cursor(cursor) if cursor else None

        rows = self.repository.list_products(
            db,
            limit=safe_limit + 1,
            category=clean_category,
            cursor=decoded_cursor,
        )
        page_rows = list(rows[:safe_limit])
        has_more = len(rows) > safe_limit

        next_cursor = None
        if has_more and page_rows:
            last_product = page_rows[-1]
            next_cursor = encode_cursor(
                updated_at=last_product.updated_at,
                product_id=last_product.id,
            )

        return PaginatedProducts(
            data=page_rows,
            next_cursor=next_cursor,
            has_more=has_more,
        )


__all__ = ["CursorDecodeError", "ProductService"]

