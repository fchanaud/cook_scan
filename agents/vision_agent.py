from transformers import AutoProcessor, LlamaForCausalLM
from PIL import Image
import torch
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class VisionAgent:
    def __init__(self, openai_api_key):  # We'll keep the param for compatibility
        logger.info("Initializing VisionAgent with Llama Vision model...")
        self.model_name = "meta-llama/Llama-3.2-11B-Vision-Instruct"
        self.hf_token = os.getenv("HUGGIN_FACE_TOKEN")
        
        if not self.hf_token:
            raise ValueError("HUGGIN_FACE_TOKEN not found in environment variables")
            
        # Initialize model and processor
        self.processor = AutoProcessor.from_pretrained(
            self.model_name,
            token=self.hf_token
        )
        self.model = LlamaForCausalLM.from_pretrained(
            self.model_name,
            token=self.hf_token,
            device_map="auto",
            torch_dtype=torch.float16
        )
        self.model.eval()

    def analyze_images(self, image_paths):
        logger.info(f"Analyzing images: {image_paths}")
        """Analyze multiple images to detect ingredients"""
        all_ingredients = set()
        
        for image_path in image_paths:
            try:
                # Load and process image
                image = Image.open(image_path)
                ingredients = self._detect_ingredients(image)
                all_ingredients.update(ingredients)
                logger.info(f"Detected ingredients from {image_path}: {ingredients}")
            except Exception as e:
                logger.error(f"Error processing image {image_path}: {e}", exc_info=True)
                continue
        
        result = list(all_ingredients)
        logger.info(f"Final ingredients list: {result}")
        return result

    def _detect_ingredients(self, image):
        """Detect ingredients in a single image using Llama Vision"""
        try:
            # Prepare prompt
            prompt = """Analyze this food image and list the main ingredients you can see.
            Return ONLY a comma-separated list of ingredients.
            Example format: beef, potatoes, carrots
            Be specific but concise.
            For this dish, list the ingredients you can clearly identify:"""

            # Process image and text
            inputs = self.processor(
                text=prompt,
                images=image,
                return_tensors="pt"
            ).to(self.model.device)

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )

            # Decode response
            response = self.processor.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"Raw model response: {response}")

            # Extract ingredients list from response
            # Remove the prompt from response and clean up
            response_text = response.split(prompt)[-1].strip()
            
            # Process ingredients
            ingredients = [
                ingredient.strip().lower()
                for ingredient in response_text.split(',')
                if ingredient.strip()
            ]
            
            logger.info(f"Processed ingredients: {ingredients}")
            return ingredients

        except Exception as e:
            logger.error(f"Error in ingredient detection: {str(e)}", exc_info=True)
            return [] 