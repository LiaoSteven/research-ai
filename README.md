# research-ai

## 🎯 Project Overview

本研究旨在采用数字人文与数据科学方法，对 YouTube 短视频的观众评论进行深度分析。

### Research Objectives

研究核心是比较AI生成短视频与传统非AI生成短视频在以下三个维度上的显著差异：

1. **观众情绪 (Audience Sentiment)**
   - 探究两类视频引发的观众情绪倾向（积极、消极、中性）有何不同

2. **讨论主题 (Topic Preference)**
   - 识别并对比观众在不同类型视频下关注和讨论的核心话题

3. **互动模式 (Interaction Patterns)**
   - 分析评论区的互动行为（如回复、点赞）是否存在差异

### Time-Series Analysis

此外，本研究还将引入时间序列分析，追踪自2022年以来，随着生成式AI技术的爆发式发展，观众对AI相关内容的反应（情绪、主题）是如何演变的。

### Dataset

通过构建并分析一个大规模评论语料库：
- **目标规模**: 约 130 万条评论
- **Token数量**: 约 20M tokens
- **时间范围**: 2022年至今

本研究致力于揭示 AI 作为一种新兴内容创作范式对观众行为和公众舆论的深层影响。

---

## 🚀 Quick Start

1. **Read CLAUDE.md first** - Contains essential rules for Claude Code
2. Follow the pre-task compliance checklist before starting any work
3. Use proper module structure under `src/main/python/`
4. Commit after every completed task

## 📁 Project Structure

```
research-ai/
├── CLAUDE.md              # Essential rules for Claude Code
├── README.md              # Project documentation
├── .gitignore             # Git ignore patterns
├── src/                   # Source code (NEVER put files in root)
│   ├── main/
│   │   ├── python/        # Python code
│   │   │   ├── core/      # Core ML algorithms
│   │   │   ├── utils/     # Data processing utilities
│   │   │   ├── models/    # Model definitions
│   │   │   ├── services/  # ML services and pipelines
│   │   │   ├── api/       # API endpoints
│   │   │   ├── training/  # Training scripts
│   │   │   ├── inference/ # Inference code
│   │   │   └── evaluation/# Model evaluation
│   │   └── resources/     # Configuration & assets
│   └── test/              # Test code
├── data/                  # Dataset management
│   ├── raw/               # Original YouTube comments
│   ├── processed/         # Cleaned data
│   ├── external/          # External sources
│   └── temp/              # Temporary files
├── notebooks/             # Jupyter notebooks
│   ├── exploratory/       # Data exploration
│   ├── experiments/       # ML experiments
│   └── reports/           # Analysis reports
├── models/                # ML models and artifacts
│   ├── trained/           # Trained models
│   ├── checkpoints/       # Checkpoints
│   └── metadata/          # Model configs
├── experiments/           # Experiment tracking
│   ├── configs/           # Experiment configs
│   ├── results/           # Results and metrics
│   └── logs/              # Training logs
├── docs/                  # Documentation
├── tools/                 # Development tools
├── scripts/               # Automation scripts
├── examples/              # Usage examples
├── output/                # Generated output files
├── logs/                  # Log files
└── tmp/                   # Temporary files
```

## 🔧 Development Guidelines

- **Always search first** before creating new files
- **Extend existing** functionality rather than duplicating
- **Use Task agents** for operations >30 seconds
- **Single source of truth** for all functionality
- **Language-agnostic structure** - follows Python best practices
- **MLOps-ready** - supports experiment tracking and model versioning

## 🛠️ Technology Stack

- **Language**: Python 3.x
- **ML/NLP**: TBD (e.g., transformers, scikit-learn, spaCy)
- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib, seaborn, plotly
- **Experiment Tracking**: TBD (e.g., MLflow, Weights & Biases)

## 📊 Research Workflow

1. **Data Collection**: YouTube API / web scraping
2. **Data Preprocessing**: Cleaning, tokenization, normalization
3. **Sentiment Analysis**: Fine-tuned transformer models
4. **Topic Modeling**: LDA, BERTopic, or similar
5. **Interaction Analysis**: Network analysis, engagement metrics
6. **Time-Series Analysis**: Trend detection, temporal patterns
7. **Visualization & Reporting**: Interactive dashboards, academic reports

## 📝 License

TBD

## 👥 Contributors

- Research Team: TBD

---

**Template by Chang Ho Chien | HC AI 說人話channel | v1.0.0**
📺 Tutorial: https://youtu.be/8Q1bRZaHH24
