from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class RecipeStep(Base):
    __tablename__ = "recipe_steps"

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

    step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    instruction: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    recipe: Mapped["Recipe"] = relationship(
        "Recipe",
        back_populates="steps",
    )