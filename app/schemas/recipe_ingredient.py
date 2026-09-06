from pydantic import BaseModel, ConfigDict, Field


class RecipeIngredientCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    amount: float | None = Field(
        default=None,
        ge=0
    )

    unit: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    preparation: str | None = Field(
        default=None,
        max_length=255
    )


class RecipeIngredientUpdate(BaseModel):
    amount: float | None = Field(
        default=None,
        ge=0
    )

    unit: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )

    preparation: str | None = Field(
        default=None,
        max_length=255
    )


class RecipeIngredientResponse(BaseModel):
    id: int
    recipe_id: int
    ingredient_id: int
    amount: float | None
    unit: str
    preparation: str | None

    ingredient: "IngredientResponse"

    model_config = ConfigDict(
        from_attributes=True
    )


from app.schemas.ingredient import IngredientResponse