"""Main entry point for the clip content analyzer with class-based architecture.

This module provides the primary interface for processing video clips using
a clean class-based architecture with proper separation of concerns.
"""

import logging
import sys
from pathlib import Path

from config import LOG_LEVEL, TEMP_DIR
from video_processor import VideoProcessor

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure application logging with both console and file output."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create formatters
    formatter = logging.Formatter(log_format)
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    file_handler = logging.FileHandler('clip_processor.log')
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def ensure_directories() -> None:
    """Ensure required directories exist."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured temp directory exists: {TEMP_DIR}")


def print_processing_summary(results: dict, processor: VideoProcessor) -> None:
    """Print a comprehensive processing summary.
    
    Args:
        results: Dictionary of processing results.
        processor: VideoProcessor instance for statistics.
    """
    if not results:
        print("\n❌ No clips were processed.")
        return
    
    stats = processor.get_processing_statistics()
    
    # Calculate frame statistics
    total_frames = sum(result.frames_extracted for result in results.values())
    successful_results = [r for r in results.values() if r.success]
    failed_results = [r for r in results.values() if not r.success]
    
    # Print summary header
    print(f"\n{'='*60}")
    print(f"🎬 CLIP PROCESSING SUMMARY")
    print(f"{'='*60}")
    
    # Overall statistics
    print(f"📊 Overall Statistics:")
    print(f"   Total clips processed: {stats['total_processed']}")
    print(f"   ✅ Successful: {stats['successful_processed']}")
    print(f"   ❌ Failed: {stats['failed_processed']}")
    print(f"   📈 Success rate: {stats['success_rate_percent']:.1f}%")
    print(f"   🖼️  Total frames extracted: {total_frames}")
    
    if successful_results:
        avg_frames = total_frames / len(successful_results)
        avg_time = sum(r.processing_time for r in successful_results if r.processing_time) / len(successful_results)
        print(f"   ⏱️  Average processing time: {avg_time:.2f}s")
        print(f"   📋 Average frames per clip: {avg_frames:.1f}")
    
    # Successful clips details
    if successful_results:
        print(f"\n✅ Successfully Processed Clips:")
        for result in successful_results:
            time_str = f" ({result.processing_time:.2f}s)" if result.processing_time else ""
            print(f"   🎥 {result.clip_title} ({result.clip_id})")
            print(f"      └── {result.frames_extracted} frames extracted{time_str}")
    
    # Failed clips details
    if failed_results:
        print(f"\n❌ Failed Clips:")
        for result in failed_results:
            time_str = f" ({result.processing_time:.2f}s)" if result.processing_time else ""
            print(f"   🚫 {result.clip_title} ({result.clip_id}){time_str}")
            if result.error_message:
                print(f"      └── Error: {result.error_message}")
    
    print(f"\n{'='*60}")


def main() -> None:
    """Main application entry point with class-based architecture."""
    setup_logging()
    logger.info("Starting clip content analyzer with class-based architecture")
    
    try:
        # Initialize directories
        ensure_directories()
        
        # Create video processor instance
        processor = VideoProcessor()
        
        # Perform health check
        logger.info("Performing system health check...")
        health = processor.health_check()
        
        unhealthy_components = [comp for comp, status in health.items() if not status]
        if unhealthy_components:
            logger.warning(f"Some components are unhealthy: {unhealthy_components}")
            print(f"⚠️  Warning: Unhealthy components detected: {', '.join(unhealthy_components)}")
        else:
            logger.info("✅ All system components are healthy")
            print("✅ System health check passed")
        
        # Process all clips
        print("\n🚀 Starting video processing...")
        results = processor.process_all_clips()
        
        # Print comprehensive summary
        print_processing_summary(results, processor)
        
        # Final logging
        stats = processor.get_processing_statistics()
        logger.info(f"Application completed: {stats}")
        
        # Exit with appropriate code
        if stats['failed_processed'] > 0:
            logger.warning("Some clips failed to process")
            sys.exit(1)
        else:
            logger.info("All clips processed successfully")
            sys.exit(0)
    
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        print("\n⏸️  Processing interrupted by user.")
        sys.exit(130)
    except Exception as error:
        logger.error(f"Application error: {error}", exc_info=True)
        print(f"\n💥 Error: {error}")
        print("Check the logs for detailed error information.")
        sys.exit(1)


if __name__ == "__main__":
    main() 