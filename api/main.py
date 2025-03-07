from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import datetime
import json
import traceback

from database.database import SessionLocal, engine
from database import models
from database.models import Base
import schemas
from main import CookScanApp
from config import Config
from agents.vision_agent import VisionAgent

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CookScan API",
    description="AI-powered ingredient detection and recipe suggestion API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/analyze-images/")
async def analyze_images(files: List[UploadFile] = File(...)):
    print("\n=== Starting Image Analysis ===")
    print(f"🕒 {datetime.datetime.now()}")
    temp_paths = []
    try:
        # Save uploaded files temporarily
        print(f"📁 Number of files received: {len(files)}")
        for file in files:
            print(f"📝 Processing file: {file.filename}")
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                print(f"📦 File size: {len(content)} bytes")
                buffer.write(content)
            temp_paths.append(temp_path)
            print(f"💾 Saved to temporary path: {temp_path}")
        
        # Analyze image
        print("\n🔍 Starting Vision Analysis...")
        vision_agent = VisionAgent(Config.OPENAI_API_KEY)
        ingredients = await vision_agent.detect_ingredients(temp_paths)
        print("\n🥕 Detected ingredients:")
        if ingredients:
            for i, ingredient in enumerate(ingredients, 1):
                print(f"  {i}. {ingredient}")
            
            print("\n👨‍🍳 Generating recipe...")
            recipe_agent = CookScanApp()
            recipe = await recipe_agent.generate_recipe(ingredients)
            print("\n📖 Generated recipe:")
            print(f"{recipe}")
        else:
            print("❌ No ingredients detected!")
            recipe = None
        
        # Clean up temporary files
        print("\n🧹 Cleaning up temporary files...")
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        response_data = {
            "success": True,
            "ingredients_count": len(ingredients) if ingredients else 0,
            "ingredients": ingredients if ingredients else [],
            "recipe": recipe,
            "message": "No ingredients detected" if not ingredients else "Ingredients detected successfully"
        }
        print(f"\n✅ Analysis complete. Response data:")
        print(json.dumps(response_data, indent=2))
        return response_data
        
    except Exception as e:
        print(f"\n❌ Error in analyze_images: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        # Clean up temporary files in case of error
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recipes/", response_model=List[schemas.Recipe])
def get_recipes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    recipes = db.query(models.Recipe).offset(skip).limit(limit).all()
    return recipes

@app.post("/recipes/favorite/{recipe_id}")
def favorite_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if recipe:
        recipe.is_favorite = True
        db.commit()
        return {"message": "Recipe marked as favorite"}
    return {"error": "Recipe not found"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 