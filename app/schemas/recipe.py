from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecipeCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    category_id: int | None = Field(
        default=None,
        gt=0,
    )


class RecipeUpdate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    category_id: int | None = Field(
        default=None,
        gt=0,
    )


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category_id: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )