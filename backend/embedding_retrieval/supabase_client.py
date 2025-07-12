"""Supabase client module for database operations.

This module provides functions to interact with the Supabase database,
specifically for fetching media clip metadata.
"""

import logging
from typing import Any

from supabase import Client, create_client

from config import SUPABASE_KEY, SUPABASE_URL

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """Create and return a Supabase client instance.
    
    Returns:
        Client: Configured Supabase client instance.
        
    Raises:
        ValueError: If Supabase credentials are not properly configured.
    """
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as error:
        logger.error(f"Failed to create Supabase client: {error}")
        raise ValueError("Unable to initialize Supabase client") from error


def fetch_media_clips() -> list[dict[str, Any]]:
    """Fetch all media clips from the database.
    
    Returns:
        list[dict[str, Any]]: List of media clip records from the database.
        
    Raises:
        RuntimeError: If database query fails.
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table('media_clips').select('*').execute()
        
        if response.data is None:
            logger.warning("No media clips found in database")
            return []
            
        logger.info(f"Successfully fetched {len(response.data)} media clips")
        return response.data
        
    except Exception as error:
        logger.error(f"Failed to fetch media clips: {error}")
        raise RuntimeError("Database query failed") from error


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(level=logging.INFO)
    
    try:
        clips = fetch_media_clips()
        for clip in clips:
            print(f"Clip: {clip.get('title', 'Unknown')} - {clip.get('id', 'No ID')}")
    except Exception as error:
        print(f"Error: {error}") 