from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def import_models() -> None:
    from app.collection import models as collection_models
    from app.projects import models as project_models

    del collection_models
    del project_models
