from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BrandProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    positioning: str = Field(min_length=1)
    target_audience: str = Field(min_length=1)
    tone: str = Field(min_length=1)
    core_value: str = Field(min_length=1)
    forbidden_terms: list[str] = Field(default_factory=list)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    brand_profile: BrandProfileCreate


class BrandProfileRead(BrandProfileCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    brand_profile: BrandProfileRead

