from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.base import Base
from app.database.connection import engine

# Import models so SQLAlchemy registers them.
from app.models.category import Category
from app.models.recipe import Recipe

from app.routers.recipes import router as recipe_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database tables.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Close database connections.
    await engine.dispose()


app = FastAPI(
    title="Recipe API",
    description="Stage 1 - Basic Recipe CRUD",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(recipe_router)


@app.get("/")
async def root():
    return {
        "message": "Recipe API is running",
        "stage": "Stage 1 - Basic Recipe CRUD",
    }