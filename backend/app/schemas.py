from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class RecordLink(BaseModel):
    target_id: UUID
    relationship_type: str = Field(min_length=2, max_length=60)

class RecordCreate(BaseModel):
    category: str = Field(min_length=2, max_length=40)
    title: str = Field(min_length=2, max_length=250)
    code: str | None = Field(default=None, max_length=80)
    status: str = Field(default="فعال", max_length=40)
    data: dict[str, Any] = Field(default_factory=dict)
    links: list[RecordLink] = Field(default_factory=list)

class RecordUpdate(RecordCreate):
    pass

class RecordRead(RecordCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime

class RelationshipCreate(BaseModel):
    source_id: UUID
    target_id: UUID
    relationship_type: str = Field(min_length=2, max_length=60)
    description: str | None = None

class RelationshipRead(RelationshipCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime

class WeightedScoreItem(BaseModel):
    record_id: UUID
    score: float = Field(ge=0)
    weight: float = Field(gt=0)

class WeightedScoreRequest(BaseModel):
    items: list[WeightedScoreItem] = Field(min_length=1)
    normalize_weights: bool = True
