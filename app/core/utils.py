from dotenv import load_dotenv, find_dotenv
import logging
import os
import zipfile
from pathlib import Path

def extract_zipfile(zip_path: str, extract_path: str):
    """
    Extract contents from a zipfile and store them in a local directory.

    Args:
    zip_path (str): Path to the zip file
    extract_path (str): Path to the directory where contents will be extracted

    Returns:
    None
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print(f"Extracted contents from '{os.path.basename(zip_path)}' to '{extract_path}' directory.")

def check_path_type(path: str) -> str:
    """
    Check if the given path is a zip file or a directory.

    Args:
    path (str): Path to check

    Returns:
    str: 'zip' if it's a zip file, 'directory' if it's a directory, 'other' otherwise
    """
    path_obj = Path(path)
    
    if path_obj.is_file() and path_obj.suffix.lower() == '.zip':
        return 'zip'
    elif path_obj.is_dir():
        return 'directory'
    else:
        return 'other'

def load_environment_variables(env_file: str | None = None) -> None:
    """
    Load environment variables from a .env file safely.

    This function loads environment variables from a `.env` file, ensuring
    that critical configurations are set before the application starts.

    Args:
        env_file (str | None): Path to a specific `.env` file. If None,
                               it searches for a `.env` file automatically.

    Behavior:
    - If `env_file` is provided, it loads the specified file.
    - If `env_file` is not provided, it attempts to locate a `.env` file in the project directory.
    - Logs a warning if no `.env` file is found.

    Returns:
        None
    """
    env_path = env_file or find_dotenv()

    if env_path:
        load_dotenv(env_path, override=True)
        logging.info(f".env file loaded from {env_path}")
    else:
        logging.warning("No .env file found. Ensure environment variables are set.")