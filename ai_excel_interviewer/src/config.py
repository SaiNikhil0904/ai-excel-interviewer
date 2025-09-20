"""
Centralized configuration for the AI Excel Interviewer.

This module loads all environment variables from the .env file using Pydantic,
configures the global google.generativeai client, and provides a single,
typed 'settings' object for the entire application.
"""
import logging
import os
import google.generativeai as genai
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Loads and validates all environment variables for the application."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

    # --- Database (PostgreSQL) ---
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str

    GOOGLE_API_KEY: str

    # --- Service Ports ---
    BACKEND_PORT: int = 8100
    MCP_PORT: int = 9100
    A2A_PORT: int = 10100
    
    @property
    def database_url_sync(self) -> str:
        """Returns the SYNC database URL needed by DatabaseSessionService."""
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# --- Global Initialization ---
logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO", format='%(asctime)s - [CONFIG] - %(levelname)s - %(message)s')

try:
    settings = Settings()
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    logger.info("Successfully configured Google AI (Gemini) API key globally.")
    # --- END OF FIX ---
    
except Exception as e:
    logger.critical(f"FATAL: Could not load application settings or configure APIs: {e}", exc_info=True)
    exit(1)