from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.recipe_ingredient import RecipeIngredient
from app.schemas.recipe_ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
    RecipeIngredientResponse,
)


router = APIRouter(
    prefix="/recipes",
    tags=["Recipe Ingredients"]
)


# ============================================================
# LESSON 25
# CREATE INGREDIENT FOR A RECIPE
# ============================================================

@router.post(
    "/{recipe_id}/ingredients",
    response_model=RecipeIngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe_ingredient(
    recipe_id: int,
    data: RecipeIngredientCreate,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # Check that the recipe exists
    # --------------------------------------------------------

    recipe_result = await session.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # Find ingredient by name
    # --------------------------------------------------------

    ingredient_result = await session.execute(
        select(Ingredient).where(
            Ingredient.name.ilike(data.name.strip())
        )
    )

    ingredient = ingredient_result.scalar_one_or_none()

    # --------------------------------------------------------
    # Create ingredient if it doesn't exist
    # --------------------------------------------------------

    if ingredient is None:
        ingredient = Ingredient(
            name=data.name.strip()
        )

        session.add(ingredient)

        await session.flush()

    # --------------------------------------------------------
    # Prevent duplicate ingredient in same recipe
    # --------------------------------------------------------

    existing_result = await session.execute(
        select(RecipeIngredient).where(
            RecipeIngredient.recipe_id == recipe_id,
            RecipeIngredient.ingredient_id == ingredient.id,
        )
    )

    existing = existing_result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ingredient already exists in this recipe",
        )

    # --------------------------------------------------------
    # Create relationship record
    # --------------------------------------------------------

    recipe_ingredient = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=ingredient.id,
        amount=data.amount,
        unit=data.unit,
        preparation=data.preparation,
    )

    session.add(recipe_ingredient)

    await session.commit()

    # --------------------------------------------------------
    # Reload with ingredient relationship
    # --------------------------------------------------------

    result = await session.execute(
        select(RecipeIngredient)
        .options(
            selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(
            RecipeIngredient.id == recipe_ingredient.id
        )
    )

    recipe_ingredient = result.scalar_one()

    return recipe_ingredient


# ============================================================
# LESSON 26
# GET RECIPE INGREDIENTS
# ============================================================

@router.get(
    "/{recipe_id}/ingredients",
    response_model=list[RecipeIngredientResponse],
)
async def get_recipe_ingredients(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # Check recipe
    # --------------------------------------------------------

    recipe_result = await session.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # Get ingredients
    # --------------------------------------------------------

    result = await session.execute(
        select(RecipeIngredient)
        .options(
            selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(
            RecipeIngredient.recipe_id == recipe_id
        )
        .order_by(
            RecipeIngredient.id
        )
    )

    return result.scalars().all()


# ============================================================
# LESSON 27
# UPDATE RECIPE INGREDIENT
# ============================================================

@router.put(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    response_model=RecipeIngredientResponse,
)
async def update_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    data: RecipeIngredientUpdate,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # Find relationship record
    # --------------------------------------------------------

    result = await session.execute(
        select(RecipeIngredient)
        .options(
            selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(
            RecipeIngredient.id == recipe_ingredient_id,
            RecipeIngredient.recipe_id == recipe_id,
        )
    )

    recipe_ingredient = result.scalar_one_or_none()

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    # --------------------------------------------------------
    # Update only supplied fields
    # --------------------------------------------------------

    if data.amount is not None:
        recipe_ingredient.amount = data.amount

    if data.unit is not None:
        recipe_ingredient.unit = data.unit

    if data.preparation is not None:
        recipe_ingredient.preparation = data.preparation

    await session.commit()

    await session.refresh(recipe_ingredient)

    # --------------------------------------------------------
    # Ensure relationship is loaded
    # --------------------------------------------------------

    result = await session.execute(
        select(RecipeIngredient)
        .options(
            selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(
            RecipeIngredient.id == recipe_ingredient_id
        )
    )

    return result.scalar_one()


# ============================================================
# LESSON 28
# DELETE RECIPE INGREDIENT
# ============================================================

@router.delete(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    session: AsyncSession = Depends(get_session),
):
    # --------------------------------------------------------
    # Find relationship record
    # --------------------------------------------------------

    result = await session.execute(
        select(RecipeIngredient).where(
            RecipeIngredient.id == recipe_ingredient_id,
            RecipeIngredient.recipe_id == recipe_id,
        )
    )

    recipe_ingredient = result.scalar_one_or_none()

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    # --------------------------------------------------------
    # Delete relationship
    # --------------------------------------------------------

    await session.delete(recipe_ingredient)

    await session.commit()

    return None