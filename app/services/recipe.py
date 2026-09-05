from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import Recipe
from app.repositories import recipe as recipe_repository
from app.schemas.recipe import RecipeCreate, RecipeUpdate


async def create_recipe(
    session: AsyncSession,
    data: RecipeCreate,
) -> Recipe:

    recipe = Recipe(
        name=data.name,
        description=data.description,
        category_id=data.category_id,
    )

    return await recipe_repository.create_recipe(
        session,
        recipe,
    )


async def get_all_recipes(
    session: AsyncSession,
) -> list[Recipe]:

    return await recipe_repository.get_all_recipes(
        session
    )


async def get_recipe(
    session: AsyncSession,
    recipe_id: int,
) -> Recipe | None:

    return await recipe_repository.get_recipe_by_id(
        session,
        recipe_id,
    )


async def update_recipe(
    session: AsyncSession,
    recipe: Recipe,
    data: RecipeUpdate,
) -> Recipe:

    recipe.name = data.name
    recipe.description = data.description
    recipe.category_id = data.category_id

    return await recipe_repository.update_recipe(
        session,
        recipe,
    )


async def delete_recipe(
    session: AsyncSession,
    recipe: Recipe,
) -> None:

    await recipe_repository.delete_recipe(
        session,
        recipe,
    )