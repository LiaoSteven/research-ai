"""
Sentiment Analysis Model

Analyzes sentiment (positive, negative, neutral) of YouTube comments.
Supports multiple backends: transformers, simple rule-based, or pre-trained models.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from enum import Enum

import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)


class SentimentLabel(Enum):
    """Sentiment classification labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SentimentAnalyzer:
    """
    Sentiment analyzer for Chinese text (YouTube comments).

    Supports multiple backends:
    - 'transformers': Hugging Face transformers (BERT-based models)
    - 'simple': Simple rule-based approach (for testing)
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        backend: str = 'transformers',
        device: str = 'cpu',
        batch_size: int = 32,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize sentiment analyzer.

        Args:
            model_name: Model name or path (for transformers backend)
            backend: Backend to use ('transformers' or 'simple')
            device: Device for computation ('cpu' or 'cuda')
            batch_size: Batch size for inference
            config: Optional configuration dictionary

        Example:
            >>> analyzer = SentimentAnalyzer(backend='transformers')
            >>> result = analyzer.analyze("这个视频太棒了！")
            >>> print(result['sentiment'])  # 'positive'
        """
        from ..core.config import get_config

        self.config = config or get_config().get_sentiment_config()
        self.backend = backend
        self.device = device
        self.batch_size = batch_size
        self.model_name = model_name or self.config.get('model_name', 'bert-base-chinese')

        self.model = None
        self.tokenizer = None

        if backend == 'transformers':
            self._initialize_transformers()
        elif backend == 'simple':
            self._initialize_simple()
        else:
            raise ValueError(f"Unknown backend: {backend}. Choose 'transformers' or 'simple'")

        logger.info(f"SentimentAnalyzer initialized with backend: {backend}")

    def _initialize_transformers(self) -> None:
        """Initialize transformers-based model."""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            logger.info(f"Loading model: {self.model_name}")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

            # Move model to device
            if self.device == 'cuda' and torch.cuda.is_available():
                self.model = self.model.cuda()
                logger.info("Using CUDA for inference")
            else:
                self.device = 'cpu'
                logger.info("Using CPU for inference")

            self.model.eval()

        except ImportError:
            logger.error("Transformers library not available. Install with: pip install transformers torch")
            raise
        except Exception as e:
            logger.error(f"Error initializing transformers model: {e}")
            raise

    def _initialize_simple(self) -> None:
        """Initialize simple rule-based sentiment analyzer."""
        # Simplified Chinese sentiment lexicon
        self.positive_words = {
            '好', '棒', '赞', '喜欢', '爱', '优秀', '精彩', '完美', '厉害',
            '牛', '强', '美', '帅', '漂亮', '可爱', '有趣', '搞笑', '感动'
        }

        self.negative_words = {
            '差', '烂', '讨厌', '恶心', '垃圾', '无聊', '糟糕', '失望',
            '难看', '丑', '假', '骗', '坑', '傻', '蠢', '弱'
        }

        logger.info("Simple rule-based sentiment analyzer initialized")

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a single text.

        Args:
            text: Input text

        Returns:
            Dictionary with sentiment label and confidence score

        Example:
            >>> result = analyzer.analyze("这个视频真的很棒！")
            >>> print(result)
            {'sentiment': 'positive', 'confidence': 0.95, 'scores': {...}}
        """
        if not text or not isinstance(text, str):
            return {
                'sentiment': SentimentLabel.NEUTRAL.value,
                'confidence': 0.0,
                'scores': {}
            }

        if self.backend == 'transformers':
            return self._analyze_with_transformers(text)
        elif self.backend == 'simple':
            return self._analyze_with_simple(text)

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment of multiple texts.

        Args:
            texts: List of input texts

        Returns:
            List of sentiment analysis results

        Example:
            >>> texts = ["很好", "不好", "一般"]
            >>> results = analyzer.analyze_batch(texts)
        """
        if self.backend == 'transformers':
            return self._analyze_batch_with_transformers(texts)
        else:
            return [self.analyze(text) for text in texts]

    def _analyze_with_transformers(self, text: str) -> Dict[str, Any]:
        """Analyze using transformers model."""
        try:
            import torch

            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                truncation=True,
                max_length=512,
                padding=True
            )

            if self.device == 'cuda':
                inputs = {k: v.cuda() for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
                predicted_class = torch.argmax(probs, dim=-1).item()
                confidence = probs[0][predicted_class].item()

            # Map class index to sentiment label
            # Note: This mapping depends on the specific model
            # Adjust based on your model's label mapping
            label_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
            sentiment = label_map.get(predicted_class, 'neutral')

            return {
                'sentiment': sentiment,
                'confidence': float(confidence),
                'scores': {
                    'negative': float(probs[0][0]),
                    'neutral': float(probs[0][1]) if probs.shape[1] > 1 else 0.0,
                    'positive': float(probs[0][2]) if probs.shape[1] > 2 else 0.0,
                }
            }

        except Exception as e:
            logger.error(f"Error in transformers analysis: {e}")
            return {
                'sentiment': SentimentLabel.NEUTRAL.value,
                'confidence': 0.0,
                'scores': {},
                'error': str(e)
            }

    def _analyze_batch_with_transformers(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze batch using transformers model."""
        try:
            import torch

            results = []

            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]

                inputs = self.tokenizer(
                    batch,
                    return_tensors='pt',
                    truncation=True,
                    max_length=512,
                    padding=True
                )

                if self.device == 'cuda':
                    inputs = {k: v.cuda() for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits
                    probs = torch.nn.functional.softmax(logits, dim=-1)
                    predicted_classes = torch.argmax(probs, dim=-1)

                # Process results
                label_map = {0: 'negative', 1: 'neutral', 2: 'positive'}

                for j, pred_class in enumerate(predicted_classes):
                    pred_class_idx = pred_class.item()
                    confidence = probs[j][pred_class_idx].item()
                    sentiment = label_map.get(pred_class_idx, 'neutral')

                    results.append({
                        'sentiment': sentiment,
                        'confidence': float(confidence),
                        'scores': {
                            'negative': float(probs[j][0]),
                            'neutral': float(probs[j][1]) if probs.shape[1] > 1 else 0.0,
                            'positive': float(probs[j][2]) if probs.shape[1] > 2 else 0.0,
                        }
                    })

            return results

        except Exception as e:
            logger.error(f"Error in batch transformers analysis: {e}")
            return [{'sentiment': 'neutral', 'confidence': 0.0, 'scores': {}, 'error': str(e)} for _ in texts]

    def _analyze_with_simple(self, text: str) -> Dict[str, Any]:
        """Analyze using simple rule-based approach."""
        positive_count = sum(1 for word in self.positive_words if word in text)
        negative_count = sum(1 for word in self.negative_words if word in text)

        total = positive_count + negative_count

        if total == 0:
            sentiment = SentimentLabel.NEUTRAL.value
            confidence = 0.5
        elif positive_count > negative_count:
            sentiment = SentimentLabel.POSITIVE.value
            confidence = positive_count / total
        elif negative_count > positive_count:
            sentiment = SentimentLabel.NEGATIVE.value
            confidence = negative_count / total
        else:
            sentiment = SentimentLabel.NEUTRAL.value
            confidence = 0.5

        return {
            'sentiment': sentiment,
            'confidence': float(confidence),
            'scores': {
                'positive': positive_count / max(total, 1),
                'negative': negative_count / max(total, 1),
                'neutral': 0.5 if total == 0 else 0.0
            }
        }

    def analyze_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str = 'text_clean',
        output_column_prefix: str = 'sentiment'
    ) -> pd.DataFrame:
        """
        Analyze sentiment for a DataFrame of comments.

        Args:
            df: Input DataFrame
            text_column: Column name containing text to analyze
            output_column_prefix: Prefix for output columns

        Returns:
            DataFrame with sentiment analysis results

        Example:
            >>> df_with_sentiment = analyzer.analyze_dataframe(df, text_column='text')
        """
        logger.info(f"Analyzing sentiment for {len(df)} comments")

        texts = df[text_column].fillna('').tolist()
        results = self.analyze_batch(texts)

        df[f'{output_column_prefix}_label'] = [r['sentiment'] for r in results]
        df[f'{output_column_prefix}_confidence'] = [r['confidence'] for r in results]
        df[f'{output_column_prefix}_positive'] = [r['scores'].get('positive', 0) for r in results]
        df[f'{output_column_prefix}_negative'] = [r['scores'].get('negative', 0) for r in results]
        df[f'{output_column_prefix}_neutral'] = [r['scores'].get('neutral', 0) for r in results]

        logger.info("Sentiment analysis complete")

        return df

    def get_sentiment_distribution(self, df: pd.DataFrame, sentiment_column: str = 'sentiment_label') -> Dict[str, int]:
        """
        Get sentiment distribution from analyzed DataFrame.

        Args:
            df: DataFrame with sentiment analysis results
            sentiment_column: Column name containing sentiment labels

        Returns:
            Dictionary with sentiment counts
        """
        return df[sentiment_column].value_counts().to_dict()
