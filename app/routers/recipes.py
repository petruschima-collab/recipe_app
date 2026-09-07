from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.connection import get_session

from app.models.recipe import Recipe
from app.models.category import Category
from app.models.ingredient import Ingredient
from app.models.recipe_ingredient import RecipeIngredient
from app.models.recipe_step import RecipeStep

from app.schemas.recipe import (
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
)

from app.schemas.recipe_ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
    RecipeIngredientResponse,
)


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


# ============================================================
# STAGE 1
# CREATE RECIPE
# ============================================================

@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(
    recipe_data: RecipeCreate,
    session: AsyncSession = Depends(get_session),
):
    recipe = Recipe(
        **recipe_data.model_dump()
    )

    session.add(recipe)

    await session.commit()
    await session.refresh(recipe)

    return recipe


# ============================================================
# STAGE 3 — LESSON 30–33
#
# LIST + SEARCH + FILTER + PAGINATION + SORTING
# ============================================================

@router.get(
    "",
    response_model=list[RecipeResponse],
    status_code=status.HTTP_200_OK,
)
async def list_recipes(
    search: Optional[str] = Query(
        default=None,
        description="Search by recipe name",
    ),

    ingredient: Optional[str] = Query(
        default=None,
        description="Search by ingredient name",
    ),

    category: Optional[str] = Query(
        default=None,
        description="Search by category name",
    ),

    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of recipes per page",
    ),

    sort_by: str = Query(
        default="created_at",
        description="Sort field",
    ),

    sort_order: str = Query(
        default="desc",
        description="asc or desc",
    ),

    session: AsyncSession = Depends(get_session),
):
    """
    Stage 3 search endpoint.

    Supports:

    GET /recipes

    GET /recipes?search=pasta

    GET /recipes?ingredient=tomato

    GET /recipes?category=dinner

    GET /recipes?search=chicken&category=dinner

    GET /recipes?page=1&limit=10

    GET /recipes?sort_by=name&sort_order=asc
    """

    # --------------------------------------------------------
    # Allowed sorting fields
    # --------------------------------------------------------

    allowed_sort_fields = {
        "id": Recipe.id,
        "name": Recipe.name,
        "created_at": Recipe.created_at,
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid sort_by. "
                "Use id, name, or created_at."
            ),
        )

    if sort_order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "sort_order must be either "
                "'asc' or 'desc'."
            ),
        )

    # --------------------------------------------------------
    # Base query
    # --------------------------------------------------------

    stmt = (
        select(Recipe)
        .options(
            selectinload(Recipe.category),
            selectinload(Recipe.ingredients)
            .selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.steps),
        )
    )

    # --------------------------------------------------------
    # LESSON 30
    # Search by recipe name
    #
    # GET /recipes?search=pasta
    # --------------------------------------------------------

    if search:
        search_term = search.strip()

        if search_term:
            stmt = stmt.where(
                func.lower(Recipe.name).like(
                    f"%{search_term.lower()}%"
                )
            )

    # --------------------------------------------------------
    # LESSON 31
    # Search by ingredient
    #
    # GET /recipes?ingredient=tomato
    # --------------------------------------------------------

    if ingredient:
        ingredient_term = ingredient.strip()

        if ingredient_term:
            stmt = (
                stmt
                .join(
                    RecipeIngredient,
                    RecipeIngredient.recipe_id == Recipe.id,
                )
                .join(
                    Ingredient,
                    Ingredient.id
                    == RecipeIngredient.ingredient_id,
                )
                .where(
                    func.lower(Ingredient.name).like(
                        f"%{ingredient_term.lower()}%"
                    )
                )
            )

    # --------------------------------------------------------
    # LESSON 32
    # Search by category
    #
    # GET /recipes?category=dinner
    # --------------------------------------------------------

    if category:
        category_term = category.strip()

        if category_term:
            stmt = (
                stmt
                .join(
                    Category,
                    Category.id == Recipe.category_id,
                )
                .where(
                    func.lower(Category.name).like(
                        f"%{category_term.lower()}%"
                    )
                )
            )

    # --------------------------------------------------------
    # Remove duplicate recipes caused by joins
    # --------------------------------------------------------

    stmt = stmt.distinct()

    # --------------------------------------------------------
    # LESSON 33
    # Sorting
    # --------------------------------------------------------

    sort_column = allowed_sort_fields[sort_by]

    if sort_order == "asc":
        stmt = stmt.order_by(
            asc(sort_column)
        )
    else:
        stmt = stmt.order_by(
            desc(sort_column)
        )

    # --------------------------------------------------------
    # LESSON 33
    # Pagination
    # --------------------------------------------------------

    offset = (page - 1) * limit

    stmt = (
        stmt
        .offset(offset)
        .limit(limit)
    )

    # --------------------------------------------------------
    # Execute asynchronously
    # --------------------------------------------------------

    result = await session.execute(stmt)

    recipes = (
        result
        .scalars()
        .unique()
        .all()
    )

    return recipes


