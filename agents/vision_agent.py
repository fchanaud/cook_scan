from langchain_openai import ChatOpenAI
from PIL import Image
import base64
from io import BytesIO

class VisionAgent:
    def __init__(self, openai_api_key):
        self.llm = ChatOpenAI(
            model="gpt-4-vision-preview",
            api_key=openai_api_key,
            max_tokens=1000,
            temperature=0.7
        )

    def analyze_images(self, image_paths):
        """Analyze multiple images to detect ingredients"""
        all_ingredients = set()
        
        for image_path in image_paths:
            try:
                # Load and process image
                image = Image.open(image_path)
                ingredients = self._detect_ingredients(image)
                all_ingredients.update(ingredients)
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                continue
        
        return list(all_ingredients)

    def _detect_ingredients(self, image):
        """Detect ingredients in a single image using GPT-4 Vision"""
        try:
            # Convert image for API
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode()

            # Create prompt for GPT-4 Vision
            response = self.llm.invoke(
                [
                    {
                        "type": "text",
                        "text": """List all food ingredients you can identify in this image. 
                        Only list the ingredients, separated by commas. 
                        Be specific but concise. 
                        If you're not sure about an ingredient, don't include it."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            )

            # Process response
            ingredients = [
                ingredient.strip().lower()
                for ingredient in response.content.split(',')
            ]
            
            return ingredients

        except Exception as e:
            print(f"Error in ingredient detection: {e}")
            return [] 