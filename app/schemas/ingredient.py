from pydantic import BaseModel, ConfigDict, Field


class IngredientBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )