import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import auth, projects, tasks
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TaskFlow API",
    version="0.1.0",
    description=(
        "A private project and task-management API. "
        "Authenticate, then use the Bearer token in Swagger."
    ),
    openapi_url="/openapi.json",
    docs_url="/docs",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: object | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body: dict[str, object] = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body, headers=headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY, "validation_error", "Invalid request", exc.errors()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return error_response(exc.status_code, "http_error", str(exc.detail), headers=exc.headers)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled request error", extra={"path": request.url.path})
    # Starlette's outer error middleware sends 500 responses outside CORSMiddleware.
    # Add the configured origin so the browser can show the real API error.
    headers = None
    if request.headers.get("origin") == settings.frontend_origin:
        headers = {"Access-Control-Allow-Origin": settings.frontend_origin, "Vary": "Origin"}
    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "internal_error",
        "Internal server error",
        headers=headers,
    )


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Checks that the API can connect to MySQL without exposing connection details."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.warning("Health check failed because the database is unavailable")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "unavailable"},
        )
    return {"status": "ok", "database": "connected"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
