from langchain_openai import ChatOpenAI
from crewai import Agent
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
from langchain.tools import Tool
from typing import List, Dict
import numpy as np

class VisionAgent:
    def __init__(self, openai_api_key):
        # Initialize CLIP model for ingredient detection
        self.model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
        
        # Comprehensive list of ingredients
        self.ingredient_categories = {
            "vegetables": [
                "tomato", "onion", "garlic", "potato", "carrot", "lettuce", "cucumber",
                "bell pepper", "broccoli", "spinach", "mushroom", "zucchini", "eggplant",
                "corn", "peas", "asparagus", "celery", "kale", "cabbage"
            ],
            "fruits": [
                "apple", "banana", "orange", "lemon", "lime", "strawberry", "blueberry",
                "raspberry", "grape", "pineapple", "mango", "avocado", "peach", "pear",
                "plum", "cherry", "watermelon", "kiwi"
            ],
            "proteins": [
                "chicken", "beef", "pork", "fish", "shrimp", "tofu", "eggs", "turkey",
                "lamb", "salmon", "tuna", "bacon", "sausage", "ham", "beans", "lentils",
                "chickpeas", "nuts"
            ],
            "dairy": [
                "milk", "cheese", "butter", "yogurt", "cream", "sour cream", "cream cheese",
                "mozzarella", "cheddar", "parmesan", "cottage cheese"
            ],
            "grains": [
                "rice", "pasta", "bread", "flour", "oats", "quinoa", "couscous",
                "noodles", "cereal", "tortilla", "bagel"
            ],
            "condiments": [
                "oil", "salt", "pepper", "sugar", "vinegar", "soy sauce", "ketchup",
                "mustard", "mayonnaise", "hot sauce", "honey", "maple syrup"
            ],
            "herbs_spices": [
                "basil", "oregano", "thyme", "rosemary", "cilantro", "parsley", "mint",
                "cinnamon", "cumin", "paprika", "turmeric", "ginger"
            ]
        }
        
        self.llm = ChatOpenAI(
            model="gpt-4-vision-preview",
            api_key=openai_api_key,
            max_tokens=1000,
            temperature=0.7
        )
        
    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="analyze_multiple_images",
                func=self.analyze_multiple_images,
                description="Analyzes multiple images to detect ingredients. Input should be a list of image paths."
            ),
            Tool(
                name="verify_ingredients",
                func=self.verify_ingredients,
                description="Verifies if detected ingredients make sense together. Input should be a list of ingredients."
            ),
            Tool(
                name="estimate_quantities",
                func=self.estimate_quantities,
                description="Estimates quantities of visible ingredients. Input should be a list of detected ingredients."
            ),
            Tool(
                name="categorize_ingredients",
                func=self.categorize_ingredients,
                description="Categorizes detected ingredients into groups. Input should be a list of ingredients."
            )
        ]
        
    def analyze_multiple_images(self, image_paths: List[str]) -> Dict[str, List[str]]:
        """Analyze multiple images to detect ingredients"""
        all_ingredients = set()
        results = {"detected_ingredients": [], "confidence_scores": {}}
        
        try:
            for image_path in image_paths:
                image = Image.open(image_path)
                
                # Flatten ingredient categories into a single list
                all_possible_ingredients = [
                    item for sublist in self.ingredient_categories.values() 
                    for item in sublist
                ]
                
                # Process image with CLIP
                inputs = self.processor(
                    images=image,
                    text=all_possible_ingredients,
                    return_tensors="pt",
                    padding=True
                )
                
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
                
                # Detect ingredients with confidence > 0.3
                for idx, ingredient in enumerate(all_possible_ingredients):
                    confidence = probs[0][idx].item()
                    if confidence > 0.3:
                        all_ingredients.add(ingredient)
                        results["confidence_scores"][ingredient] = max(
                            confidence,
                            results["confidence_scores"].get(ingredient, 0)
                        )
            
            results["detected_ingredients"] = list(all_ingredients)
            return results
            
        except Exception as e:
            return {"error": f"Error analyzing images: {str(e)}"}
            
    def verify_ingredients(self, ingredients: List[str]) -> Dict[str, List[str]]:
        """Verify if detected ingredients make sense together"""
        categorized = self.categorize_ingredients(ingredients)
        verified = []
        suggestions = []
        
        # Basic verification rules
        if len(categorized.get("proteins", [])) > 0 and len(categorized.get("vegetables", [])) == 0:
            suggestions.append("Consider adding some vegetables to balance the meal")
            
        if len(ingredients) < 3:
            suggestions.append("The recipe might be too simple, consider adding more ingredients")
            
        return {
            "verified_ingredients": ingredients,
            "suggestions": suggestions
        }
        
    def estimate_quantities(self, ingredients: List[str]) -> Dict[str, str]:
        """Estimate quantities of visible ingredients"""
        # This could be improved with object detection models for size estimation
        standard_portions = {
            "vegetables": "1 cup",
            "fruits": "1 piece",
            "proteins": "6 oz",
            "dairy": "1 cup",
            "grains": "1 cup",
            "condiments": "1 tablespoon",
            "herbs_spices": "1 teaspoon"
        }
        
        quantities = {}
        categorized = self.categorize_ingredients(ingredients)
        
        for category, items in categorized.items():
            for item in items:
                quantities[item] = standard_portions.get(category, "1 unit")
                
        return quantities
        
    def categorize_ingredients(self, ingredients: List[str]) -> Dict[str, List[str]]:
        """Categorize ingredients into groups"""
        categorized = {category: [] for category in self.ingredient_categories.keys()}
        
        for ingredient in ingredients:
            for category, items in self.ingredient_categories.items():
                if ingredient in items:
                    categorized[category].append(ingredient)
                    break
                    
        return {k: v for k, v in categorized.items() if v}  # Remove empty categories 

    def analyze_images(self, image_paths):
        ingredients = []
        for image_path in image_paths:
            try:
                # Load and process image
                image = Image.open(image_path)
                ingredients.extend(self._detect_ingredients(image))
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                continue
        
        return list(set(ingredients))  # Remove duplicates

    def _detect_ingredients(self, image):
        # Common ingredients to check against
        common_ingredients = [
            "tomato", "onion", "garlic", "potato", "carrot", "chicken",
            "beef", "fish", "rice", "pasta", "lettuce", "cucumber",
            "pepper", "salt", "olive oil", "butter", "cheese", "egg",
            "milk", "flour", "sugar", "lemon", "lime", "apple",
            # Add more ingredients as needed
        ]

        # Process image for CLIP
        inputs = self.processor(
            images=image,
            text=common_ingredients,
            return_tensors="pt",
            padding=True
        )

        # Get model outputs
        outputs = self.model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = torch.softmax(logits_per_image, dim=1)

        # Get ingredients with high confidence (>0.5)
        detected_ingredients = [
            ingredient for idx, ingredient in enumerate(common_ingredients)
            if probs[0][idx].item() > 0.5
        ]

        # Use GPT-4 Vision for additional ingredient detection
        vision_response = self.llm.invoke(
            [
                {
                    "type": "text",
                    "text": "What ingredients do you see in this image? List only the ingredients, separated by commas."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{self._image_to_base64(image)}"
                    }
                }
            ]
        )

        # Combine CLIP and GPT-4 Vision results
        gpt_ingredients = [
            ingredient.strip().lower()
            for ingredient in vision_response.content.split(',')
        ]
        
        return list(set(detected_ingredients + gpt_ingredients))

    def _image_to_base64(self, image):
        import base64
        from io import BytesIO
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode() 