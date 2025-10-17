"""
YouTube Data Collector Service

Collects comments from YouTube videos using the YouTube Data API v3.
"""

import time
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import json

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    build = None
    HttpError = None

# Handle both relative and absolute imports
try:
    from ..core.config import get_config
except ImportError:
    from core.config import get_config


logger = logging.getLogger(__name__)


class YouTubeCollector:
    """
    YouTube comment collector using YouTube Data API v3.

    Example:
        >>> collector = YouTubeCollector(api_key="YOUR_API_KEY")
        >>> comments = collector.get_video_comments("dQw4w9WgXcQ")
        >>> collector.save_comments(comments, "data/raw/comments.json")
    """

    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize YouTube collector.

        Args:
            api_key: YouTube Data API key. If None, loads from config.
            config_path: Optional path to config file.

        Raises:
            ImportError: If google-api-python-client is not installed.
            ValueError: If API key is not provided or found in config.
        """
        if build is None:
            raise ImportError(
                "google-api-python-client is required. Install with: "
                "pip install google-api-python-client"
            )

        self.config = get_config(config_path)
        self.api_key = api_key or self.config.youtube_api_key

        if not self.api_key:
            raise ValueError(
                "YouTube API key not found. "
                "Provide via api_key parameter or set YOUTUBE_API_KEY environment variable."
            )

        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.rate_limit_delay = self.config.get('rate_limit.requests_per_second', 1.0)
        self.max_results = self.config.get('youtube.max_results_per_request', 100)

        logger.info("YouTubeCollector initialized")

    def get_video_comments(
        self,
        video_id: str,
        max_comments: Optional[int] = None,
        include_replies: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get comments for a specific video.

        Args:
            video_id: YouTube video ID
            max_comments: Maximum number of comments to retrieve (None for all)
            include_replies: Whether to include comment replies

        Returns:
            List of comment dictionaries with metadata

        Example:
            >>> comments = collector.get_video_comments("dQw4w9WgXcQ", max_comments=50)
        """
        comments = []
        page_token = None
        requests_made = 0

        max_comments = max_comments or self.config.get('data_collection.max_comments_per_video', 100)

        try:
            while True:
                # Rate limiting
                if requests_made > 0:
                    time.sleep(1.0 / self.rate_limit_delay)

                # Request comment threads
                request = self.youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    maxResults=min(self.max_results, max_comments - len(comments)),
                    pageToken=page_token,
                    textFormat='plainText'
                )

                response = request.execute()
                requests_made += 1

                # Process comment threads
                for item in response.get('items', []):
                    comment_data = self._parse_comment_thread(item, video_id)
                    comments.append(comment_data)

                    # Include replies if requested
                    if include_replies and 'replies' in item:
                        for reply in item['replies']['comments']:
                            reply_data = self._parse_reply(reply, video_id, comment_data['comment_id'])
                            comments.append(reply_data)

                # Check if we have enough comments or reached the end
                page_token = response.get('nextPageToken')
                if not page_token or len(comments) >= max_comments:
                    break

                logger.debug(f"Collected {len(comments)} comments so far for video {video_id}")

            logger.info(f"Collected {len(comments)} comments for video {video_id}")
            return comments[:max_comments]

        except HttpError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Error collecting comments for video {video_id}: {e}")
            raise

    def _parse_comment_thread(self, item: Dict, video_id: str) -> Dict[str, Any]:
        """Parse a comment thread item into structured data."""
        snippet = item['snippet']['topLevelComment']['snippet']

        return {
            'video_id': video_id,
            'comment_id': item['snippet']['topLevelComment']['id'],
            'parent_id': None,
            'author': snippet['authorDisplayName'],
            'author_channel_id': snippet.get('authorChannelId', {}).get('value'),
            'text': snippet['textDisplay'],
            'like_count': snippet['likeCount'],
            'published_at': snippet['publishedAt'],
            'updated_at': snippet['updatedAt'],
            'reply_count': item['snippet']['totalReplyCount'],
            'is_reply': False,
            'collected_at': datetime.utcnow().isoformat()
        }

    def _parse_reply(self, reply: Dict, video_id: str, parent_id: str) -> Dict[str, Any]:
        """Parse a reply comment into structured data."""
        snippet = reply['snippet']

        return {
            'video_id': video_id,
            'comment_id': reply['id'],
            'parent_id': parent_id,
            'author': snippet['authorDisplayName'],
            'author_channel_id': snippet.get('authorChannelId', {}).get('value'),
            'text': snippet['textDisplay'],
            'like_count': snippet['likeCount'],
            'published_at': snippet['publishedAt'],
            'updated_at': snippet['updatedAt'],
            'reply_count': 0,
            'is_reply': True,
            'collected_at': datetime.utcnow().isoformat()
        }

    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with video metadata
        """
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            )
            response = request.execute()

            if not response.get('items'):
                raise ValueError(f"Video not found: {video_id}")

            item = response['items'][0]
            snippet = item['snippet']
            statistics = item['statistics']

            return {
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_id': snippet['channelId'],
                'channel_title': snippet['channelTitle'],
                'published_at': snippet['publishedAt'],
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'collected_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting video info for {video_id}: {e}")
            raise

    def collect_from_video_list(
        self,
        video_ids: List[str],
        output_dir: str = "data/raw",
        video_type: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Collect comments from multiple videos.

        Args:
            video_ids: List of YouTube video IDs
            output_dir: Directory to save collected data
            video_type: Type label for videos (e.g., 'ai_generated', 'non_ai')

        Returns:
            Dictionary with collection statistics
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        all_comments = []
        video_metadata = []
        stats = {'total_videos': len(video_ids), 'total_comments': 0, 'failed_videos': 0}

        for idx, video_id in enumerate(video_ids, 1):
            logger.info(f"Processing video {idx}/{len(video_ids)}: {video_id}")

            try:
                # Get video info
                video_info = self.get_video_info(video_id)
                if video_type:
                    video_info['video_type'] = video_type
                video_metadata.append(video_info)

                # Get comments
                comments = self.get_video_comments(video_id)
                for comment in comments:
                    if video_type:
                        comment['video_type'] = video_type
                all_comments.extend(comments)

                stats['total_comments'] += len(comments)

            except Exception as e:
                logger.error(f"Failed to process video {video_id}: {e}")
                stats['failed_videos'] += 1
                continue

        # Save collected data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        type_suffix = f"_{video_type}" if video_type else ""

        comments_file = output_path / f"comments{type_suffix}_{timestamp}.json"
        videos_file = output_path / f"videos{type_suffix}_{timestamp}.json"

        self.save_comments(all_comments, comments_file)
        self.save_video_metadata(video_metadata, videos_file)

        logger.info(f"Collection complete. Stats: {stats}")
        return stats

    @staticmethod
    def save_comments(comments: List[Dict], output_file: str) -> None:
        """Save comments to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(comments)} comments to {output_file}")

    @staticmethod
    def save_video_metadata(videos: List[Dict], output_file: str) -> None:
        """Save video metadata to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved metadata for {len(videos)} videos to {output_file}")

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.

        Args:
            url: YouTube URL (full or shortened)

        Returns:
            Video ID or None if not found

        Example:
            >>> YouTubeCollector.extract_video_id("https://youtube.com/shorts/abc123")
            'abc123'
        """
        import re

        patterns = [
            r'(?:youtube\.com\/shorts\/)([\w-]+)',
            r'(?:youtube\.com\/watch\?v=)([\w-]+)',
            r'(?:youtu\.be\/)([\w-]+)',
            r'(?:youtube\.com\/embed\/)([\w-]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # If no pattern matches, assume it's already a video ID
        if re.match(r'^[\w-]{11}$', url):
            return url

        return None