# ============================================================
# STAGE 1
# GET ONE RECIPE
# ============================================================

@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
async def get_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(Recipe)
        .options(
            selectinload(Recipe.category),
            selectinload(Recipe.ingredients)
            .selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.steps),
        )
        .where(Recipe.id == recipe_id)
    )

    result = await session.execute(stmt)

    recipe = result.scalars().unique().first()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    return recipe


# ============================================================
# STAGE 1
# UPDATE RECIPE
# ============================================================

@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
async def update_recipe(
    recipe_id: int,
    recipe_data: RecipeUpdate,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Recipe).where(
        Recipe.id == recipe_id
    )

    result = await session.execute(stmt)

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    update_data = recipe_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(recipe, field, value)

    await session.commit()
    await session.refresh(recipe)

    return recipe


# ============================================================
# STAGE 1
# DELETE RECIPE
# ============================================================

@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Recipe).where(
        Recipe.id == recipe_id
    )

    result = await session.execute(stmt)

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    await session.delete(recipe)

    await session.commit()

    return None


# ============================================================
# STAGE 2
# ADD INGREDIENT TO RECIPE
# ============================================================

@router.post(
    "/{recipe_id}/ingredients",
    response_model=RecipeIngredientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_recipe_ingredient(
    recipe_id: int,
    ingredient_data,
    session: AsyncSession = Depends(get_session),
):
    recipe_stmt = select(Recipe).where(
        Recipe.id == recipe_id
    )

    recipe_result = await session.execute(
        recipe_stmt
    )

    recipe = recipe_result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # --------------------------------------------------------
    # Find existing ingredient
    # --------------------------------------------------------

    ingredient_stmt = select(Ingredient).where(
        func.lower(Ingredient.name)
        == ingredient_data.name.lower()
    )

    ingredient_result = await session.execute(
        ingredient_stmt
    )

    ingredient = (
        ingredient_result
        .scalar_one_or_none()
    )

    # --------------------------------------------------------
    # Create ingredient if it doesn't exist
    # --------------------------------------------------------

    if ingredient is None:
        ingredient = Ingredient(
            name=ingredient_data.name
        )

        session.add(ingredient)

        await session.flush()

    # --------------------------------------------------------
    # Create relationship
    # --------------------------------------------------------

    recipe_ingredient = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=ingredient.id,
        amount=ingredient_data.amount,
        unit=ingredient_data.unit,
        preparation=ingredient_data.preparation,
    )

    session.add(recipe_ingredient)

    await session.commit()

    await session.refresh(
        recipe_ingredient
    )

    return recipe_ingredient


# ============================================================
# STAGE 2
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
    recipe_stmt = select(Recipe.id).where(
        Recipe.id == recipe_id
    )

    recipe_result = await session.execute(
        recipe_stmt
    )

    recipe_exists = recipe_result.scalar_one_or_none()

    if recipe_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    stmt = (
        select(RecipeIngredient)
        .options(
            selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(
            RecipeIngredient.recipe_id
            == recipe_id
        )
    )

    result = await session.execute(stmt)

    return result.scalars().all()


# ============================================================
# STAGE 2
# UPDATE RECIPE INGREDIENT
# ============================================================

@router.put(
    "/{recipe_id}/ingredients/{recipe_ingredient_id}",
    response_model=RecipeIngredientResponse,
)
async def update_recipe_ingredient(
    recipe_id: int,
    recipe_ingredient_id: int,
    ingredient_data,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(RecipeIngredient)
        .options(
            selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(
            RecipeIngredient.id
            == recipe_ingredient_id,
            RecipeIngredient.recipe_id
            == recipe_id,
        )
    )

    result = await session.execute(stmt)

    recipe_ingredient = (
        result
        .scalar_one_or_none()
    )

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    update_data = ingredient_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        if field != "name":
            setattr(
                recipe_ingredient,
                field,
                value,
            )

    await session.commit()

    await session.refresh(
        recipe_ingredient
    )

    return recipe_ingredient


# ============================================================
# STAGE 2
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
    stmt = select(RecipeIngredient).where(
        RecipeIngredient.id
        == recipe_ingredient_id,
        RecipeIngredient.recipe_id
        == recipe_id,
    )

    result = await session.execute(stmt)

    recipe_ingredient = (
        result
        .scalar_one_or_none()
    )

    if recipe_ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe ingredient not found",
        )

    await session.delete(
        recipe_ingredient
    )

    await session.commit()

    return None