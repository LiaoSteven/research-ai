#!/usr/bin/env python3
"""
Data Collection Script

Collect YouTube comments from a list of video URLs.

Usage:
    python scripts/collect_data.py --video-list data/raw/video_urls.txt --video-type ai_generated
"""

import argparse
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "main" / "python"))

from services.youtube_collector import YouTubeCollector
from core.config import get_config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Collect YouTube comments')
    parser.add_argument(
        '--video-list',
        type=str,
        required=True,
        help='Path to file containing video URLs (one per line)'
    )
    parser.add_argument(
        '--video-type',
        type=str,
        choices=['ai_generated', 'non_ai'],
        help='Type label for videos'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw',
        help='Output directory for collected data'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='YouTube Data API key (overrides environment variable)'
    )
    parser.add_argument(
        '--max-comments',
        type=int,
        help='Maximum comments per video'
    )

    args = parser.parse_args()

    try:
        # Load video URLs
        logger.info(f"Loading video URLs from {args.video_list}")
        with open(args.video_list, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        # Extract video IDs
        collector = YouTubeCollector(api_key=args.api_key)
        video_ids = []
        for url in urls:
            video_id = collector.extract_video_id(url)
            if video_id:
                video_ids.append(video_id)
            else:
                logger.warning(f"Could not extract video ID from: {url}")

        logger.info(f"Found {len(video_ids)} valid video IDs")

        if not video_ids:
            logger.error("No valid video IDs found")
            return 1

        # Collect comments
        stats = collector.collect_from_video_list(
            video_ids=video_ids,
            output_dir=args.output_dir,
            video_type=args.video_type
        )

        logger.info("="*60)
        logger.info("Collection Summary:")
        logger.info(f"  Total videos processed: {stats['total_videos']}")
        logger.info(f"  Total comments collected: {stats['total_comments']}")
        logger.info(f"  Failed videos: {stats['failed_videos']}")
        logger.info("="*60)

        return 0

    except Exception as e:
        logger.error(f"Error during data collection: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
