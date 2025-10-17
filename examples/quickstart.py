#!/usr/bin/env python3
"""
Quick Start Example

Demonstrates basic usage of the research-ai package.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "main" / "python"))

from services.youtube_collector import YouTubeCollector
from utils.data_preprocessor import DataPreprocessor
from models.sentiment_analyzer import SentimentAnalyzer
from models.topic_model import TopicModel


def example_data_collection():
    """Example: Collect comments from YouTube videos."""
    print("\n" + "="*60)
    print("Example 1: Data Collection")
    print("="*60)

    # Initialize collector
    collector = YouTubeCollector()  # API key from environment

    # Collect comments from a single video
    video_id = "dQw4w9WgXcQ"  # Replace with actual video ID
    print(f"Collecting comments from video: {video_id}")

    try:
        comments = collector.get_video_comments(video_id, max_comments=10)
        print(f"Collected {len(comments)} comments")

        # Display first comment
        if comments:
            print(f"\nFirst comment:")
            print(f"  Author: {comments[0]['author']}")
            print(f"  Text: {comments[0]['text'][:100]}...")
            print(f"  Likes: {comments[0]['like_count']}")

    except Exception as e:
        print(f"Error: {e}")
        print("Note: Set YOUTUBE_API_KEY environment variable")


def example_preprocessing():
    """Example: Preprocess comment data."""
    print("\n" + "="*60)
    print("Example 2: Data Preprocessing")
    print("="*60)

    # Sample comments
    comments = [
        {
            'video_id': 'abc123',
            'comment_id': 'comment1',
            'author': 'User1',
            'text': '这个视频真的很棒！太喜欢了！',
            'like_count': 10,
            'published_at': '2024-01-15T10:30:00Z',
            'reply_count': 2
        },
        {
            'video_id': 'abc123',
            'comment_id': 'comment2',
            'author': 'User2',
            'text': '不太好看，感觉很无聊...',
            'like_count': 1,
            'published_at': '2024-01-15T11:00:00Z',
            'reply_count': 0
        }
    ]

    # Preprocess
    preprocessor = DataPreprocessor()
    df = preprocessor.preprocess_comments(comments, clean_text=True)

    print(f"\nPreprocessed {len(df)} comments")
    print("\nDataFrame columns:", df.columns.tolist())
    print("\nFirst few rows:")
    print(df[['author', 'text_clean', 'text_length']].head())


def example_sentiment_analysis():
    """Example: Sentiment analysis."""
    print("\n" + "="*60)
    print("Example 3: Sentiment Analysis")
    print("="*60)

    # Initialize analyzer (using simple backend for quick demo)
    analyzer = SentimentAnalyzer(backend='simple')

    # Analyze single text
    texts = [
        "这个视频太棒了！",
        "不好看，很无聊",
        "还行吧，一般般"
    ]

    print("\nAnalyzing sentiments:")
    for text in texts:
        result = analyzer.analyze(text)
        print(f"  Text: {text}")
        print(f"  Sentiment: {result['sentiment']} (confidence: {result['confidence']:.2f})")


def example_topic_modeling():
    """Example: Topic modeling."""
    print("\n" + "="*60)
    print("Example 4: Topic Modeling")
    print("="*60)

    # Sample texts
    texts = [
        "这个AI视频制作得很专业",
        "感觉这是AI生成的内容",
        "非常有创意的视频",
        "剪辑很棒",
        "音乐配得很好",
        "画面质量很高",
        "这个创作者很有才华",
        "视频内容很有深度",
    ]

    # Initialize and fit topic model
    print("\nFitting LDA topic model...")
    model = TopicModel(algorithm='LDA', n_topics=2)
    model.fit(texts)

    # Display topics
    print("\nExtracted topics:")
    model.print_topics(n_words=5)


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print(" research-ai Quick Start Examples")
    print("="*70)

    # Note: Data collection requires API key
    # example_data_collection()

    example_preprocessing()
    example_sentiment_analysis()
    example_topic_modeling()

    print("\n" + "="*70)
    print("Examples complete!")
    print("="*70 + "\n")

    print("Next steps:")
    print("1. Set YOUTUBE_API_KEY environment variable")
    print("2. Run: python scripts/collect_data.py --video-list your_videos.txt")
    print("3. Run: python scripts/preprocess_data.py --input data/raw/comments.json --output data/processed/comments.csv")
    print("4. Explore notebooks/ directory for detailed analysis")


if __name__ == '__main__':
    main()
