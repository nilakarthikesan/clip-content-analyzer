"""Frame extraction module for video processing.

This module provides functionality to extract frames from video files at
specified time percentages using MoviePy and PIL.
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image

from config import DEFAULT_FRAME_PERCENTAGES

logger = logging.getLogger(__name__)


def extract_frames_at_percentages(
    video_path: str | Path,
    percentages: Optional[list[float]] = None
) -> list[Image.Image]:
    """Extract frames from video at specified time percentages.
    
    Args:
        video_path: Path to the video file to process.
        percentages: List of time percentages (0.0-1.0) to extract frames at.
                    Defaults to [0.25, 0.5, 0.75].
    
    Returns:
        list[Image.Image]: List of PIL Images extracted from the video.
    
    Raises:
        FileNotFoundError: If the video file doesn't exist.
        ValueError: If percentages are invalid or video cannot be processed.
        RuntimeError: If frame extraction fails.
    """
    if percentages is None:
        percentages = DEFAULT_FRAME_PERCENTAGES.copy()
    
    # Validate inputs
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not percentages:
        raise ValueError("At least one percentage must be specified")
    
    for percentage in percentages:
        if not 0.0 <= percentage <= 1.0:
            raise ValueError(f"Percentage must be between 0.0 and 1.0, got: {percentage}")
    
    logger.info(f"Extracting frames from {video_path} at percentages: {percentages}")
    
    clip: Optional[VideoFileClip] = None
    try:
        clip = VideoFileClip(str(video_path))
        duration = clip.duration
        
        if duration <= 0:
            raise ValueError(f"Invalid video duration: {duration}")
        
        frames = []
        for percentage in percentages:
            timestamp = duration * percentage
            logger.debug(f"Extracting frame at {percentage*100:.1f}% ({timestamp:.2f}s)")
            
            try:
                frame_array = clip.get_frame(timestamp)
                # Convert numpy array to PIL Image
                image = Image.fromarray(np.uint8(frame_array))
                frames.append(image)
            except Exception as error:
                logger.error(f"Failed to extract frame at {percentage}: {error}")
                raise RuntimeError(f"Frame extraction failed at {percentage}") from error
        
        logger.info(f"Successfully extracted {len(frames)} frames")
        return frames
        
    except Exception as error:
        logger.error(f"Failed to process video {video_path}: {error}")
        raise
    finally:
        # Ensure video clip is properly closed
        if clip is not None:
            try:
                clip.close()
            except Exception as error:
                logger.warning(f"Error closing video clip: {error}")


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    test_video_path = "path/to/your/video.mp4"
    
    try:
        frames = extract_frames_at_percentages(test_video_path)
        for i, image in enumerate(frames, 1):
            output_path = f"frame_{i}.jpg"
            image.save(output_path)
            print(f"Saved frame {i} to {output_path}")
    except Exception as error:
        print(f"Error: {error}") 