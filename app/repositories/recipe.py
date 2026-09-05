from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import Recipe


async def create_recipe(
    session: AsyncSession,
    recipe: Recipe,
) -> Recipe:

    session.add(recipe)

    await session.commit()

    await session.refresh(recipe)

    return recipe


async def get_all_recipes(
    session: AsyncSession,
) -> list[Recipe]:

    result = await session.execute(
        select(Recipe).order_by(Recipe.id)
    )

    return list(result.scalars().all())


async def get_recipe_by_id(
    session: AsyncSession,
    recipe_id: int,
) -> Recipe | None:

    result = await session.execute(
        select(Recipe).where(
            Recipe.id == recipe_id
        )
    )

    return result.scalar_one_or_none()


async def update_recipe(
    session: AsyncSession,
    recipe: Recipe,
) -> Recipe:

    await session.commit()

    await session.refresh(recipe)

    return recipe


async def delete_recipe(
    session: AsyncSession,
    recipe: Recipe,
) -> None:

    await session.delete(recipe)

    await session.commit()