"""Main entry point for the clip content analyzer.

This module provides the primary interface for processing video clips,
extracting frames, and managing the complete video analysis pipeline.
"""

import logging
import sys
from pathlib import Path

from config import LOG_LEVEL, TEMP_DIR
from process_clips import process_all_clips


def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('clip_processor.log')
        ]
    )


def ensure_directories() -> None:
    """Ensure required directories exist."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting clip content analyzer")
        ensure_directories()
        
        # Process all clips
        results = process_all_clips()
        
        if results:
            logger.info(f"Successfully processed {len(results)} clips")
            
            # Print summary
            total_frames = sum(len(frames) for frames in results.values())
            print(f"\n=== PROCESSING SUMMARY ===")
            print(f"Clips processed: {len(results)}")
            print(f"Total frames extracted: {total_frames}")
            print(f"Average frames per clip: {total_frames / len(results):.1f}")
            
            print(f"\n=== CLIP DETAILS ===")
            for clip_id, frame_paths in results.items():
                print(f"  {clip_id}: {len(frame_paths)} frames")
        else:
            logger.warning("No clips were successfully processed")
            print("No clips were processed. Check logs for details.")
    
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        print("\nProcessing interrupted.")
    except Exception as error:
        logger.error(f"Application error: {error}", exc_info=True)
        print(f"Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
