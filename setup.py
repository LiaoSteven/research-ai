"""
Setup script for research-ai package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="research-ai",
    version="0.1.0",
    description="YouTube Shorts Comment Analysis Research Project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Research Team",
    python_requires=">=3.8",
    package_dir={"": "src/main/python"},
    packages=find_packages(where="src/main/python"),
    install_requires=[
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.1",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "google-api-python-client>=2.100.0",
        "google-auth>=2.20.0",
        "scikit-learn>=1.3.0",
        "tqdm>=4.65.0",
        "pyarrow>=14.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
    ],
    extras_require={
        "full": [
            "torch>=2.0.0",
            "transformers>=4.30.0",
            "bertopic>=0.16.0",
            "sentence-transformers>=2.2.0",
            "prophet>=1.1.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "jupyterlab>=4.0.0",
            "ipywidgets>=8.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "research-ai-collect=scripts.collect_data:main",
            "research-ai-preprocess=scripts.preprocess_data:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
