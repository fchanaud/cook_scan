from main import RecipeGeneratorApp
from config import Config

def test_app():
    app = RecipeGeneratorApp(Config.OPENAI_API_KEY)
    # Use a small test image
    result = app.run("test_image.jpg")
    print(result)

if __name__ == "__main__":
    test_app() 