"""Main video processor class for coordinating the complete workflow.

This module provides the VideoProcessor class that orchestrates the entire
video processing pipeline with proper dependency injection and state management.
"""

import logging
from pathlib import Path
from typing import Optional

from config import TEMP_DIR
from database_manager import DatabaseManager
from frame_extractor_class import FrameExtractor
from video_downloader import VideoDownloader

logger = logging.getLogger(__name__)


class ProcessingResult:
    """Represents the result of processing a single video clip."""
    
    def __init__(self, clip_id: str, clip_title: str, success: bool = False):
        """Initialize processing result.
        
        Args:
            clip_id: ID of the processed clip.
            clip_title: Title of the processed clip.
            success: Whether processing was successful.
        """
        self.clip_id = clip_id
        self.clip_title = clip_title
        self.success = success
        self.frame_paths: list[str] = []
        self.error_message: Optional[str] = None
        self.processing_time: Optional[float] = None
        self.frames_extracted: int = 0


class VideoProcessor:
    """Main orchestrator for video processing workflow."""
    
    def __init__(
        self,
        temp_dir: Optional[Path] = None,
        database_manager: Optional[DatabaseManager] = None,
        video_downloader: Optional[VideoDownloader] = None,
        frame_extractor: Optional[FrameExtractor] = None
    ) -> None:
        """Initialize the video processor with dependency injection.
        
        Args:
            temp_dir: Directory for temporary files. Defaults to config value.
            database_manager: Database manager instance. Creates new if None.
            video_downloader: Video downloader instance. Creates new if None.
            frame_extractor: Frame extractor instance. Creates new if None.
        """
        self.temp_dir = temp_dir or TEMP_DIR
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components with dependency injection
        self.database_manager = database_manager or DatabaseManager()
        self.video_downloader = video_downloader or VideoDownloader()
        self.frame_extractor = frame_extractor or FrameExtractor()
        
        # Processing statistics
        self.total_processed = 0
        self.successful_processed = 0
        self.failed_processed = 0
        
        logger.info(f"VideoProcessor initialized with temp_dir: {self.temp_dir}")
    
    def _create_temp_path(self, clip_id: str, extension: str = '.mov') -> Path:
        """Create a temporary file path for a clip.
        
        Args:
            clip_id: ID of the clip.
            extension: File extension to use.
        
        Returns:
            Path: Temporary file path.
        """
        return self.temp_dir / f"{clip_id}{extension}"
    
    def _progress_callback(self, downloaded: int, total: Optional[int] = None) -> None:
        """Progress callback for download operations.
        
        Args:
            downloaded: Bytes downloaded so far.
            total: Total bytes to download (if known).
        """
        if total:
            percentage = (downloaded / total) * 100
            logger.info(f"Download progress: {downloaded:,}/{total:,} bytes ({percentage:.1f}%)")
        else:
            logger.info(f"Download progress: {downloaded:,} bytes")
    
    def _frame_progress_callback(self, current: int, total: int, percentage: float) -> None:
        """Progress callback for frame extraction operations.
        
        Args:
            current: Current frame number.
            total: Total frames to extract.
            percentage: Time percentage of current frame.
        """
        logger.info(f"Frame extraction progress: {current}/{total} frames ({percentage*100:.1f}%)")
    
    def process_single_clip(self, clip: dict) -> ProcessingResult:
        """Process a single video clip.
        
        Args:
            clip: Dictionary containing clip metadata from database.
        
        Returns:
            ProcessingResult: Result of processing the clip.
        """
        import time
        
        clip_id = clip.get('id', 'unknown')
        clip_title = clip.get('title', 'Unknown')
        video_url = clip.get('clip_path')
        
        result = ProcessingResult(clip_id, clip_title)
        start_time = time.time()
        
        if not video_url:
            result.error_message = "No clip_path found in clip data"
            logger.error(f"No clip_path found for clip {clip_id}")
            return result
        
        temp_file = self._create_temp_path(clip_id)
        
        try:
            logger.info(f"Processing clip: {clip_title} (ID: {clip_id})")
            
            # Step 1: Download video
            logger.info("Step 1: Downloading video...")
            download_success = self.video_downloader.download_video(
                video_url, 
                temp_file,
                progress_callback=self._progress_callback
            )
            
            if not download_success:
                result.error_message = "Video download failed"
                return result
            
            # Step 2: Extract frames
            logger.info("Step 2: Extracting frames...")
            frames = self.frame_extractor.extract_frames_at_percentages(
                temp_file,
                progress_callback=self._frame_progress_callback
            )
            
            # Step 3: Save frames
            logger.info("Step 3: Saving frames...")
            frame_paths = []
            for i, image in enumerate(frames, 1):
                frame_path = f"{clip_id}_frame_{i}.jpg"
                image.save(frame_path)
                frame_paths.append(frame_path)
                logger.debug(f"Saved frame {i} to {frame_path}")
            
            # Update result
            result.success = True
            result.frame_paths = frame_paths
            result.frames_extracted = len(frames)
            result.processing_time = time.time() - start_time
            
            logger.info(
                f"Successfully processed {clip_title}: {len(frames)} frames extracted "
                f"in {result.processing_time:.2f}s"
            )
            
        except Exception as error:
            result.error_message = str(error)
            result.processing_time = time.time() - start_time
            logger.error(f"Failed to process clip {clip_title}: {error}")
            
        finally:
            # Clean up temporary file
            if temp_file.exists():
                try:
                    temp_file.unlink()
                    logger.debug(f"Cleaned up temporary file: {temp_file}")
                except Exception as error:
                    logger.warning(f"Failed to clean up {temp_file}: {error}")
        
        return result
    
    def process_all_clips(self) -> dict[str, ProcessingResult]:
        """Process all clips from the database.
        
        Returns:
            dict[str, ProcessingResult]: Dictionary mapping clip IDs to processing results.
        """
        logger.info("Starting to process all clips")
        
        try:
            # Fetch clips from database
            clips = self.database_manager.fetch_all_clips()
            if not clips:
                logger.warning("No clips found in database")
                return {}
            
            logger.info(f"Found {len(clips)} clips to process")
            
            results = {}
            self.total_processed = 0
            self.successful_processed = 0
            self.failed_processed = 0
            
            # Process each clip
            for i, clip in enumerate(clips, 1):
                clip_id = clip.get('id', f'unknown_{i}')
                logger.info(f"Processing clip {i}/{len(clips)}: {clip_id}")
                
                result = self.process_single_clip(clip)
                results[clip_id] = result
                
                # Update statistics
                self.total_processed += 1
                if result.success:
                    self.successful_processed += 1
                else:
                    self.failed_processed += 1
                
                # Log progress
                success_rate = (self.successful_processed / self.total_processed) * 100
                logger.info(
                    f"Progress: {self.total_processed}/{len(clips)} clips processed "
                    f"({success_rate:.1f}% success rate)"
                )
            
            logger.info(
                f"Processing complete: {self.successful_processed}/{self.total_processed} "
                f"clips processed successfully ({success_rate:.1f}% success rate)"
            )
            
            return results
            
        except Exception as error:
            logger.error(f"Failed to process clips: {error}")
            raise
    
    def process_clip_by_id(self, clip_id: str) -> Optional[ProcessingResult]:
        """Process a specific clip by ID.
        
        Args:
            clip_id: ID of the clip to process.
        
        Returns:
            Optional[ProcessingResult]: Processing result if clip found, None otherwise.
        """
        logger.info(f"Processing single clip: {clip_id}")
        
        try:
            clip = self.database_manager.get_clip_by_id(clip_id)
            if not clip:
                logger.warning(f"Clip {clip_id} not found in database")
                return None
            
            return self.process_single_clip(clip)
            
        except Exception as error:
            logger.error(f"Failed to process clip {clip_id}: {error}")
            raise
    
    def get_processing_statistics(self) -> dict[str, int]:
        """Get processing statistics.
        
        Returns:
            dict[str, int]: Dictionary containing processing statistics.
        """
        return {
            'total_processed': self.total_processed,
            'successful_processed': self.successful_processed,
            'failed_processed': self.failed_processed,
            'success_rate_percent': round(
                (self.successful_processed / self.total_processed * 100) 
                if self.total_processed > 0 else 0, 1
            )
        }
    
    def health_check(self) -> dict[str, bool]:
        """Perform a health check on all components.
        
        Returns:
            dict[str, bool]: Health status of each component.
        """
        logger.info("Performing system health check")
        
        health = {
            'database': False,
            'temp_directory': False,
            'video_downloader': False,
            'frame_extractor': False
        }
        
        try:
            # Check database connection
            health['database'] = self.database_manager.get_connection_status()
            
            # Check temp directory
            health['temp_directory'] = self.temp_dir.exists() and self.temp_dir.is_dir()
            
            # Check video downloader (basic validation)
            health['video_downloader'] = hasattr(self.video_downloader, 'session')
            
            # Check frame extractor
            health['frame_extractor'] = hasattr(self.frame_extractor, 'default_percentages')
            
        except Exception as error:
            logger.error(f"Health check failed: {error}")
        
        logger.info(f"Health check results: {health}")
        return health 