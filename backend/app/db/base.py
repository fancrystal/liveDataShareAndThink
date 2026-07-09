from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def import_models() -> None:
    from app.analysis import models as analysis_models
    from app.collection import models as collection_models
    from app.generation import models as generation_models
    from app.projects import models as project_models

    del analysis_models
    del collection_models
    del generation_models
    del project_models
