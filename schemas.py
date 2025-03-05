from pydantic import BaseModel
from typing import List, Optional

class RecipeBase(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    match_percentage: float

class Recipe(RecipeBase):
    id: int
    is_favorite: bool

    class Config:
        from_attributes = True 