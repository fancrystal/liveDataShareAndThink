from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.analysis.router import router as analysis_router
from app.collection.router import router as collection_router
from app.core.config import get_settings
from app.db.base import Base, import_models
from app.db.session import build_engine, build_session_factory
from app.generation.router import router as generation_router
from app.projects.router import router as projects_router


def create_app(database_url: str | None = None) -> FastAPI:
    app = FastAPI(title="LiveDataShareAndThink")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:17777",
            "http://127.0.0.1:17777",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    settings = get_settings()
    engine = build_engine(database_url or settings.database_url)
    import_models()
    Base.metadata.create_all(engine)
    app.state.engine = engine
    app.state.session_factory = build_session_factory(engine)
    app.include_router(projects_router)
    app.include_router(collection_router)
    app.include_router(analysis_router)
    app.include_router(generation_router)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "live-data-share-and-think",
            "phase": "content-growth",
        }

    @app.get("/api/collection-proxy/status")
    def collection_proxy_status() -> dict[str, bool | str]:
        configured = bool(settings.collection_proxy_url and settings.collection_proxy_token)
        return {
            "configured": configured,
            "message": "Local collection proxy configured" if configured else "Local collection proxy needs configuration",
        }

    return app


app = create_app()
