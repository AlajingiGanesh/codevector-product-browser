import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import products_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logging_config import configure_logging

settings = get_settings()
print("DATABASE_URL =", settings.database_url)
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        import app.models  # noqa: F401

        logger.info("AUTO_CREATE_TABLES enabled; creating database tables if needed.")
        Base.metadata.create_all(bind=engine)

    logger.info("%s started in %s mode.", settings.app_name, settings.environment)
    yield
    logger.info("%s stopped.", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


app.include_router(products_router)

