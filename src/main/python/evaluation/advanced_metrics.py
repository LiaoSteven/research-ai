#!/usr/bin/env python3
"""
Advanced Metrics Module for YouTube Comment Analysis

This module implements four key quantitative metrics:
1. Audience Loyalty - measures subscriber intent
2. Content Stickiness - engagement index per video
3. Community Vitality - reply network analysis
4. Controversy Index - sentiment polarization

Requirements:
- pandas
- transformers (Hugging Face)
- networkx
- torch (for transformers)
"""

import sys
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional
import re
import warnings
warnings.filterwarnings('ignore')

# Try to import transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available. Controversy analysis will use fallback method.")


class AdvancedMetrics:
    """
    Advanced metrics calculator for YouTube comments and videos.

    Metrics:
    - Audience Loyalty: Proportion of comments mentioning subscription intent
    - Content Stickiness: Engagement index per video
    - Community Vitality: Reply network depth and connectivity
    - Controversy Index: Sentiment polarization score
    """

    def __init__(self, use_gpu: bool = False):
        """
        Initialize the metrics calculator.

        Args:
            use_gpu: Whether to use GPU for transformer models (if available)
        """
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        self.sentiment_analyzer = None

        # Initialize sentiment analyzer if transformers available
        if TRANSFORMERS_AVAILABLE:
            try:
                print(f"Initializing sentiment analyzer on {self.device}...")
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=0 if self.device == "cuda" else -1,
                    max_length=512,
                    truncation=True
                )
                print("✅ Sentiment analyzer loaded")
            except Exception as e:
                print(f"⚠️ Could not load sentiment analyzer: {e}")
                print("Will use fallback keyword-based method")
                self.sentiment_analyzer = None

    def calculate_loyalty_rate(self, comments_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate audience loyalty rate based on subscription-related keywords.

        Detects comments containing: subscribe, follow, joined, subbed, bell, notification

        Args:
            comments_df: DataFrame with 'text' and 'video_id' columns

        Returns:
            Dictionary mapping video_id to loyalty_rate (0-1)
        """
        print("\n" + "="*80)
        print("1️⃣ Calculating Audience Loyalty Rate")
        print("="*80)

        # Loyalty keywords
        loyalty_keywords = [
            'subscribe', 'subscribed', 'subscriber', 'sub',
            'follow', 'followed', 'follower',
            'joined', 'join',
            'bell', 'notification',
            'channel', 'support'
        ]

        # Create pattern
        pattern = '|'.join([f'\\b{kw}\\w*\\b' for kw in loyalty_keywords])

        # Detect loyalty comments
        comments_df['is_loyalty'] = comments_df['text'].str.lower().str.contains(
            pattern,
            regex=True,
            na=False
        )

        # Calculate per-video loyalty rate
        loyalty_by_video = comments_df.groupby('video_id').agg(
            loyalty_count=('is_loyalty', 'sum'),
            total_count=('is_loyalty', 'count')
        )
        loyalty_by_video['loyalty_rate'] = (
            loyalty_by_video['loyalty_count'] / loyalty_by_video['total_count']
        )

        # Overall statistics
        overall_loyalty = comments_df['is_loyalty'].sum()
        overall_rate = overall_loyalty / len(comments_df)

        print(f"\n📊 Loyalty Statistics:")
        print(f"  Total comments: {len(comments_df)}")
        print(f"  Loyalty comments: {overall_loyalty} ({overall_rate*100:.2f}%)")
        print(f"  Videos analyzed: {len(loyalty_by_video)}")
        print(f"\n  Top 5 videos by loyalty rate:")
        top5 = loyalty_by_video.nlargest(5, 'loyalty_rate')[['loyalty_count', 'total_count', 'loyalty_rate']]
        for idx, row in top5.iterrows():
            print(f"    {idx}: {row['loyalty_rate']*100:.1f}% ({int(row['loyalty_count'])}/{int(row['total_count'])})")

        return loyalty_by_video['loyalty_rate'].to_dict()

    def calculate_engagement_index(
        self,
        comments_df: pd.DataFrame,
        videos_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calculate content stickiness via engagement index.

        Formula: engagement_index = (comment_count/view_count + like_count/view_count) / 2

        Args:
            comments_df: DataFrame with 'video_id' column
            videos_df: DataFrame with 'video_id', 'view_count', 'like_count', 'comment_count'

        Returns:
            Dictionary mapping video_id to engagement_index
        """
        print("\n" + "="*80)
        print("2️⃣ Calculating Content Stickiness (Engagement Index)")
        print("="*80)

        # Count comments per video
        comment_counts = comments_df['video_id'].value_counts().to_dict()

        # Calculate engagement index
        engagement_results = []

        for _, video in videos_df.iterrows():
            video_id = video['video_id']
            view_count = int(video['view_count'])
            like_count = int(video['like_count'])

            # Get actual comment count from our data
            actual_comment_count = comment_counts.get(video_id, 0)

            if view_count > 0:
                comment_rate = actual_comment_count / view_count
                like_rate = like_count / view_count
                engagement_index = (comment_rate + like_rate) / 2
            else:
                engagement_index = 0.0

            engagement_results.append({
                'video_id': video_id,
                'view_count': view_count,
                'like_count': like_count,
                'comment_count': actual_comment_count,
                'comment_rate': comment_rate if view_count > 0 else 0,
                'like_rate': like_rate if view_count > 0 else 0,
                'engagement_index': engagement_index
            })

        engagement_df = pd.DataFrame(engagement_results)

        # Statistics
        print(f"\n📊 Engagement Statistics:")
        print(f"  Videos analyzed: {len(engagement_df)}")
        print(f"  Mean engagement index: {engagement_df['engagement_index'].mean():.6f}")
        print(f"  Median engagement index: {engagement_df['engagement_index'].median():.6f}")
        print(f"  Std engagement index: {engagement_df['engagement_index'].std():.6f}")
        print(f"\n  Top 5 videos by engagement:")
        top5 = engagement_df.nlargest(5, 'engagement_index')[
            ['video_id', 'view_count', 'comment_count', 'like_count', 'engagement_index']
        ]
        for _, row in top5.iterrows():
            print(f"    {row['video_id']}: {row['engagement_index']:.6f} "
                  f"(views={row['view_count']}, comments={row['comment_count']}, likes={row['like_count']})")

        return engagement_df.set_index('video_id')['engagement_index'].to_dict()

    def calculate_community_vitality(self, comments_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate community vitality using networkx reply graph analysis.

        Metrics:
        - Average reply chain depth
        - Average degree centrality
        - Network density

        Args:
            comments_df: DataFrame with 'comment_id', 'parent_id', 'video_id' columns

        Returns:
            Dictionary mapping video_id to avg_reply_depth
        """
        print("\n" + "="*80)
        print("3️⃣ Calculating Community Vitality (Reply Network)")
        print("="*80)

        vitality_results = {}

        for video_id in comments_df['video_id'].unique():
            video_comments = comments_df[comments_df['video_id'] == video_id].copy()

            # Create directed graph (parent -> child reply)
            G = nx.DiGraph()

            # Add all comments as nodes
            for comment_id in video_comments['comment_id']:
                G.add_node(comment_id)

            # Add edges for replies
            for _, row in video_comments.iterrows():
                if pd.notna(row['parent_id']) and row['parent_id'] != '':
                    # This is a reply
                    parent_id = row['parent_id']
                    child_id = row['comment_id']
                    if parent_id in G.nodes:
                        G.add_edge(parent_id, child_id)

            # Calculate metrics
            if G.number_of_nodes() > 0:
                # Find root nodes (comments with no incoming edges)
                root_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]

                # Calculate average reply depth
                depths = []
                for root in root_nodes:
                    # BFS to find max depth from this root
                    try:
                        # Get all nodes reachable from this root
                        reachable = nx.descendants(G, root)
                        if reachable:
                            # Calculate shortest path lengths
                            lengths = nx.single_source_shortest_path_length(G, root)
                            max_depth = max(lengths.values())
                            depths.append(max_depth)
                        else:
                            depths.append(0)  # No replies
                    except:
                        depths.append(0)

                avg_reply_depth = np.mean(depths) if depths else 0.0

                # Additional metrics
                num_roots = len(root_nodes)
                num_replies = G.number_of_edges()
                reply_rate = num_replies / G.number_of_nodes() if G.number_of_nodes() > 0 else 0

                vitality_results[video_id] = {
                    'avg_reply_depth': avg_reply_depth,
                    'num_comments': G.number_of_nodes(),
                    'num_replies': num_replies,
                    'reply_rate': reply_rate,
                    'num_threads': num_roots
                }
            else:
                vitality_results[video_id] = {
                    'avg_reply_depth': 0.0,
                    'num_comments': 0,
                    'num_replies': 0,
                    'reply_rate': 0.0,
                    'num_threads': 0
                }

        # Statistics
        avg_depths = [v['avg_reply_depth'] for v in vitality_results.values()]

        print(f"\n📊 Community Vitality Statistics:")
        print(f"  Videos analyzed: {len(vitality_results)}")
        print(f"  Mean reply depth: {np.mean(avg_depths):.3f}")
        print(f"  Median reply depth: {np.median(avg_depths):.3f}")
        print(f"  Max reply depth: {np.max(avg_depths):.3f}")
        print(f"\n  Top 5 videos by reply depth:")
        sorted_videos = sorted(vitality_results.items(),
                               key=lambda x: x[1]['avg_reply_depth'],
                               reverse=True)[:5]
        for video_id, metrics in sorted_videos:
            print(f"    {video_id}: depth={metrics['avg_reply_depth']:.2f}, "
                  f"threads={metrics['num_threads']}, replies={metrics['num_replies']}")

        # Return only avg_reply_depth
        return {vid: metrics['avg_reply_depth'] for vid, metrics in vitality_results.items()}

    def calculate_controversy_score(
        self,
        comments_df: pd.DataFrame,
        method: str = 'auto'
    ) -> Dict[str, float]:
        """
        Calculate controversy index using sentiment analysis and polarization.

        Methods:
        - 'transformer': Use Hugging Face sentiment model (if available)
        - 'keyword': Use keyword-based fallback method
        - 'auto': Use transformer if available, else keyword

        Args:
            comments_df: DataFrame with 'text' and 'video_id' columns
            method: Analysis method ('transformer', 'keyword', or 'auto')

        Returns:
            Dictionary mapping video_id to controversy_score (0-1)
        """
        print("\n" + "="*80)
        print("4️⃣ Calculating Controversy Index")
        print("="*80)

        # Determine method
        use_transformer = (
            method == 'transformer' or
            (method == 'auto' and self.sentiment_analyzer is not None)
        )

        if use_transformer and self.sentiment_analyzer is not None:
            print("Using transformer-based sentiment analysis...")
            return self._calculate_controversy_transformer(comments_df)
        else:
            print("Using keyword-based sentiment analysis...")
            return self._calculate_controversy_keyword(comments_df)

    def _calculate_controversy_transformer(self, comments_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate controversy using transformer sentiment model."""

        controversy_results = {}

        for video_id in comments_df['video_id'].unique():
            video_comments = comments_df[comments_df['video_id'] == video_id].copy()

            # Analyze sentiment for each comment
            texts = video_comments['text'].tolist()

            # Batch process (max 100 at a time to avoid memory issues)
            batch_size = 100
            all_sentiments = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                try:
                    results = self.sentiment_analyzer(batch)
                    all_sentiments.extend(results)
                except Exception as e:
                    print(f"  ⚠️ Error processing batch for {video_id}: {e}")
                    # Fill with neutral sentiment
                    all_sentiments.extend([{'label': 'NEUTRAL', 'score': 0.5}] * len(batch))

            # Extract sentiment scores (-1 to 1 range)
            sentiment_scores = []
            for result in all_sentiments:
                if result['label'] == 'POSITIVE':
                    sentiment_scores.append(result['score'])
                else:  # NEGATIVE
                    sentiment_scores.append(-result['score'])

            # Calculate polarization (variance of sentiment)
            if len(sentiment_scores) > 1:
                sentiment_variance = np.var(sentiment_scores)
                # Normalize to 0-1 range (variance of uniform -1 to 1 is 0.333)
                controversy_score = min(sentiment_variance / 0.333, 1.0)
            else:
                controversy_score = 0.0

            controversy_results[video_id] = controversy_score

        # Statistics
        print(f"\n📊 Controversy Statistics (Transformer):")
        print(f"  Videos analyzed: {len(controversy_results)}")
        print(f"  Mean controversy: {np.mean(list(controversy_results.values())):.3f}")
        print(f"  Median controversy: {np.median(list(controversy_results.values())):.3f}")
        print(f"\n  Top 5 most controversial videos:")
        sorted_videos = sorted(controversy_results.items(), key=lambda x: x[1], reverse=True)[:5]
        for video_id, score in sorted_videos:
            print(f"    {video_id}: {score:.3f}")

        return controversy_results

    def _calculate_controversy_keyword(self, comments_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate controversy using keyword-based method."""

        # Define controversy keywords
        negative_keywords = [
            'fake', 'copyright', 'uncanny', 'scary', 'creepy', 'weird',
            'stolen', 'plagiarism', 'unoriginal', 'soulless', 'lifeless',
            'terrible', 'awful', 'bad', 'hate', 'dislike', 'disappointed'
        ]

        positive_keywords = [
            'creative', 'amazing', 'awesome', 'incredible', 'beautiful',
            'love', 'great', 'fantastic', 'wonderful', 'impressive',
            'brilliant', 'perfect', 'excellent', 'stunning'
        ]

        controversy_results = {}

        for video_id in comments_df['video_id'].unique():
            video_comments = comments_df[comments_df['video_id'] == video_id].copy()

            # Count positive and negative comments
            pos_pattern = '|'.join([f'\\b{kw}\\w*\\b' for kw in positive_keywords])
            neg_pattern = '|'.join([f'\\b{kw}\\w*\\b' for kw in negative_keywords])

            video_comments['is_positive'] = video_comments['text'].str.lower().str.contains(
                pos_pattern, regex=True, na=False
            )
            video_comments['is_negative'] = video_comments['text'].str.lower().str.contains(
                neg_pattern, regex=True, na=False
            )

            num_positive = video_comments['is_positive'].sum()
            num_negative = video_comments['is_negative'].sum()
            total = len(video_comments)

            # Calculate polarization
            # High controversy = balanced positive/negative (close to 0.5 each)
            # Low controversy = dominated by one sentiment
            if total > 0:
                pos_rate = num_positive / total
                neg_rate = num_negative / total

                # Controversy is high when both rates are similar and non-zero
                # Use entropy-like measure
                if pos_rate + neg_rate > 0:
                    # Normalized to 0-1 range
                    balance = min(pos_rate, neg_rate) / max(pos_rate, neg_rate) if max(pos_rate, neg_rate) > 0 else 0
                    magnitude = pos_rate + neg_rate
                    controversy_score = balance * magnitude
                else:
                    controversy_score = 0.0
            else:
                controversy_score = 0.0

            controversy_results[video_id] = controversy_score

        # Statistics
        print(f"\n📊 Controversy Statistics (Keyword):")
        print(f"  Videos analyzed: {len(controversy_results)}")
        print(f"  Mean controversy: {np.mean(list(controversy_results.values())):.3f}")
        print(f"  Median controversy: {np.median(list(controversy_results.values())):.3f}")
        print(f"\n  Top 5 most controversial videos:")
        sorted_videos = sorted(controversy_results.items(), key=lambda x: x[1], reverse=True)[:5]
        for video_id, score in sorted_videos:
            print(f"    {video_id}: {score:.3f}")

        return controversy_results

    def calculate_all_metrics(
        self,
        comments_df: pd.DataFrame,
        videos_df: pd.DataFrame,
        output_path: str = 'output/metrics/metrics_summary.csv'
    ) -> pd.DataFrame:
        """
        Calculate all four metrics and save to CSV.

        Args:
            comments_df: Comments DataFrame
            videos_df: Videos DataFrame
            output_path: Path to save metrics summary

        Returns:
            DataFrame with all metrics per video
        """
        print("\n" + "="*80)
        print("🎯 ADVANCED METRICS CALCULATION")
        print("="*80)
        print(f"Comments: {len(comments_df)}")
        print(f"Videos: {len(videos_df)}")

        # Calculate each metric
        loyalty_rates = self.calculate_loyalty_rate(comments_df)
        engagement_indices = self.calculate_engagement_index(comments_df, videos_df)
        reply_depths = self.calculate_community_vitality(comments_df)
        controversy_scores = self.calculate_controversy_score(comments_df, method='auto')

        # Combine into single DataFrame
        all_video_ids = set(loyalty_rates.keys()) | set(engagement_indices.keys()) | \
                        set(reply_depths.keys()) | set(controversy_scores.keys())

        results = []
        for video_id in all_video_ids:
            results.append({
                'video_id': video_id,
                'loyalty_rate': loyalty_rates.get(video_id, 0.0),
                'engagement_index': engagement_indices.get(video_id, 0.0),
                'avg_reply_depth': reply_depths.get(video_id, 0.0),
                'controversy_score': controversy_scores.get(video_id, 0.0)
            })

        metrics_df = pd.DataFrame(results)

        # Add video metadata
        video_info = videos_df[['video_id', 'title', 'view_count', 'like_count', 'comment_count']].copy()
        metrics_df = metrics_df.merge(video_info, on='video_id', how='left')

        # Reorder columns
        metrics_df = metrics_df[[
            'video_id', 'title', 'view_count', 'like_count', 'comment_count',
            'loyalty_rate', 'engagement_index', 'avg_reply_depth', 'controversy_score'
        ]]

        # Save to CSV
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        metrics_df.to_csv(output_path, index=False)

        print("\n" + "="*80)
        print("✅ METRICS CALCULATION COMPLETE")
        print("="*80)
        print(f"\n📊 Summary Statistics:")
        print(metrics_df[['loyalty_rate', 'engagement_index', 'avg_reply_depth', 'controversy_score']].describe())
        print(f"\n💾 Results saved to: {output_path}")

        return metrics_df


def main():
    """Main function for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(description='Calculate advanced metrics for YouTube comments')
    parser.add_argument('--comments', required=True, help='Path to comments JSON file')
    parser.add_argument('--videos', required=True, help='Path to videos JSON file')
    parser.add_argument('--output', default='output/metrics/metrics_summary.csv',
                        help='Output CSV path')
    parser.add_argument('--gpu', action='store_true', help='Use GPU for transformers')

    args = parser.parse_args()

    # Load data
    print("Loading data...")
    comments_df = pd.read_json(args.comments)
    videos_df = pd.read_json(args.videos)

    # Calculate metrics
    calculator = AdvancedMetrics(use_gpu=args.gpu)
    results = calculator.calculate_all_metrics(
        comments_df=comments_df,
        videos_df=videos_df,
        output_path=args.output
    )

    print("\n✅ Done!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
