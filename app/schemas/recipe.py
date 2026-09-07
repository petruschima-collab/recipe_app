from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecipeBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    category_id: int | None = None

    is_public: bool = False

    prep_minutes: int = Field(
        default=0,
        ge=0,
    )

    cook_minutes: int = Field(
        default=0,
        ge=0,
    )


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    category_id: int | None = None

    is_public: bool | None = None

    prep_minutes: int | None = Field(
        default=None,
        ge=0,
    )

    cook_minutes: int | None = Field(
        default=None,
        ge=0,
    )


class RecipeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    description: str | None
    category_id: int | None
    owner_id: int
    is_public: bool
    prep_minutes: int
    cook_minutes: int
    created_at: datetime