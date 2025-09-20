"""
ai_excel_interviewer/src/utils/prompts_loader.py

Utility for loading YAML-based prompt instructions from the prompts directory.
"""

import yaml
import logging
from pathlib import Path
from functools import lru_cache
from shared_src.config import PROJECT_ROOT

logger = logging.getLogger(__name__)
PROMPTS_DIR = PROJECT_ROOT / "ai_excel_interviewer" / "src" / "prompts"

@lru_cache(maxsize=1)
def load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)["instruction"]
    except Exception as e:
        logger.critical(f"Failed to load prompt '{filename}': {e}", exc_info=True)
        raise