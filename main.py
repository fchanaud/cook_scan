from fastapi import FastAPI, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from agents.vision_agent import VisionAgent
from agents.recipe_agent import RecipeAgent
from config import Config

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://<your-render-app>.onrender.com"],  # Update with your domain
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
    try:
        # Save uploaded files temporarily
        temp_paths = []
        for file in files:
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            temp_paths.append(temp_path)
            
        # Process images
        vision_agent = VisionAgent(Config.OPENAI_API_KEY)
        recipe_agent = RecipeAgent(Config.OPENAI_API_KEY)
        
        # Get ingredients and recipes
        ingredients = vision_agent.analyze_images(temp_paths)
        recipes = recipe_agent.suggest_recipes(ingredients)
        
        return recipes
        
    except Exception as e:
        return {"error": str(e)}, 500
        
    finally:
        # Clean up temporary files
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 