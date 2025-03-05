from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from database.database import SessionLocal, engine
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
    allow_origins=["*"],  # In production, replace with specific origins
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

@app.post("/analyze-images/", response_model=List[schemas.Recipe])
async def analyze_images(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    # Save uploaded files temporarily
    temp_paths = []
    try:
        for file in files:
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())
            temp_paths.append(temp_path)
        
        # Initialize CookScan app
        cook_scan_app = CookScanApp(Config.OPENAI_API_KEY)
        results = cook_scan_app.run(temp_paths)
        
        # Save results to database
        db_recipes = []
        for recipe in results:
            db_recipe = models.Recipe(
                title=recipe['title'],
                ingredients=recipe['ingredients'],
                instructions=recipe['instructions'],
                match_percentage=recipe['match_percentage']
            )
            db.add(db_recipe)
            db_recipes.append(db_recipe)
        
        db.commit()
        return db_recipes
        
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