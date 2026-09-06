from typing import Optional

from sqlalchemy import ForeignKey, Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    __table_args__ = (
        UniqueConstraint(
            "recipe_id",
            "ingredient_id",
            name="uq_recipe_ingredient"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    amount: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    preparation: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    recipe: Mapped["Recipe"] = relationship(
        "Recipe",
        back_populates="recipe_ingredients"
    )

    ingredient: Mapped["Ingredient"] = relationship(
        "Ingredient",
        back_populates="recipe_ingredients"
    )