from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    ingredients = Column(JSON)
    instructions = Column(String)
    match_percentage = Column(Float)
    is_favorite = Column(Boolean, default=False) 