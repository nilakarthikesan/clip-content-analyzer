"""Frame extraction class for video processing.

This module provides a FrameExtractor class that handles frame extraction
from video files with proper resource management and comprehensive validation.
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image

from config import DEFAULT_FRAME_PERCENTAGES

logger = logging.getLogger(__name__)


class FrameExtractor:
    """Handles frame extraction from video files with resource management."""
    
    def __init__(self, default_percentages: Optional[list[float]] = None) -> None:
        """Initialize the frame extractor.
        
        Args:
            default_percentages: Default time percentages for frame extraction.
                                Defaults to config values [0.25, 0.5, 0.75].
        """
        self.default_percentages = default_percentages or DEFAULT_FRAME_PERCENTAGES.copy()
        logger.info(f"FrameExtractor initialized with percentages: {self.default_percentages}")
    
    def validate_percentages(self, percentages: list[float]) -> None:
        """Validate that percentages are within valid ranges.
        
        Args:
            percentages: List of percentages to validate.
            
        Raises:
            ValueError: If any percentage is invalid.
        """
        if not percentages:
            raise ValueError("At least one percentage must be specified")
        
        for percentage in percentages:
            if not isinstance(percentage, (int, float)):
                raise ValueError(f"Percentage must be a number, got: {type(percentage)}")
            if not 0.0 <= percentage <= 1.0:
                raise ValueError(f"Percentage must be between 0.0 and 1.0, got: {percentage}")
    
    def validate_video_file(self, video_path: Path) -> None:
        """Validate that the video file exists and is accessible.
        
        Args:
            video_path: Path to the video file.
            
        Raises:
            FileNotFoundError: If the video file doesn't exist.
            ValueError: If the file is not accessible or valid.
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not video_path.is_file():
            raise ValueError(f"Path is not a file: {video_path}")
        
        if video_path.stat().st_size == 0:
            raise ValueError(f"Video file is empty: {video_path}")
    
    def extract_frames_at_percentages(
        self,
        video_path: str | Path,
        percentages: Optional[list[float]] = None,
        progress_callback: Optional[callable] = None
    ) -> list[Image.Image]:
        """Extract frames from video at specified time percentages.
        
        Args:
            video_path: Path to the video file to process.
            percentages: List of time percentages (0.0-1.0) to extract frames at.
                        Defaults to instance default percentages.
            progress_callback: Optional callback function for progress updates.
                              Should accept (current_frame, total_frames, percentage) parameters.
        
        Returns:
            list[Image.Image]: List of PIL Images extracted from the video.
        
        Raises:
            FileNotFoundError: If the video file doesn't exist.
            ValueError: If percentages are invalid or video cannot be processed.
            RuntimeError: If frame extraction fails.
        """
        if percentages is None:
            percentages = self.default_percentages.copy()
        
        # Validate inputs
        video_path = Path(video_path)
        self.validate_video_file(video_path)
        self.validate_percentages(percentages)
        
        logger.info(f"Extracting {len(percentages)} frames from {video_path}")
        logger.debug(f"Frame percentages: {percentages}")
        
        clip: Optional[VideoFileClip] = None
        extracted_frames = []
        
        try:
            # Load video clip
            clip = VideoFileClip(str(video_path))
            duration = clip.duration
            
            if duration <= 0:
                raise ValueError(f"Invalid video duration: {duration}s")
            
            logger.info(f"Video duration: {duration:.2f}s")
            
            # Extract frames at each percentage
            for i, percentage in enumerate(percentages, 1):
                timestamp = duration * percentage
                logger.debug(f"Extracting frame {i}/{len(percentages)} at {percentage*100:.1f}% ({timestamp:.2f}s)")
                
                try:
                    # Extract frame as numpy array
                    frame_array = clip.get_frame(timestamp)
                    
                    # Validate frame data
                    if frame_array is None or frame_array.size == 0:
                        raise RuntimeError(f"Failed to extract frame data at {percentage}")
                    
                    # Convert numpy array to PIL Image
                    image = Image.fromarray(np.uint8(frame_array))
                    
                    # Validate image
                    if image.size[0] == 0 or image.size[1] == 0:
                        raise RuntimeError(f"Invalid image dimensions at {percentage}")
                    
                    extracted_frames.append(image)
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(i, len(percentages), percentage)
                    
                    logger.debug(f"Successfully extracted frame {i}: {image.size}")
                    
                except Exception as error:
                    logger.error(f"Failed to extract frame at {percentage*100:.1f}%: {error}")
                    raise RuntimeError(f"Frame extraction failed at {percentage*100:.1f}%") from error
            
            logger.info(f"Successfully extracted {len(extracted_frames)} frames")
            return extracted_frames
            
        except Exception as error:
            logger.error(f"Failed to process video {video_path}: {error}")
            raise
        finally:
            # Ensure video clip is properly closed
            if clip is not None:
                try:
                    clip.close()
                    logger.debug("Video clip closed successfully")
                except Exception as error:
                    logger.warning(f"Error closing video clip: {error}")
    
    def extract_single_frame(
        self,
        video_path: str | Path,
        timestamp: float
    ) -> Image.Image:
        """Extract a single frame at a specific timestamp.
        
        Args:
            video_path: Path to the video file to process.
            timestamp: Time in seconds to extract the frame.
        
        Returns:
            Image.Image: PIL Image extracted from the video.
        
        Raises:
            FileNotFoundError: If the video file doesn't exist.
            ValueError: If timestamp is invalid.
            RuntimeError: If frame extraction fails.
        """
        video_path = Path(video_path)
        self.validate_video_file(video_path)
        
        if timestamp < 0:
            raise ValueError(f"Timestamp must be non-negative, got: {timestamp}")
        
        clip: Optional[VideoFileClip] = None
        
        try:
            clip = VideoFileClip(str(video_path))
            
            if timestamp > clip.duration:
                raise ValueError(f"Timestamp {timestamp}s exceeds video duration {clip.duration}s")
            
            frame_array = clip.get_frame(timestamp)
            image = Image.fromarray(np.uint8(frame_array))
            
            logger.info(f"Extracted single frame at {timestamp}s: {image.size}")
            return image
            
        except Exception as error:
            logger.error(f"Failed to extract frame at {timestamp}s: {error}")
            raise RuntimeError(f"Frame extraction failed at {timestamp}s") from error
        finally:
            if clip is not None:
                try:
                    clip.close()
                except Exception as error:
                    logger.warning(f"Error closing video clip: {error}")
    
    def get_video_info(self, video_path: str | Path) -> dict[str, any]:
        """Get basic information about a video file.
        
        Args:
            video_path: Path to the video file.
        
        Returns:
            dict: Video information including duration, fps, size, etc.
        """
        video_path = Path(video_path)
        self.validate_video_file(video_path)
        
        clip: Optional[VideoFileClip] = None
        
        try:
            clip = VideoFileClip(str(video_path))
            
            info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,
                'filename': video_path.name,
                'file_size': video_path.stat().st_size
            }
            
            logger.info(f"Video info: {info}")
            return info
            
        except Exception as error:
            logger.error(f"Failed to get video info: {error}")
            raise RuntimeError(f"Failed to get video info") from error
        finally:
            if clip is not None:
                try:
                    clip.close()
                except Exception as error:
                    logger.warning(f"Error closing video clip: {error}") 