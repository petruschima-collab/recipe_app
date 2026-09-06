from app.routers.recipes import router as recipes_router
from app.routers.ingredients import router as ingredients_router


__all__ = [
    "recipes_router",
    "ingredients_router",
]