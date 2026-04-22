import os 
from dotenv import load_dotenv
load_dotenv()

class Settings:
    """Configuration settings for the application."""

    def __init__(self):
        # Logging and debuggin
        self.TESTER = os.getenv("TESTER", "false").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        # Gemini API keys
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.GOOGLE_API_MODEL_NAME = os.getenv("GOOGLE_API_MODEL_NAME")
        
# Global settings instance
settings = Settings()