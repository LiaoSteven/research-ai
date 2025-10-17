"""
Data Preprocessing Utilities

Handles cleaning, normalization, and transformation of YouTube comment data.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Preprocessor for YouTube comment data.

    Handles:
    - Text cleaning (remove URLs, emojis, special characters)
    - Duplicate removal
    - Spam filtering
    - Data normalization
    - Feature extraction
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize preprocessor.

        Args:
            config: Preprocessing configuration dictionary
        """
        # Handle both relative and absolute imports
        try:
            from ..core.config import get_config
        except ImportError:
            from core.config import get_config

        self.config = config or get_config().get_preprocessing_config()
        self.min_length = self.config.get('min_comment_length', 5)
        self.max_length = self.config.get('max_comment_length', 1000)
        self.remove_spam = self.config.get('remove_spam', True)
        self.remove_duplicates = self.config.get('remove_duplicates', True)

        logger.info("DataPreprocessor initialized")

    def preprocess_comments(
        self,
        comments: List[Dict[str, Any]],
        clean_text: bool = True
    ) -> pd.DataFrame:
        """
        Preprocess a list of comments.

        Args:
            comments: List of comment dictionaries
            clean_text: Whether to clean text content

        Returns:
            Preprocessed DataFrame
        """
        if not comments:
            logger.warning("No comments to preprocess")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(comments)
        initial_count = len(df)
        logger.info(f"Starting preprocessing with {initial_count} comments")

        # Basic cleaning
        df = self._filter_by_length(df)
        df = self._remove_empty_comments(df)

        if self.remove_duplicates:
            df = self._remove_duplicates(df)

        if self.remove_spam:
            df = self._filter_spam(df)

        if clean_text:
            df['text_clean'] = df['text'].apply(self.clean_text)
            df['text_length'] = df['text_clean'].str.len()
            df['word_count'] = df['text_clean'].str.split().str.len()

        # Extract temporal features
        df = self._extract_temporal_features(df)

        # Add metadata
        df['preprocessed_at'] = datetime.utcnow().isoformat()

        final_count = len(df)
        removed = initial_count - final_count
        logger.info(f"Preprocessing complete: {final_count} comments kept, {removed} removed")

        return df

    def clean_text(self, text: str) -> str:
        """
        Clean a single text string.

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return ""

        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # Remove mentions
        text = re.sub(r'@\w+', '', text)

        # Remove hashtags but keep the text
        text = re.sub(r'#(\w+)', r'\1', text)

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def _filter_by_length(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter comments by length."""
        before = len(df)
        df = df[df['text'].str.len().between(self.min_length, self.max_length)]
        after = len(df)

        if before > after:
            logger.debug(f"Filtered {before - after} comments by length")

        return df

    def _remove_empty_comments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove comments with empty or null text."""
        before = len(df)
        df = df[df['text'].notna() & (df['text'].str.strip() != '')]
        after = len(df)

        if before > after:
            logger.debug(f"Removed {before - after} empty comments")

        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate comments based on text content."""
        before = len(df)
        df = df.drop_duplicates(subset=['text'], keep='first')
        after = len(df)

        if before > after:
            logger.debug(f"Removed {before - after} duplicate comments")

        return df

    def _filter_spam(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter potential spam comments.

        Simple heuristics:
        - Too many repeated characters
        - Too many emojis
        - Too many special characters
        """
        def is_spam(text: str) -> bool:
            if not isinstance(text, str):
                return True

            # Check for excessive repeated characters
            if re.search(r'(.)\1{5,}', text):
                return True

            # Check for excessive special characters
            special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s\u4e00-\u9fff]', text)) / max(len(text), 1)
            if special_char_ratio > 0.5:
                return True

            # Check for common spam patterns
            spam_patterns = [
                r'点击.*链接',
                r'加.*微信',
                r'关注.*抽奖',
                r'免费领取',
            ]
            for pattern in spam_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True

            return False

        before = len(df)
        df = df[~df['text'].apply(is_spam)]
        after = len(df)

        if before > after:
            logger.debug(f"Filtered {before - after} spam comments")

        return df

    def _extract_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract temporal features from timestamps."""
        if 'published_at' in df.columns:
            df['published_datetime'] = pd.to_datetime(df['published_at'], errors='coerce')
            df['published_date'] = df['published_datetime'].dt.date
            df['published_year'] = df['published_datetime'].dt.year
            df['published_month'] = df['published_datetime'].dt.month
            df['published_day_of_week'] = df['published_datetime'].dt.dayofweek
            df['published_hour'] = df['published_datetime'].dt.hour

        return df

    @staticmethod
    def load_from_json(file_path: str) -> List[Dict[str, Any]]:
        """Load comments from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} comments from {file_path}")
        return data

    @staticmethod
    def save_to_csv(df: pd.DataFrame, output_file: str) -> None:
        """Save preprocessed data to CSV."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Saved {len(df)} rows to {output_file}")

    @staticmethod
    def save_to_parquet(df: pd.DataFrame, output_file: str) -> None:
        """Save preprocessed data to Parquet format (efficient for large datasets)."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_parquet(output_path, index=False, engine='pyarrow', compression='snappy')
        logger.info(f"Saved {len(df)} rows to {output_file}")

    def generate_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for preprocessed data.

        Args:
            df: Preprocessed DataFrame

        Returns:
            Dictionary with summary statistics
        """
        stats = {
            'total_comments': len(df),
            'unique_videos': df['video_id'].nunique() if 'video_id' in df.columns else 0,
            'unique_authors': df['author'].nunique() if 'author' in df.columns else 0,
            'date_range': {
                'start': df['published_datetime'].min().isoformat() if 'published_datetime' in df.columns else None,
                'end': df['published_datetime'].max().isoformat() if 'published_datetime' in df.columns else None,
            },
            'text_statistics': {
                'avg_length': df['text_length'].mean() if 'text_length' in df.columns else 0,
                'median_length': df['text_length'].median() if 'text_length' in df.columns else 0,
                'avg_word_count': df['word_count'].mean() if 'word_count' in df.columns else 0,
            },
            'engagement_statistics': {
                'total_likes': df['like_count'].sum() if 'like_count' in df.columns else 0,
                'avg_likes': df['like_count'].mean() if 'like_count' in df.columns else 0,
                'total_replies': df['reply_count'].sum() if 'reply_count' in df.columns else 0,
            }
        }

        if 'video_type' in df.columns:
            stats['video_types'] = df['video_type'].value_counts().to_dict()

        return stats
