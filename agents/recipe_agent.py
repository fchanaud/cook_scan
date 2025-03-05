from crewai import Agent
import requests
from langchain.tools import Tool
from typing import List, Dict

class RecipeAgent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.spoonacular.com/recipes"
        
    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="search_recipes",
                func=self.search_recipes,
                description="Search for recipes based on available ingredients. Input should be a list of ingredients."
            ),
            Tool(
                name="suggest_substitutions",
                func=self.suggest_substitutions,
                description="Suggest possible substitutions for missing ingredients. Input should be an ingredient name."
            ),
            Tool(
                name="rank_recipes",
                func=self.rank_recipes,
                description="Rank recipes by simplicity and match percentage. Input should be a list of recipes."
            ),
            Tool(
                name="analyze_nutrition",
                func=self.analyze_nutrition,
                description="Analyze nutritional content of recipes. Input should be a recipe ID."
            )
        ]
        
    def search_recipes(self, ingredients: List[str], min_match_percentage: float = 0.8) -> List[Dict]:
        """
        Search for recipes based on available ingredients
        """
        try:
            # Convert ingredients list to comma-separated string
            ingredients_str = ','.join(ingredients)
            
            # API endpoint for recipe search
            endpoint = f"{self.base_url}/findByIngredients"
            
            params = {
                "apiKey": self.api_key,
                "ingredients": ingredients_str,
                "number": 10,
                "ranking": 2,  # Maximize used ingredients
                "ignorePantry": True
            }
            
            response = requests.get(endpoint, params=params)
            recipes = response.json()
            
            # Filter and rank recipes based on match percentage
            filtered_recipes = []
            for recipe in recipes:
                used_count = len(recipe['usedIngredients'])
                total_required = used_count + len(recipe['missedIngredients'])
                match_percentage = used_count / total_required
                
                if match_percentage >= min_match_percentage:
                    recipe['match_percentage'] = match_percentage
                    filtered_recipes.append(recipe)
            
            # Sort by number of ingredients (ascending) and match percentage (descending)
            filtered_recipes.sort(key=lambda x: (
                len(x['usedIngredients']) + len(x['missedIngredients']),
                -x['match_percentage']
            ))
            
            return self.rank_recipes(filtered_recipes)
            
        except Exception as e:
            return f"Error searching recipes: {str(e)}"
    
    def suggest_substitutions(self, ingredient: str) -> List[str]:
        """
        Suggest possible substitutions for missing ingredients
        """
        try:
            endpoint = f"{self.base_url}/substitutes"
            
            params = {
                "apiKey": self.api_key,
                "ingredientName": ingredient
            }
            
            response = requests.get(endpoint, params=params)
            substitutes = response.json()
            
            return substitutes.get('substitutes', [])
            
        except Exception as e:
            return f"Error finding substitutions: {str(e)}"
            
    def rank_recipes(self, recipes: List[Dict]) -> List[Dict]:
        """Rank recipes by simplicity and match percentage"""
        return sorted(
            recipes,
            key=lambda x: (
                len(x['usedIngredients']) + len(x['missedIngredients']),
                -x['match_percentage']
            )
        )
        
    def analyze_nutrition(self, recipe_id: int) -> Dict:
        """Analyze nutritional content of a recipe"""
        try:
            endpoint = f"{self.base_url}/{recipe_id}/nutritionWidget.json"
            
            params = {
                "apiKey": self.api_key
            }
            
            response = requests.get(endpoint, params=params)
            return response.json()
            
        except Exception as e:
            return f"Error analyzing nutrition: {str(e)}" 