import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Vision model settings
    CONFIDENCE_THRESHOLD = 0.5
    
    # Recipe matching settings
    MIN_MATCH_PERCENTAGE = 0.8
    MAX_RECIPES = 10
    
    # Agent settings
    TEMPERATURE = 0.7  # Controls creativity vs determinism
    MAX_RETRIES = 3    # Number of times an agent will retry a failed task
    TIMEOUT = 300      # Maximum time (in seconds) for an agent to complete a task
    
    # Agent behavior settings
    VERBOSE = True     # Enable detailed logging of agent actions
    ALLOW_DELEGATION = True  # Allow agents to delegate subtasks
    MEMORY_WINDOW = 10  # Number of previous interactions to maintain in context 