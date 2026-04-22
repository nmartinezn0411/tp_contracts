import os 
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    """Configuration settings for the application."""

    def __init__(self):
        # Logging and debugging
        self.TESTER = os.getenv("TESTER", "false").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

        # Gemini API keys
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.GOOGLE_API_MODEL_NAME = os.getenv("GOOGLE_API_MODEL_NAME")

        # Data location
        self.data_folder = BASE_DIR / "data"

        # CSV filenames
        self.timesheet_location = "timesheet.csv"
        self.billing_location = "billing.csv"
        self.contracts_location = "contracts.csv"

        # Full paths (FIXED)
        self.timesheet = self.data_folder / self.timesheet_location
        self.billing = self.data_folder / self.billing_location
        self.contracts = self.data_folder / self.contracts_location

# Global settings instance
settings = Settings()