"""
Topic Modeling Module

Identifies and extracts topics from YouTube comments using LDA or BERTopic.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)


class TopicModel:
    """
    Topic modeling for text data.

    Supports:
    - LDA (Latent Dirichlet Allocation)
    - BERTopic (BERT-based topic modeling)
    """

    def __init__(
        self,
        algorithm: str = 'LDA',
        n_topics: int = 10,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize topic model.

        Args:
            algorithm: Algorithm to use ('LDA' or 'BERTopic')
            n_topics: Number of topics to extract
            config: Optional configuration dictionary

        Example:
            >>> model = TopicModel(algorithm='LDA', n_topics=10)
            >>> topics = model.fit_transform(texts)
        """
        from ..core.config import get_config

        self.config = config or get_config().get_topic_modeling_config()
        self.algorithm = algorithm or self.config.get('algorithm', 'LDA')
        self.n_topics = n_topics or self.config.get('n_topics', 10)
        self.n_words_per_topic = self.config.get('n_words_per_topic', 10)

        self.model = None
        self.vectorizer = None
        self.feature_names = None

        logger.info(f"TopicModel initialized with algorithm: {self.algorithm}")

    def fit(self, texts: List[str]) -> 'TopicModel':
        """
        Fit topic model on texts.

        Args:
            texts: List of text documents

        Returns:
            Self (for method chaining)
        """
        logger.info(f"Fitting topic model on {len(texts)} documents")

        if self.algorithm == 'LDA':
            self._fit_lda(texts)
        elif self.algorithm == 'BERTopic':
            self._fit_bertopic(texts)
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")

        logger.info("Topic model fitting complete")
        return self

    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Transform texts to topic distributions.

        Args:
            texts: List of text documents

        Returns:
            Topic distribution matrix (n_documents x n_topics)
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")

        if self.algorithm == 'LDA':
            return self._transform_lda(texts)
        elif self.algorithm == 'BERTopic':
            return self._transform_bertopic(texts)

    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """
        Fit model and transform texts in one step.

        Args:
            texts: List of text documents

        Returns:
            Topic distribution matrix
        """
        self.fit(texts)
        return self.transform(texts)

    def _fit_lda(self, texts: List[str]) -> None:
        """Fit LDA model."""
        try:
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.decomposition import LatentDirichletAllocation

            # Vectorize texts
            self.vectorizer = CountVectorizer(
                max_df=self.config.get('max_df', 0.95),
                min_df=self.config.get('min_df', 5),
                max_features=self.config.get('max_features', 1000),
                token_pattern=r'[\u4e00-\u9fff]+|[a-zA-Z]+'  # Chinese + English
            )

            doc_term_matrix = self.vectorizer.fit_transform(texts)
            self.feature_names = self.vectorizer.get_feature_names_out()

            # Fit LDA
            self.model = LatentDirichletAllocation(
                n_components=self.n_topics,
                random_state=42,
                max_iter=self.config.get('max_iter', 20),
                learning_method='batch'
            )

            self.model.fit(doc_term_matrix)

        except ImportError:
            logger.error("scikit-learn is required for LDA. Install with: pip install scikit-learn")
            raise

    def _transform_lda(self, texts: List[str]) -> np.ndarray:
        """Transform texts using LDA model."""
        doc_term_matrix = self.vectorizer.transform(texts)
        return self.model.transform(doc_term_matrix)

    def _fit_bertopic(self, texts: List[str]) -> None:
        """Fit BERTopic model."""
        try:
            from bertopic import BERTopic

            self.model = BERTopic(
                nr_topics=self.n_topics,
                language='multilingual',
                calculate_probabilities=True
            )

            self.model.fit(texts)

        except ImportError:
            logger.error("BERTopic is required. Install with: pip install bertopic")
            raise

    def _transform_bertopic(self, texts: List[str]) -> np.ndarray:
        """Transform texts using BERTopic model."""
        topics, probs = self.model.transform(texts)
        return probs

    def get_topics(self) -> Dict[int, List[Tuple[str, float]]]:
        """
        Get topics with their top words.

        Returns:
            Dictionary mapping topic ID to list of (word, weight) tuples

        Example:
            >>> topics = model.get_topics()
            >>> for topic_id, words in topics.items():
            ...     print(f"Topic {topic_id}: {', '.join([w[0] for w in words[:5]])}")
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")

        if self.algorithm == 'LDA':
            return self._get_lda_topics()
        elif self.algorithm == 'BERTopic':
            return self._get_bertopic_topics()

    def _get_lda_topics(self) -> Dict[int, List[Tuple[str, float]]]:
        """Get LDA topics."""
        topics = {}

        for topic_idx, topic in enumerate(self.model.components_):
            top_indices = topic.argsort()[-self.n_words_per_topic:][::-1]
            top_words = [(self.feature_names[i], topic[i]) for i in top_indices]
            topics[topic_idx] = top_words

        return topics

    def _get_bertopic_topics(self) -> Dict[int, List[Tuple[str, float]]]:
        """Get BERTopic topics."""
        topics = {}

        for topic_id in range(self.n_topics):
            topic_words = self.model.get_topic(topic_id)
            topics[topic_id] = topic_words[:self.n_words_per_topic]

        return topics

    def print_topics(self, n_words: Optional[int] = None) -> None:
        """
        Print topics in a readable format.

        Args:
            n_words: Number of words to display per topic (default: use config)

        Example:
            >>> model.print_topics(n_words=5)
        """
        n_words = n_words or self.n_words_per_topic
        topics = self.get_topics()

        print(f"\n{'='*60}")
        print(f"Topic Model: {self.algorithm} ({self.n_topics} topics)")
        print(f"{'='*60}\n")

        for topic_id, words in topics.items():
            word_list = [f"{word}({weight:.3f})" for word, weight in words[:n_words]]
            print(f"Topic {topic_id}: {', '.join(word_list)}")

        print(f"\n{'='*60}\n")

    def analyze_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str = 'text_clean',
        output_column_prefix: str = 'topic'
    ) -> pd.DataFrame:
        """
        Perform topic modeling on a DataFrame.

        Args:
            df: Input DataFrame
            text_column: Column containing text to analyze
            output_column_prefix: Prefix for output columns

        Returns:
            DataFrame with topic assignments

        Example:
            >>> df_with_topics = model.analyze_dataframe(df)
        """
        logger.info(f"Analyzing topics for {len(df)} documents")

        texts = df[text_column].fillna('').tolist()

        # Fit and transform
        topic_distributions = self.fit_transform(texts)

        # Get dominant topic for each document
        dominant_topics = topic_distributions.argmax(axis=1)
        dominant_probs = topic_distributions.max(axis=1)

        df[f'{output_column_prefix}_id'] = dominant_topics
        df[f'{output_column_prefix}_probability'] = dominant_probs

        # Add topic distribution columns
        for i in range(self.n_topics):
            df[f'{output_column_prefix}_{i}_prob'] = topic_distributions[:, i]

        logger.info("Topic analysis complete")

        return df

    def get_topic_distribution(
        self,
        df: pd.DataFrame,
        topic_column: str = 'topic_id'
    ) -> Dict[int, int]:
        """
        Get distribution of documents across topics.

        Args:
            df: DataFrame with topic assignments
            topic_column: Column containing topic IDs

        Returns:
            Dictionary mapping topic ID to document count
        """
        return df[topic_column].value_counts().sort_index().to_dict()

    def save_model(self, model_path: str) -> None:
        """
        Save trained model to disk.

        Args:
            model_path: Path to save model
        """
        import pickle

        model_path = Path(model_path)
        model_path.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            'algorithm': self.algorithm,
            'n_topics': self.n_topics,
            'model': self.model,
            'vectorizer': self.vectorizer,
            'feature_names': self.feature_names,
            'config': self.config
        }

        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"Model saved to {model_path}")

    @classmethod
    def load_model(cls, model_path: str) -> 'TopicModel':
        """
        Load trained model from disk.

        Args:
            model_path: Path to saved model

        Returns:
            Loaded TopicModel instance
        """
        import pickle

        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)

        instance = cls(
            algorithm=model_data['algorithm'],
            n_topics=model_data['n_topics'],
            config=model_data['config']
        )

        instance.model = model_data['model']
        instance.vectorizer = model_data['vectorizer']
        instance.feature_names = model_data['feature_names']

        logger.info(f"Model loaded from {model_path}")

        return instance

    def compare_topic_distributions(
        self,
        df: pd.DataFrame,
        group_column: str,
        topic_column: str = 'topic_id'
    ) -> pd.DataFrame:
        """
        Compare topic distributions between groups (e.g., AI vs non-AI videos).

        Args:
            df: DataFrame with topic assignments
            group_column: Column to group by (e.g., 'video_type')
            topic_column: Column containing topic IDs

        Returns:
            DataFrame with topic distribution comparison

        Example:
            >>> comparison = model.compare_topic_distributions(
            ...     df, group_column='video_type', topic_column='topic_id'
            ... )
        """
        comparison = df.groupby([group_column, topic_column]).size().unstack(fill_value=0)

        # Calculate percentages
        comparison_pct = comparison.div(comparison.sum(axis=1), axis=0) * 100

        logger.info(f"Topic distribution comparison complete for {group_column}")

        return comparison_pct
