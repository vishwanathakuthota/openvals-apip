from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    admin,
    ai_economics,
    auth,
    companies,
    confidence,
    countries,
    health,
    industries,
    metrics,
    models,
    roi_calculator,
    scoreboard,
    sources,
)
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="APIP API",
        description="AI Profitability Intelligence Platform API",
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
    )

    app.include_router(health.router)
    app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
    app.include_router(scoreboard.router, prefix="/api/v1", tags=["scoreboard"])
    app.include_router(companies.router, prefix="/api/v1", tags=["companies"])
    app.include_router(industries.router, prefix="/api/v1", tags=["industries"])
    app.include_router(countries.router, prefix="/api/v1", tags=["countries"])
    app.include_router(models.router, prefix="/api/v1", tags=["models"])
    app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])
    app.include_router(confidence.router, prefix="/api/v1", tags=["confidence"])
    app.include_router(ai_economics.router, prefix="/api/v1", tags=["ai-economics"])
    app.include_router(roi_calculator.router, prefix="/api/v1", tags=["roi-calculator"])
    app.include_router(sources.router, prefix="/api/v1", tags=["sources"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
    return app


app = create_app()
