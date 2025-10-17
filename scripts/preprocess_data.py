#!/usr/bin/env python3
"""
Data Preprocessing Script

Clean and preprocess collected YouTube comments.

Usage:
    python scripts/preprocess_data.py --input data/raw/comments.json --output data/processed/comments_clean.csv
"""

import argparse
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "main" / "python"))

from utils.data_preprocessor import DataPreprocessor
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Preprocess YouTube comments')
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input JSON file with raw comments'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output file for preprocessed data (CSV or Parquet)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'parquet'],
        default='csv',
        help='Output format'
    )
    parser.add_argument(
        '--no-clean-text',
        action='store_true',
        help='Skip text cleaning step'
    )

    args = parser.parse_args()

    try:
        # Load data
        logger.info(f"Loading data from {args.input}")
        comments = DataPreprocessor.load_from_json(args.input)

        # Preprocess
        preprocessor = DataPreprocessor()
        df = preprocessor.preprocess_comments(
            comments,
            clean_text=not args.no_clean_text
        )

        # Generate statistics
        stats = preprocessor.generate_summary_statistics(df)
        logger.info("\n" + "="*60)
        logger.info("Preprocessing Summary:")
        logger.info(f"  Total comments: {stats['total_comments']}")
        logger.info(f"  Unique videos: {stats['unique_videos']}")
        logger.info(f"  Unique authors: {stats['unique_authors']}")
        logger.info(f"  Avg text length: {stats['text_statistics']['avg_length']:.1f}")
        logger.info(f"  Avg word count: {stats['text_statistics']['avg_word_count']:.1f}")
        logger.info("="*60 + "\n")

        # Save preprocessed data
        if args.format == 'csv':
            DataPreprocessor.save_to_csv(df, args.output)
        else:
            DataPreprocessor.save_to_parquet(df, args.output)

        # Save statistics
        stats_file = Path(args.output).parent / 'preprocessing_stats.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"Statistics saved to {stats_file}")

        return 0

    except Exception as e:
        logger.error(f"Error during preprocessing: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
