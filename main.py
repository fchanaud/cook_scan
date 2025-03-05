from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from agents.vision_agent import VisionAgent
from agents.recipe_agent import RecipeAgent
from config import Config

class CookScanApp:
    def __init__(self, openai_api_key):
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,
            api_key=openai_api_key
        )
        
    def create_agents(self):
        vision_agent_tools = VisionAgent().get_tools()
        recipe_agent_tools = RecipeAgent(Config.SPOONACULAR_API_KEY).get_tools()
        
        # Create Vision Agent for ingredient detection
        self.vision_agent = Agent(
            role='Computer Vision Expert',
            goal='Accurately identify and list ingredients from images',
            backstory='Expert in computer vision with specialized knowledge in food and ingredient recognition',
            allow_delegation=True,
            llm=self.llm,
            tools=vision_agent_tools
        )

        # Create Recipe Agent for matching and suggestions
        self.recipe_agent = Agent(
            role='Recipe Expert',
            goal='Match available ingredients with suitable recipes and provide cooking suggestions',
            backstory='Experienced chef with deep knowledge of recipes and ingredient substitutions',
            allow_delegation=True,
            llm=self.llm,
            tools=recipe_agent_tools
        )

    def create_tasks(self, image_path):
        # Task 1: Analyze image and detect ingredients
        image_analysis = Task(
            description="""
            1. Analyze the provided image and identify all visible ingredients
            2. Verify the detected ingredients make sense together
            3. Estimate quantities where possible
            """,
            agent=self.vision_agent,
            expected_output='List of detected ingredients with quantities',
            context={'image_path': image_path}
        )

        # Task 2: Match ingredients with recipes
        recipe_matching = Task(
            description="""
            1. Search for recipes using the detected ingredients
            2. Rank recipes by simplicity and ingredient match
            3. Suggest substitutions for any missing key ingredients
            4. Analyze nutritional content of top recipes
            """,
            agent=self.recipe_agent,
            expected_output='Ranked list of recipe suggestions with substitutions and nutrition info',
            context={'min_match_percentage': 0.8}
        )

        return [image_analysis, recipe_matching]

    def run(self, image_path):
        self.create_agents()
        tasks = self.create_tasks(image_path)
        
        crew = Crew(
            agents=[self.vision_agent, self.recipe_agent],
            tasks=tasks,
            process=Process.sequential
        )

        result = crew.kickoff()
        return result 