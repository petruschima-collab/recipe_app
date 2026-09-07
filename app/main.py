from fastapi import FastAPI

from app.routers.recipes import router as recipes_router


app = FastAPI(
    title="Recipe API",
    version="1.0.0",
)


app.include_router(
    recipes_router
)