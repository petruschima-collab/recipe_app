from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey(
            "recipes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id"),
        nullable=False,
    )

    amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    preparation: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    recipe: Mapped["Recipe"] = relationship(
        "Recipe",
        back_populates="ingredients",
    )

    ingredient: Mapped["Ingredient"] = relationship(
        "Ingredient",
        back_populates="recipe_ingredients",
    )