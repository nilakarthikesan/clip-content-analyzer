"""Video downloader with rate limiting and progress tracking.

This module provides a VideoDownloader class that handles downloading videos
from URLs with rate limiting, progress tracking, and comprehensive error handling.
"""

import logging
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
import validators
from ratelimit import limits, sleep_and_retry

from config import DOWNLOAD_CHUNK_SIZE, MAX_FILE_SIZE_BYTES

logger = logging.getLogger(__name__)


class VideoDownloader:
    """Handles video downloads with rate limiting and validation."""
    
    # Rate limiting: 5 downloads per minute to be respectful to servers
    CALLS = 5
    RATE_LIMIT_PERIOD = 60  # seconds
    
    def __init__(self, max_file_size: Optional[int] = None) -> None:
        """Initialize the video downloader.
        
        Args:
            max_file_size: Maximum file size in bytes. Defaults to config value.
        """
        self.max_file_size = max_file_size or MAX_FILE_SIZE_BYTES
        self.session = requests.Session()
        self._setup_session()
        logger.info(f"VideoDownloader initialized with {self.max_file_size:,} byte limit")
    
    def _setup_session(self) -> None:
        """Configure the requests session with appropriate headers and timeouts."""
        self.session.headers.update({
            'User-Agent': 'ClipContentAnalyzer/1.0 (Educational Project)',
            'Accept': 'video/*,*/*;q=0.9',
        })
        # Set reasonable timeouts
        self.session.timeout = (10, 300)  # (connect, read) timeouts
    
    def validate_url(self, url: str) -> bool:
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
    
    @sleep_and_retry
    @limits(calls=CALLS, period=RATE_LIMIT_PERIOD)
    def _rate_limited_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make a rate-limited HTTP request.
        
        Args:
            method: HTTP method (GET, HEAD, etc.).
            url: URL to request.
            **kwargs: Additional arguments for requests.
            
        Returns:
            requests.Response: The HTTP response.
        """
        logger.debug(f"Making rate-limited {method} request to {url}")
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    
    def _check_file_size(self, url: str) -> Optional[int]:
        """Check the file size before downloading.
        
        Args:
            url: URL to check.
            
        Returns:
            Optional[int]: File size in bytes if available, None otherwise.
            
        Raises:
            ValueError: If file size exceeds maximum allowed.
        """
        try:
            head_response = self._rate_limited_request('HEAD', url, timeout=30)
            content_length = head_response.headers.get('content-length')
            
            if content_length:
                file_size = int(content_length)
                if file_size > self.max_file_size:
                    raise ValueError(
                        f"File size {file_size:,} bytes exceeds maximum allowed "
                        f"{self.max_file_size:,} bytes"
                    )
                logger.info(f"File size check passed: {file_size:,} bytes")
                return file_size
            
            logger.warning("Content-Length header not found, proceeding with download")
            return None
            
        except requests.exceptions.RequestException as error:
            logger.warning(f"Could not check file size: {error}")
            return None
    
    def download_video(self, url: str, local_path: Path, progress_callback: Optional[callable] = None) -> bool:
        """Download a video from URL to local file with rate limiting and progress tracking.
        
        Args:
            url: URL of the video to download.
            local_path: Local path where the video should be saved.
            progress_callback: Optional callback function for progress updates.
                              Should accept (downloaded_bytes, total_bytes) parameters.
        
        Returns:
            bool: True if download was successful, False otherwise.
            
        Raises:
            ValueError: If URL is invalid or file size exceeds limits.
            requests.RequestException: If download fails.
            IOError: If file writing fails.
        """
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        logger.info(f"Starting download from: {url}")
        logger.info(f"Saving to: {local_path}")
        
        # Check file size first
        expected_size = self._check_file_size(url)
        
        # Ensure parent directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        total_downloaded = 0
        
        try:
            # Download file in chunks with rate limiting
            response = self._rate_limited_request('GET', url, stream=True, timeout=30)
            
            with open(local_path, 'wb') as file_handle:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if chunk:  # Filter out keep-alive chunks
                        file_handle.write(chunk)
                        total_downloaded += len(chunk)
                        
                        # Check file size during download
                        if total_downloaded > self.max_file_size:
                            raise ValueError(
                                f"Download exceeded maximum file size: {self.max_file_size:,} bytes"
                            )
                        
                        # Call progress callback if provided
                        if progress_callback:
                            progress_callback(total_downloaded, expected_size)
            
            download_time = time.time() - start_time
            speed_mbps = (total_downloaded / (1024 * 1024)) / download_time if download_time > 0 else 0
            
            logger.info(
                f"Download completed! Size: {total_downloaded:,} bytes, "
                f"Time: {download_time:.1f}s, Speed: {speed_mbps:.1f} MB/s"
            )
            return True
            
        except requests.exceptions.Timeout as error:
            logger.error(f"Download timeout: {error}")
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
        finally:
            # Clean up partial download on failure
            if local_path.exists() and total_downloaded == 0:
                try:
                    local_path.unlink()
                    logger.info("Cleaned up failed download")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up partial download: {cleanup_error}")
    
    def __del__(self) -> None:
        """Clean up the requests session."""
        if hasattr(self, 'session'):
            self.session.close() 