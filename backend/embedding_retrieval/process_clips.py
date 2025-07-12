"""Video processing pipeline for media clips.

This module provides the main processing pipeline that downloads videos,
extracts frames, and manages the complete workflow for video analysis.
"""

import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
import validators

from config import DOWNLOAD_CHUNK_SIZE, MAX_FILE_SIZE_BYTES, TEMP_DIR
from frame_extractor import extract_frames_at_percentages
from supabase_client import fetch_media_clips

logger = logging.getLogger(__name__)


def _validate_url(url: str) -> bool:
    """Validate that a URL is properly formatted and uses allowed schemes.
    
    Args:
        url: URL string to validate.
        
    Returns:
        bool: True if URL is valid, False otherwise.
    """
    if not validators.url(url):
        return False
    
    parsed = urlparse(url)
    allowed_schemes = {'http', 'https'}
    return parsed.scheme in allowed_schemes


def download_video_file(url: str, local_path: Path) -> None:
    """Download a video from URL to local file with validation and progress tracking.
    
    Args:
        url: URL of the video to download.
        local_path: Local path where the video should be saved.
        
    Raises:
        ValueError: If URL is invalid or file size exceeds limits.
        requests.RequestException: If download fails.
        IOError: If file writing fails.
    """
    if not _validate_url(url):
        raise ValueError(f"Invalid URL: {url}")
    
    logger.info(f"Starting download from: {url}")
    logger.info(f"Saving to: {local_path}")
    
    try:
        # Make HEAD request to check file size
        head_response = requests.head(url, timeout=30)
        head_response.raise_for_status()
        
        content_length = head_response.headers.get('content-length')
        if content_length:
            file_size = int(content_length)
            if file_size > MAX_FILE_SIZE_BYTES:
                raise ValueError(
                    f"File size {file_size} bytes exceeds maximum allowed "
                    f"{MAX_FILE_SIZE_BYTES} bytes"
                )
            logger.info(f"File size: {file_size:,} bytes")
        
        # Download file in chunks
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Ensure parent directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        total_downloaded = 0
        with open(local_path, 'wb') as file_handle:
            for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                if chunk:  # Filter out keep-alive chunks
                    file_handle.write(chunk)
                    total_downloaded += len(chunk)
                    
                    # Check file size during download
                    if total_downloaded > MAX_FILE_SIZE_BYTES:
                        raise ValueError(
                            f"Download exceeded maximum file size: {MAX_FILE_SIZE_BYTES}"
                        )
        
        logger.info(f"Download completed! Total size: {total_downloaded:,} bytes")
        
    except requests.exceptions.Timeout as error:
        raise requests.RequestException(f"Download timeout: {error}") from error
    except requests.exceptions.RequestException as error:
        logger.error(f"HTTP/Network error: {error}")
        raise
    except IOError as error:
        logger.error(f"File writing error: {error}")
        raise
    except Exception as error:
        logger.error(f"Unexpected download error: {error}")
        raise


def process_single_clip(clip: dict) -> Optional[list[str]]:
    """Process a single video clip by downloading and extracting frames.
    
    Args:
        clip: Dictionary containing clip metadata from database.
        
    Returns:
        Optional[list[str]]: List of frame file paths if successful, None if failed.
    """
    clip_id = clip.get('id')
    clip_title = clip.get('title', 'Unknown')
    video_url = clip.get('clip_path')
    
    if not video_url:
        logger.error(f"No clip_path found for clip {clip_id}")
        return None
    
    # Create temporary file path
    temp_file = TEMP_DIR / f"{clip_id}.mov"
    frame_paths = []
    
    try:
        logger.info(f"Processing clip: {clip_title} (ID: {clip_id})")
        
        # Download video
        download_video_file(video_url, temp_file)
        
        # Extract frames
        frames = extract_frames_at_percentages(temp_file)
        
        # Save frames
        for i, image in enumerate(frames, 1):
            frame_path = f"{clip_id}_frame_{i}.jpg"
            image.save(frame_path)
            frame_paths.append(frame_path)
            logger.debug(f"Saved frame {i} to {frame_path}")
        
        logger.info(f"Successfully processed {clip_title}: {len(frames)} frames extracted")
        return frame_paths
        
    except Exception as error:
        logger.error(f"Failed to process clip {clip_title}: {error}")
        return None
    finally:
        # Clean up temporary file
        if temp_file.exists():
            try:
                temp_file.unlink()
                logger.debug(f"Cleaned up temporary file: {temp_file}")
            except Exception as error:
                logger.warning(f"Failed to clean up {temp_file}: {error}")


def process_all_clips() -> dict[str, list[str]]:
    """Process all clips from the database.
    
    Returns:
        dict[str, list[str]]: Dictionary mapping clip IDs to frame file paths.
    """
    logger.info("Starting to process all clips")
    
    try:
        clips = fetch_media_clips()
        if not clips:
            logger.warning("No clips found in database")
            return {}
        
        logger.info(f"Found {len(clips)} clips to process")
        
        results = {}
        successful_count = 0
        
        for clip in clips:
            clip_id = clip.get('id', 'unknown')
            frame_paths = process_single_clip(clip)
            
            if frame_paths:
                results[clip_id] = frame_paths
                successful_count += 1
        
        logger.info(
            f"Processing complete: {successful_count}/{len(clips)} clips processed successfully"
        )
        return results
        
    except Exception as error:
        logger.error(f"Failed to process clips: {error}")
        raise


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        results = process_all_clips()
        print(f"Processing complete. {len(results)} clips processed successfully.")
        for clip_id, frame_paths in results.items():
            print(f"  {clip_id}: {len(frame_paths)} frames")
    except Exception as error:
        print(f"Error: {error}") 