from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.projects.models import BrandProfile, Project
from app.projects.schemas import ProjectCreate


class ProjectService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, payload: ProjectCreate) -> Project:
        project = Project(name=payload.name, description=payload.description)
        project.brand_profile = BrandProfile(**payload.brand_profile.model_dump())
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def get(self, project_id: str) -> Project:
        project = self.session.get(Project, project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def list(self) -> list[Project]:
        return list(self.session.scalars(select(Project).order_by(Project.created_at)))

