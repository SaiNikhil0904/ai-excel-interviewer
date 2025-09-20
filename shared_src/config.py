"""
shared_src/config.py

Centralized configuration for AI Excel Interviewer.
Loads environment variables from a .env file and provides a typed Pydantic Settings object.
"""
import logging
import json
from pathlib import Path
from typing import List, Literal
from dotenv import load_dotenv
from pydantic import Field
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings

# Load .env if exists
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    print(f"INFO: Loaded environment variables from {ENV_PATH}")
else:
    print(f"WARNING: .env file not found at {ENV_PATH}. Using system environment variables.")

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    APP_ENVIRONMENT: Literal["local"] = Field("local", alias="APP_ENVIRONMENT")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO", alias="LOG_LEVEL")
    GOOGLE_API_KEY: str = Field(..., alias="GOOGLE_API_KEY")

    # --- Database (PostgreSQL) ---
    DB_USER: str = Field(..., alias="DB_USER")
    DB_PASSWORD: str = Field(..., alias="DB_PASSWORD")
    DB_NAME: str = Field(..., alias="DB_NAME")
    DB_HOST: str = Field("localhost", alias="DB_HOST")
    DB_PORT: int = Field(5432, alias="DB_PORT")

    # --- AI Excel Interviewer Service ---
    AI_EXCEL_INTERVIEWER_SERVICE_NAME: str = Field("ai_excel_interviewer", alias="AI_EXCEL_INTERVIEWER_SERVICE_NAME")
    AI_EXCEL_INTERVIEWER_INTERNAL_PORT: int = Field(8100, alias="AI_EXCEL_INTERVIEWER_INTERNAL_PORT")
    AI_EXCEL_INTERVIEWER_MCP_SERVICE_NAME: str = Field("ai_excel_interviewer_mcp", alias="AI_EXCEL_INTERVIEWER_MCP_SERVICE_NAME")
    AI_EXCEL_INTERVIEWER_MCP_INTERNAL_PORT: int = Field(9100, alias="AI_EXCEL_INTERVIEWER_MCP_INTERNAL_PORT")
    AI_EXCEL_INTERVIEWER_A2A_SERVICE_NAME: str = Field("ai_excel_interviewer_a2a", alias="AI_EXCEL_INTERVIEWER_A2A_SERVICE_NAME")
    AI_EXCEL_INTERVIEWER_A2A_INTERNAL_PORT: int = Field(10100, alias="AI_EXCEL_INTERVIEWER_A2A_INTERNAL_PORT")

    ALLOWED_ORIGINS_STR: str = Field('["http://localhost:3000"]', alias="ALLOWED_ORIGINS_STR")

    @property
    def allowed_origins(self) -> List[str]:
        try:
            return json.loads(self.ALLOWED_ORIGINS_STR)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse ALLOWED_ORIGINS_STR: {self.ALLOWED_ORIGINS_STR}")
            return []

    @property
    def database_url_async(self) -> str:
        """Async DB URL (asyncpg)"""
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        ))

    @property
    def database_url_sync(self) -> str:
        """Sync DB URL (psycopg2)"""
        return str(PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        ))

# Instantiate settings
try:
    settings = Settings()
    logging.basicConfig(level=settings.LOG_LEVEL.upper(), format="%(asctime)s - %(name)s [%(levelname)s] - %(message)s", force=True)
    logger.info("AI Excel Interviewer configuration loaded successfully.")
except Exception as e:
    logging.basicConfig(level="ERROR", format="%(asctime)s -CRITICAL- %(message)s")
    logger.critical(f"FATAL: Could not load application settings: {e}", exc_info=True)
    exit(1)