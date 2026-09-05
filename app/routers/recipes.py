from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.schemas.recipe import (
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
)
from app.services import recipe as recipe_service


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


# ============================================================
# LESSON 20
# POST /recipes
# Create a recipe
# ============================================================

@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a recipe",
)
async def create_recipe(
    data: RecipeCreate,
    session: AsyncSession = Depends(get_session),
):
    recipe = await recipe_service.create_recipe(
        session,
        data,
    )

    return recipe


# ============================================================
# LESSON 21
# GET /recipes
# List all recipes
# ============================================================

@router.get(
    "",
    response_model=list[RecipeResponse],
    status_code=status.HTTP_200_OK,
    summary="List recipes",
)
async def list_recipes(
    session: AsyncSession = Depends(get_session),
):
    recipes = await recipe_service.get_all_recipes(
        session
    )

    return recipes


# ============================================================
# LESSON 22
# GET /recipes/{id}
# Retrieve one recipe
# ============================================================

@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a recipe",
)
async def get_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    recipe = await recipe_service.get_recipe(
        session,
        recipe_id,
    )

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return recipe


# ============================================================
# LESSON 23
# PUT /recipes/{id}
# Update recipe
# ============================================================

@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a recipe",
)
async def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    session: AsyncSession = Depends(get_session),
):
    recipe = await recipe_service.get_recipe(
        session,
        recipe_id,
    )

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    updated_recipe = await recipe_service.update_recipe(
        session,
        recipe,
        data,
    )

    return updated_recipe


# ============================================================
# LESSON 24
# DELETE /recipes/{id}
# Delete recipe
# ============================================================

@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recipe",
)
async def delete_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    recipe = await recipe_service.get_recipe(
        session,
        recipe_id,
    )

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    await recipe_service.delete_recipe(
        session,
        recipe,
    )

    return None