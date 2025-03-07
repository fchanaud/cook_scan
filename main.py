from fastapi import FastAPI, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from agents.vision_agent import VisionAgent
from agents.recipe_agent import RecipeAgent
from config import Config
from database.database import get_supabase
import logging

app = FastAPI()
supabase = get_supabase()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cook-scan.onrender.com"],  # Update with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API endpoints
@app.post("/analyze-images/")
async def analyze_images(files: List[UploadFile] = File(...)):
    temp_paths = []
    try:
        # Save uploaded files temporarily
        logger.info(f"Received {len(files)} files for analysis")
        
        for file in files:
            temp_path = f"temp_{file.filename}"
            logger.info(f"Processing file: {file.filename}")
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            temp_paths.append(temp_path)
            
        # Process images
        vision_agent = VisionAgent(Config.OPENAI_API_KEY)
        recipe_agent = RecipeAgent(Config.OPENAI_API_KEY)
        
        # Get ingredients and recipes
        logger.info("Analyzing images with vision agent...")
        ingredients = vision_agent.analyze_images(temp_paths)
        if not ingredients:
            logger.warning("No ingredients detected")
            return {"error": "No ingredients detected in the images"}, 400
            
        logger.info(f"Detected ingredients: {ingredients}")
        
        logger.info("Generating recipes...")
        recipes = recipe_agent.suggest_recipes(ingredients)
        if not recipes:
            logger.warning("No recipes generated")
            return {"error": "Could not generate recipes from the detected ingredients"}, 400
            
        logger.info(f"Generated recipes: {recipes}")
        return {"success": True, "recipes": recipes, "ingredients": ingredients}
        
    except Exception as e:
        logger.error(f"Error in analyze_images: {str(e)}", exc_info=True)
        return {"error": str(e)}, 500
        
    finally:
        # Clean up temporary files
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                logger.info(f"Cleaning up temporary file: {temp_path}")
                os.remove(temp_path)

@app.get("/test-supabase")
async def test_supabase():
    try:
        # Test Supabase connection
        response = supabase.table("recipes").select("*").limit(1).execute()
        return {"message": "Connected to Supabase successfully", "data": response.data}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Starting CookScan API server...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 