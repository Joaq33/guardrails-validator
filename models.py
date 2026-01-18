from typing import Literal
from pydantic import BaseModel, Field


class HeroCapabilities(BaseModel):
    """Schema for validating superhero capabilities."""

    can_fly: bool = Field(description="Whether the character has the ability to fly")
    has_super_strength: bool = Field(
        description="Whether the character possesses superhuman strength"
    )
    gender: Literal["male", "female", "unknown"] = Field(
        description="The character's gender identity"
    )
