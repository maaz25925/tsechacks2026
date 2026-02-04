from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers.creator import router as creator_router
from app.routers.discovery import router as discovery_router
from app.routers.payments import router as payments_router
from app.routers.reviews import router as reviews_router
from app.routers.sessions import router as sessions_router
from app.routers.wallet import router as wallet_router
from app.schemas import HealthResponse
from app.services.seed import seed_fake_data


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title="Murph Backend", version="0.1.0")

    # CORS for Vite dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Keep errors JSON for frontend; avoid leaking internals in production.
        if s.env.lower() == "dev":
            return JSONResponse(
                status_code=500,
                content={"error": {"message": str(exc), "code": "INTERNAL_ERROR"}},
            )
        return JSONResponse(
            status_code=500,
            content={"error": {"message": "Internal server error", "code": "INTERNAL_ERROR"}},
        )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse()

    @app.get("/config")
    def config_public() -> dict:
        # Helpful during hackathon dev. Do not expose secrets.
        return get_settings().to_public_dict()

    app.include_router(discovery_router)
    app.include_router(wallet_router)
    app.include_router(sessions_router)
    app.include_router(payments_router)
    app.include_router(reviews_router)
    app.include_router(creator_router)

    @app.on_event("startup")
    def _seed() -> None:
        # Seeds fake users + listings for quick frontend demo.
        seed_fake_data()

    return app


app = create_app()

