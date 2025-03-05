import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class RecipeAgent:
    def __init__(self, openai_api_key):
        # Load Recipe1M model and tokenizer
        self.model_name = "facebook/recipe1m"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        self.model.eval()  # Set to evaluation mode

    def suggest_recipes(self, ingredients):
        try:
            # Format ingredients for input
            ingredients_text = ", ".join(ingredients)
            input_text = f"Ingredients: {ingredients_text}\nRecipe:"
            
            # Tokenize input
            inputs = self.tokenizer(input_text, return_tensors="pt", padding=True)
            
            # Generate recipe
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    max_length=512,
                    num_return_sequences=3,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.95
                )

            # Process and format recipes
            recipes = []
            for idx, output in enumerate(outputs):
                recipe_text = self.tokenizer.decode(output, skip_special_tokens=True)
                
                # Parse recipe text into structured format
                recipe = self._parse_recipe(recipe_text, idx + 1)
                if recipe:
                    recipes.append(recipe)

            return recipes

        except Exception as e:
            print(f"Error generating recipes: {e}")
            return []

    def _parse_recipe(self, recipe_text, recipe_id):
        """Parse generated recipe text into structured format"""
        try:
            # Split into sections
            sections = recipe_text.split('\n\n')
            
            # Extract title (first line)
            title = sections[0].strip()
            if 'Ingredients:' in title:
                title = title.split('Ingredients:')[0].strip()

            # Extract ingredients
            ingredients = []
            instructions = []
            
            for section in sections[1:]:
                if 'Ingredients:' in section:
                    # Get ingredients list
                    ingredients_text = section.split('Ingredients:')[1]
                    ingredients = [
                        ing.strip() 
                        for ing in ingredients_text.split('\n') 
                        if ing.strip()
                    ]
                elif 'Instructions:' in section:
                    # Get cooking instructions
                    instructions_text = section.split('Instructions:')[1]
                    instructions = [
                        inst.strip() 
                        for inst in instructions_text.split('\n') 
                        if inst.strip()
                    ]

            return {
                'id': recipe_id,
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions
            }

        except Exception as e:
            print(f"Error parsing recipe: {e}")
            return None 