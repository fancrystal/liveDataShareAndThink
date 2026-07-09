from fastapi import FastAPI

from app.collection.router import router as collection_router
from app.core.config import get_settings
from app.db.base import Base, import_models
from app.db.session import build_engine, build_session_factory
from app.projects.router import router as projects_router


def create_app(database_url: str | None = None) -> FastAPI:
    app = FastAPI(title="LiveDataShareAndThink")
    settings = get_settings()
    engine = build_engine(database_url or settings.database_url)
    import_models()
    Base.metadata.create_all(engine)
    app.state.engine = engine
    app.state.session_factory = build_session_factory(engine)
    app.include_router(projects_router)
    app.include_router(collection_router)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "live-data-share-and-think",
            "phase": "content-growth",
        }

    return app


app = create_app()
