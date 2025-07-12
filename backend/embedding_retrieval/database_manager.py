"""Database manager for Supabase operations.

This module provides a DatabaseManager class that encapsulates all database
operations with proper connection management and error handling.
"""

import logging
from typing import Any, Optional

from supabase import Client, create_client

from config import SUPABASE_KEY, SUPABASE_URL

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for media clips."""
    
    def __init__(self) -> None:
        """Initialize the database manager with Supabase client."""
        self._client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Supabase client with error handling."""
        try:
            self._client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Database client initialized successfully")
        except Exception as error:
            logger.error(f"Failed to initialize database client: {error}")
            raise ValueError("Unable to initialize database client") from error
    
    @property
    def client(self) -> Client:
        """Get the Supabase client, reinitializing if necessary."""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def fetch_all_clips(self) -> list[dict[str, Any]]:
        """Fetch all media clips from the database.
        
        Returns:
            list[dict[str, Any]]: List of media clip records.
            
        Raises:
            RuntimeError: If database query fails.
        """
        try:
            response = self.client.table('media_clips').select('*').execute()
            
            if response.data is None:
                logger.warning("No media clips found in database")
                return []
            
            logger.info(f"Successfully fetched {len(response.data)} media clips")
            return response.data
            
        except Exception as error:
            logger.error(f"Failed to fetch media clips: {error}")
            raise RuntimeError("Database query failed") from error
    
    def get_clip_by_id(self, clip_id: str) -> Optional[dict[str, Any]]:
        """Fetch a specific clip by ID.
        
        Args:
            clip_id: The ID of the clip to fetch.
            
        Returns:
            Optional[dict[str, Any]]: Clip data if found, None otherwise.
        """
        try:
            response = self.client.table('media_clips').select('*').eq('id', clip_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Successfully fetched clip {clip_id}")
                return response.data[0]
            
            logger.warning(f"Clip {clip_id} not found")
            return None
            
        except Exception as error:
            logger.error(f"Failed to fetch clip {clip_id}: {error}")
            raise RuntimeError(f"Failed to fetch clip {clip_id}") from error
    
    def get_connection_status(self) -> bool:
        """Check if database connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise.
        """
        try:
            # Simple health check query
            response = self.client.table('media_clips').select('id').limit(1).execute()
            return True
        except Exception as error:
            logger.error(f"Database connection unhealthy: {error}")
            return False 