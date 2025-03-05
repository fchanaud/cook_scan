import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')
    
    # Vision model settings
    CONFIDENCE_THRESHOLD = 0.5
    
    # Recipe matching settings
    MIN_MATCH_PERCENTAGE = 0.8
    MAX_RECIPES = 10 