from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.database.connection import get_session
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.ingredient import Ingredient
from app.models.user import User
from app.schemas.recipe import (
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
)


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


# ============================================================
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
    current_user: User = Depends(get_current_user),
):

    recipe = Recipe(
        name=recipe_data.name,
        description=recipe_data.description,
        category_id=recipe_data.category_id,
        is_public=recipe_data.is_public,
        prep_minutes=recipe_data.prep_minutes,
        cook_minutes=recipe_data.cook_minutes,
        owner_id=current_user.id,
    )

    session.add(recipe)

    await session.commit()
    await session.refresh(recipe)

    return recipe


# ============================================================
# LIST AUTHENTICATED USER'S RECIPES + STAGE 3/5 SEARCH
# ============================================================

@router.get(
    "",
    response_model=list[RecipeResponse],
)
async def list_recipes(
    search: str | None = Query(
        default=None,
        min_length=1,
    ),

    ingredient: list[str] | None = Query(
        default=None,
    ),

    category: str | None = Query(
        default=None,
    ),

    max_time: int | None = Query(
        default=None,
        ge=0,
    ),

    page: int = Query(
        default=1,
        ge=1,
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),

    session: AsyncSession = Depends(get_session),

    current_user: User = Depends(get_current_user),
):

    query = (
        select(Recipe)
        .join(
            Recipe.category,
            isouter=True,
        )
        .where(
            Recipe.owner_id == current_user.id
        )
    )

    # --------------------------------------------------------
    # Search by recipe name
    # --------------------------------------------------------

    if search:
        query = query.where(
            Recipe.name.ilike(f"%{search}%")
        )

    # --------------------------------------------------------
    # Search by category
    # --------------------------------------------------------

    if category:
        from app.models.category import Category

        query = query.where(
            Category.name.ilike(f"%{category}%")
        )

    # --------------------------------------------------------
    # STAGE 5
    # Multiple ingredient filtering
    #
    # ?ingredient=chicken&ingredient=rice
    #
    # Recipe must contain BOTH ingredients.
    # --------------------------------------------------------

    if ingredient:

        normalized_ingredients = [
            item.strip().lower()
            for item in ingredient
            if item.strip()
        ]

        normalized_ingredients = list(
            dict.fromkeys(normalized_ingredients)
        )

        if normalized_ingredients:

            ingredient_subquery = (
                select(
                    RecipeIngredient.recipe_id
                )
                .join(
                    Ingredient,
                    Ingredient.id
                    == RecipeIngredient.ingredient_id,
                )
                .where(
                    func.lower(Ingredient.name).in_(
                        normalized_ingredients
                    )
                )
                .group_by(
                    RecipeIngredient.recipe_id
                )
                .having(
                    func.count(
                        func.distinct(
                            func.lower(Ingredient.name)
                        )
                    )
                    == len(normalized_ingredients)
                )
            )

            query = query.where(
                Recipe.id.in_(ingredient_subquery)
            )

    # --------------------------------------------------------
    # STAGE 5
    # Maximum total time
    #
    # prep_minutes + cook_minutes <= max_time
    # --------------------------------------------------------

    if max_time is not None:

        total_time = (
            func.coalesce(
                Recipe.prep_minutes,
                0,
            )
            +
            func.coalesce(
                Recipe.cook_minutes,
                0,
            )
        )

        query = query.where(
            total_time <= max_time
        )

    # --------------------------------------------------------
    # Sorting
    # --------------------------------------------------------

    query = query.order_by(
        Recipe.created_at.desc()
    )

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    offset = (page - 1) * limit

    query = query.offset(
        offset
    ).limit(
        limit
    )

    result = await session.execute(query)

    recipes = result.scalars().unique().all()

    return recipes


# ============================================================
# PUBLIC RECIPES
# ============================================================

@router.get(
    "/public",
    response_model=list[RecipeResponse],
)
async def list_public_recipes(
    session: AsyncSession = Depends(get_session),
):

    result = await session.execute(
        select(Recipe)
        .where(
            Recipe.is_public.is_(True)
        )
        .order_by(
            Recipe.created_at.desc()
        )
    )

    return result.scalars().all()


# ============================================================
# GET RECIPE BY ID
# ============================================================

@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
)
async def get_recipe(
    recipe_id: int,

    session: AsyncSession = Depends(get_session),

    current_user: User = Depends(get_current_user),
):

    result = await session.execute(
        select(Recipe)
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    # Owner can always view the recipe.
    if recipe.owner_id == current_user.id:
        return recipe

    # Other authenticated users can only view public recipes.
    if recipe.is_public:
        return recipe

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not allowed to view this recipe",
    )


# ============================================================
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

    current_user: User = Depends(get_current_user),
):

    result = await session.execute(
        select(Recipe)
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own recipes",
        )

    update_data = recipe_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            recipe,
            field,
            value,
        )

    await session.commit()
    await session.refresh(recipe)

    return recipe


# ============================================================
# DELETE RECIPE
# ============================================================

@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipe(
    recipe_id: int,

    session: AsyncSession = Depends(get_session),

    current_user: User = Depends(get_current_user),
):

    result = await session.execute(
        select(Recipe)
        .where(
            Recipe.id == recipe_id
        )
    )

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )

    if recipe.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own recipes",
        )

    await session.delete(recipe)

    await session.commit()

    return None