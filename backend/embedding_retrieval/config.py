"""Configuration module for clip content analyzer.

This module handles environment variable loading and provides centralized
configuration constants for the application.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase configuration
SUPABASE_URL: Optional[str] = os.getenv('SUPABASE_URL')
SUPABASE_KEY: Optional[str] = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing required environment variables: SUPABASE_URL and SUPABASE_KEY. "
        "Please check your .env file or environment configuration."
    )

# Processing configuration
MAX_FILE_SIZE_MB: int = int(os.getenv('MAX_FILE_SIZE_MB', '100'))
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
TEMP_DIR: Path = Path(os.getenv('TEMP_DIR', '/tmp'))
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

# Frame extraction constants
DEFAULT_FRAME_PERCENTAGES: list[float] = [0.25, 0.5, 0.75]
DOWNLOAD_CHUNK_SIZE: int = 8192

# File extensions
SUPPORTED_VIDEO_EXTENSIONS: set[str] = {'.mp4', '.mov', '.avi', '.mkv', '.webm'} 