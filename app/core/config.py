from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent.parent.parent   # This resolves the base_dir to the root folder.

ENV_FILE_PATH=BASE_DIR / ".env" # This allows us to know the env file path.

