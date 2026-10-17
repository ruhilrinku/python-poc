import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions import DomainError

logger = logging.getLogger("api.error")

_STATUS_BY_CODE = {
    "VALIDATION_ERROR": 400,
    "EMPLOYEE_NOT_FOUND": 404,
    "DEPARTMENT_NOT_FOUND": 404,
    "DUPLICATE_EMAIL": 409,
    "DUPLICATE_EMPLOYEE_CODE": 409,
}


def _error_body(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


async def _domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status_code = _STATUS_BY_CODE.get(exc.code, 400)
    logger.warning(
        "domain.error",
        extra={
            "extra_fields": {
                "code": exc.code,
                "path": request.url.path,
                "detail": exc.message,
            }
        },
    )
    return JSONResponse(
        status_code=status_code, content=_error_body(exc.code, exc.message)
    )


async def _validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    message = "; ".join(
        f"{'.'.join(str(p) for p in err['loc'][1:])}: {err['msg']}"
        for err in exc.errors()
    )
    logger.warning(
        "request.validation_error",
        extra={"extra_fields": {"path": request.url.path, "detail": message}},
    )
    return JSONResponse(
        status_code=422,
        content=_error_body("VALIDATION_ERROR", message or "Invalid request"),
    )


async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "request.unhandled_error",
        extra={"extra_fields": {"path": request.url.path}},
    )
    return JSONResponse(
        status_code=500,
        content=_error_body("INTERNAL_ERROR", "An unexpected error occurred"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_error_handler)
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(Exception, _unhandled_error_handler)
