from collections.abc import Sequence

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.core.cursor import ProductCursor
from app.models.product import Product


class ProductRepository:
    def list_products(
        self,
        db: Session,
        *,
        limit: int,
        category: str | None = None,
        cursor: ProductCursor | None = None,
    ) -> Sequence[Product]:
        stmt = select(Product)

        if category:
            stmt = stmt.where(Product.category == category)

        if cursor:
            stmt = stmt.where(
                or_(
                    Product.updated_at < cursor.updated_at,
                    and_(
                        Product.updated_at == cursor.updated_at,
                        Product.id < cursor.id,
                    ),
                )
            )

        stmt = stmt.order_by(Product.updated_at.desc(), Product.id.desc()).limit(limit)
        return db.execute(stmt).scalars().all()

