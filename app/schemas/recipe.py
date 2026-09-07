from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# RECIPE CREATE
# ============================================================

class RecipeCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
    )

    category_id: int | None = Field(
        default=None,
        gt=0,
    )


# ============================================================
# RECIPE UPDATE
# ============================================================

class RecipeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
    )

    category_id: int | None = Field(
        default=None,
        gt=0,
    )


# ============================================================
# CATEGORY RESPONSE
# ============================================================

class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# INGREDIENT RESPONSE
# ============================================================

class IngredientResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# RECIPE INGREDIENT RESPONSE
# ============================================================

class RecipeIngredientResponse(BaseModel):
    id: int
    recipe_id: int
    ingredient_id: int
    amount: float | None
    unit: str
    preparation: str | None

    ingredient: IngredientResponse

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# RECIPE STEP RESPONSE
# ============================================================

class RecipeStepResponse(BaseModel):
    id: int
    step_number: int
    instruction: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# RECIPE RESPONSE
# ============================================================

class RecipeResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category: CategoryResponse | None
    created_at: datetime

    ingredients: list[
        RecipeIngredientResponse
    ] = []

    steps: list[
        RecipeStepResponse
    ] = []

    model_config = ConfigDict(
        from_attributes=True
    )