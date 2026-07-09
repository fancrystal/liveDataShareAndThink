from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="LiveDataShareAndThink")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "live-data-share-and-think",
            "phase": "content-growth",
        }

    return app


app = create_app()
