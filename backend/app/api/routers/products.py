import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.cursor import CursorDecodeError
from app.schemas.product import PaginatedProducts, ProductCategory
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/products", tags=["products"])
service = ProductService()


@router.get("", response_model=PaginatedProducts)
def list_products(
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=settings.max_page_size,
            description="Number of products to return.",
        ),
    ] = settings.default_page_size,
    category: Annotated[
        ProductCategory | None,
        Query(description="Optional product category filter."),
    ] = None,
    cursor: Annotated[
        str | None,
        Query(description="Opaque cursor returned by the previous response."),
    ] = None,
    db: Session = Depends(get_db),
) -> PaginatedProducts:
    try:
        return service.list_products(
            db,
            limit=limit,
            category=category,
            cursor=cursor,
        )
    except CursorDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid cursor.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except SQLAlchemyError as exc:
        logger.exception("Database error while listing products.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database temporarily unavailable.",
        ) from exc

