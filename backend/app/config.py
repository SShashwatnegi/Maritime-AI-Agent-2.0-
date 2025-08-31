import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Gemini
    USE_GEMINI = os.getenv("USE_GEMINI", "true").lower() == "true"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # OpenWeatherMap
    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

    def validate(self):
        """Validate configuration settings."""
        if self.USE_GEMINI and not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY must be set when USE_GEMINI is True")
        if not self.OPENWEATHERMAP_API_KEY:
            raise ValueError("OPENWEATHERMAP_API_KEY must be set")

settings = Settings()
settings.validate()