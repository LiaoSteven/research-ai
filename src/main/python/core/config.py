"""
Configuration Management Module

Handles loading and accessing project configuration from YAML files and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for research-ai project."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to YAML config file. If None, uses default location.
        """
        # Load environment variables
        load_dotenv()

        # Determine config file path
        if config_path is None:
            config_path = self._get_default_config_path()

        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _get_default_config_path(self) -> Path:
        """Get default configuration file path."""
        # Navigate from this file to config directory
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent.parent
        return project_root / "src" / "main" / "resources" / "config" / "config.yaml"

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

        # Replace environment variable placeholders
        self._substitute_env_vars(self._config)

    def _substitute_env_vars(self, config_dict: Dict[str, Any]) -> None:
        """
        Recursively substitute environment variable placeholders.

        Args:
            config_dict: Dictionary to process (modified in-place)
        """
        for key, value in config_dict.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                config_dict[key] = os.getenv(env_var, value)
            elif isinstance(value, dict):
                self._substitute_env_vars(value)

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key_path: Configuration key path (e.g., 'youtube.api_key')
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            >>> config = Config()
            >>> api_key = config.get('youtube.api_key')
            >>> batch_size = config.get('sentiment.batch_size', 32)
        """
        keys = key_path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_youtube_config(self) -> Dict[str, Any]:
        """Get YouTube API configuration."""
        return self._config.get('youtube', {})

    def get_sentiment_config(self) -> Dict[str, Any]:
        """Get sentiment analysis configuration."""
        return self._config.get('sentiment', {})

    def get_topic_modeling_config(self) -> Dict[str, Any]:
        """Get topic modeling configuration."""
        return self._config.get('topic_modeling', {})

    def get_preprocessing_config(self) -> Dict[str, Any]:
        """Get preprocessing configuration."""
        return self._config.get('preprocessing', {})

    @property
    def youtube_api_key(self) -> str:
        """Get YouTube API key from environment or config."""
        return self.get('youtube.api_key', '')

    @property
    def output_dir(self) -> Path:
        """Get output directory path."""
        output_dir = self.get('output.base_dir', 'output')
        return Path(output_dir)

    def __repr__(self) -> str:
        return f"Config(config_path='{self.config_path}')"


# Global config instance (lazy loaded)
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get global configuration instance.

    Args:
        config_path: Optional path to config file

    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None or config_path is not None:
        _config_instance = Config(config_path)
    return _config_instance
