from langchain_openai import ChatOpenAI
from database.database import get_supabase
import logging

logger = logging.getLogger(__name__)

class RecipeAgent:
    def __init__(self, openai_api_key):
        logger.info("Initializing RecipeAgent...")
        self.llm = ChatOpenAI(
            model="gpt-4",
            api_key=openai_api_key,
            temperature=0.7
        )
        self.supabase = get_supabase()

    def suggest_recipes(self, ingredients):
        try:
            logger.info(f"Generating recipes for ingredients: {ingredients}")
            # Format ingredients for prompt
            ingredients_text = ", ".join(ingredients)
            
            # Create prompt for recipe generation
            prompt = [
                {
                    "role": "system",
                    "content": """You are a creative chef. Generate a recipe using the provided ingredients.
                    Format the recipe with a title and clear instructions.
                    Keep it concise but detailed enough to follow."""
                },
                {
                    "role": "user",
                    "content": f"Create a recipe using these ingredients: {ingredients_text}"
                }
            ]
            
            # Generate recipes
            recipes = []
            for _ in range(3):  # Generate 3 different recipes
                response = self.llm.invoke(prompt)
                recipe = self._parse_recipe(response.content)
                if recipe:
                    # Store recipe in Supabase
                    stored_recipe = self._store_recipe(recipe, ingredients)
                    recipes.append(stored_recipe)

            logger.info(f"Generated {len(recipes)} recipes")
            return recipes

        except Exception as e:
            logger.error(f"Error generating recipes: {e}", exc_info=True)
            return []

    def _parse_recipe(self, recipe_text):
        """Parse generated recipe text into structured format"""
        try:
            # Split into lines
            lines = recipe_text.strip().split('\n')
            
            # First non-empty line is title
            title = next(line.strip() for line in lines if line.strip())
            
            # Rest is instructions
            instructions = '\n'.join(
                line.strip() 
                for line in lines[1:] 
                if line.strip()
            )

            return {
                'title': title,
                'instructions': instructions
            }

        except Exception as e:
            logger.error(f"Error parsing recipe: {e}", exc_info=True)
            return None

    def _store_recipe(self, recipe, ingredients):
        """Store recipe in Supabase database"""
        try:
            # Prepare recipe data
            recipe_data = {
                'name': recipe['title'],
                'ingredients': ingredients,
                'instructions': recipe['instructions']
            }

            # Insert into recipes table
            result = self.supabase.table('recipes').insert(recipe_data).execute()
            
            # Return stored recipe with database ID
            if result.data:
                stored_recipe = result.data[0]
                return {
                    'id': stored_recipe['id'],
                    'title': stored_recipe['name'],
                    'ingredients': stored_recipe['ingredients'],
                    'instructions': stored_recipe['instructions']
                }
            return recipe

        except Exception as e:
            logger.error(f"Error storing recipe: {e}", exc_info=True)
            return recipe 