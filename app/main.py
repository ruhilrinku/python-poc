import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.adapters.inbound.http.department_router import router as department_router
from app.adapters.inbound.http.employee_router import router as employee_router
from app.adapters.inbound.http.error_handlers import register_exception_handlers
from app.adapters.inbound.http.middleware import RequestLoggingMiddleware
from app.infrastructure.config import get_settings
from app.infrastructure.logging import configure_logging
from app.infrastructure.migrations import run_migrations

settings = get_settings()
configure_logging(settings.log_level, settings.log_json)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.run_migrations_on_startup:
        try:
            run_migrations(settings)
        except Exception:
            logger.exception("liquibase.update.failed")
            if settings.fail_on_migration_error:
                raise
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Employee Management API (FastAPI, hexagonal architecture).",
        lifespan=lifespan,
    )
    app.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(app)
    app.include_router(employee_router)
    app.include_router(department_router)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    logger.info("app.started", extra={"extra_fields": {"version": settings.app_version}})
    return app


app = create_app()
