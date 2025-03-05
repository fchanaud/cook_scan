from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from database.database import SessionLocal, engine
from database import models
from database.models import Base
import schemas
from main import CookScanApp
from config import Config

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
    try:
        # Save uploaded files temporarily
        temp_paths = []
        for file in files:
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            temp_paths.append(temp_path)
            
        # Initialize CookScan app and process images
        cook_scan_app = CookScanApp(Config.OPENAI_API_KEY)
        recipes = cook_scan_app.run(temp_paths)
        
        return recipes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Clean up temporary files
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)

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