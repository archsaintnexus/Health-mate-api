from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent # Goes up to the project_root
ENV_FILE_PATH = BASE_DIR / ".env"