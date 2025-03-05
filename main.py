from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from agents.vision_agent import VisionAgent
from agents.recipe_agent import RecipeAgent
from config import Config

class CookScanApp:
    def __init__(self, openai_api_key):
        self.vision_agent = VisionAgent(openai_api_key)
        self.recipe_agent = RecipeAgent(openai_api_key)

    def run(self, image_paths):
        # Detect ingredients from images
        ingredients = self.vision_agent.analyze_images(image_paths)
        
        # Get recipe suggestions based on ingredients
        recipes = self.recipe_agent.suggest_recipes(ingredients)
        
        return recipes 