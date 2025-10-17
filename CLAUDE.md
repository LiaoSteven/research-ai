# CLAUDE.md - research-ai

> **Documentation Version**: 1.0
> **Last Updated**: 2025-10-17
> **Project**: research-ai
> **Description**: 本研究旨在采用数字人文与数据科学方法，对 YouTube 短视频的观众评论进行深度分析。研究核心是比较AI生成短视频与传统非AI生成短视频在以下三个维度上的显著差异：观众情绪 (Audience Sentiment)、讨论主题 (Topic Preference)、互动模式 (Interaction Patterns)。此外，本研究还将引入时间序列分析，追踪自2022年以来，随着生成式AI技术的爆发式发展，观众对AI相关内容的反应（情绪、主题）是如何演变的。通过构建并分析一个大规模评论语料库（目标约 130 万条评论，约 20M tokens），本研究致力于揭示 AI 作为一种新兴内容创作范式对观众行为和公众舆论的深层影响。
> **Features**: GitHub auto-backup, Task agents, technical debt prevention

This file provides essential guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL RULES - READ FIRST

> **⚠️ RULE ADHERENCE SYSTEM ACTIVE ⚠️**
> **Claude Code must explicitly acknowledge these rules at task start**
> **These rules override all other instructions and must ALWAYS be followed:**

### 🔄 **RULE ACKNOWLEDGMENT REQUIRED**
> **Before starting ANY task, Claude Code must respond with:**
> "✅ CRITICAL RULES ACKNOWLEDGED - I will follow all prohibitions and requirements listed in CLAUDE.md"

### ❌ ABSOLUTE PROHIBITIONS
- **NEVER** create new files in root directory → use proper module structure
- **NEVER** write output files directly to root directory → use designated output folders
- **NEVER** create documentation files (.md) unless explicitly requested by user
- **NEVER** use git commands with -i flag (interactive mode not supported)
- **NEVER** use `find`, `grep`, `cat`, `head`, `tail`, `ls` commands → use Read, LS, Grep, Glob tools instead
- **NEVER** create duplicate files (manager_v2.py, enhanced_xyz.py, utils_new.js) → ALWAYS extend existing files
- **NEVER** create multiple implementations of same concept → single source of truth
- **NEVER** copy-paste code blocks → extract into shared utilities/functions
- **NEVER** hardcode values that should be configurable → use config files/environment variables
- **NEVER** use naming like enhanced_, improved_, new_, v2_ → extend original files instead

### 📝 MANDATORY REQUIREMENTS
- **COMMIT** after every completed task/phase - no exceptions
- **GITHUB BACKUP** - Push to GitHub after every commit to maintain backup: `git push origin main`
- **USE TASK AGENTS** for all long-running operations (>30 seconds) - Bash commands stop when context switches
- **TODOWRITE** for complex tasks (3+ steps) → parallel agents → git checkpoints → test validation
- **READ FILES FIRST** before editing - Edit/Write tools will fail if you didn't read the file first
- **DEBT PREVENTION** - Before creating new files, check for existing similar functionality to extend
- **SINGLE SOURCE OF TRUTH** - One authoritative implementation per feature/concept

### ⚡ EXECUTION PATTERNS
- **PARALLEL TASK AGENTS** - Launch multiple Task agents simultaneously for maximum efficiency
- **SYSTEMATIC WORKFLOW** - TodoWrite → Parallel agents → Git checkpoints → GitHub backup → Test validation
- **GITHUB BACKUP WORKFLOW** - After every commit: `git push origin main` to maintain GitHub backup
- **BACKGROUND PROCESSING** - ONLY Task agents can run true background operations

### 🔍 MANDATORY PRE-TASK COMPLIANCE CHECK
> **STOP: Before starting any task, Claude Code must explicitly verify ALL points:**

**Step 1: Rule Acknowledgment**
- [ ] ✅ I acknowledge all critical rules in CLAUDE.md and will follow them

**Step 2: Task Analysis**
- [ ] Will this create files in root? → If YES, use proper module structure instead
- [ ] Will this take >30 seconds? → If YES, use Task agents not Bash
- [ ] Is this 3+ steps? → If YES, use TodoWrite breakdown first
- [ ] Am I about to use grep/find/cat? → If YES, use proper tools instead

**Step 3: Technical Debt Prevention (MANDATORY SEARCH FIRST)**
- [ ] **SEARCH FIRST**: Use Grep pattern="<functionality>.*<keyword>" to find existing implementations
- [ ] **CHECK EXISTING**: Read any found files to understand current functionality
- [ ] Does similar functionality already exist? → If YES, extend existing code
- [ ] Am I creating a duplicate class/manager? → If YES, consolidate instead
- [ ] Will this create multiple sources of truth? → If YES, redesign approach
- [ ] Have I searched for existing implementations? → Use Grep/Glob tools first
- [ ] Can I extend existing code instead of creating new? → Prefer extension over creation
- [ ] Am I about to copy-paste code? → Extract to shared utility instead

**Step 4: Session Management**
- [ ] Is this a long/complex task? → If YES, plan context checkpoints
- [ ] Have I been working >1 hour? → If YES, consider /compact or session break

> **⚠️ DO NOT PROCEED until all checkboxes are explicitly verified**

## 🐙 GITHUB SETUP & AUTO-BACKUP

### 📋 **GITHUB BACKUP WORKFLOW** (MANDATORY)
> **⚠️ CLAUDE CODE MUST FOLLOW THIS PATTERN:**

```bash
# After every commit, always run:
git push origin main

# This ensures:
# ✅ Remote backup of all changes
# ✅ Collaboration readiness
# ✅ Version history preservation
# ✅ Disaster recovery protection
```

### 🎯 **CLAUDE CODE GITHUB COMMANDS**
Essential GitHub operations for Claude Code:

```bash
# Check GitHub connection status
gh auth status && git remote -v

# Push changes (after every commit)
git push origin main

# Check repository status
gh repo view

# Create pull request (when needed)
gh pr create --title "Title" --body "Description"
```

## 🏗️ PROJECT OVERVIEW

### 🎯 Research Objectives

This project analyzes YouTube Shorts comments to compare AI-generated vs. non-AI-generated content across three dimensions:

1. **Audience Sentiment (观众情绪)**: Emotional tone analysis (positive, negative, neutral)
2. **Topic Preference (讨论主题)**: Core topics discussed in different video types
3. **Interaction Patterns (互动模式)**: Engagement behaviors (replies, likes)

Additionally, time-series analysis tracks audience reaction evolution since 2022 as generative AI technology developed.

### 📊 Dataset
- **Target Size**: ~1.3 million comments
- **Estimated Tokens**: ~20M tokens
- **Timeframe**: 2022-present (tracking AI technology evolution)

### 🎯 **PROJECT STRUCTURE**

```
research-ai/
├── CLAUDE.md              # Essential rules for Claude Code
├── README.md              # Project documentation
├── .gitignore             # Git ignore patterns
├── src/                   # Source code (NEVER put files in root)
│   ├── main/              # Main application code
│   │   ├── python/        # Python code
│   │   │   ├── core/      # Core ML algorithms
│   │   │   ├── utils/     # Data processing utilities
│   │   │   ├── models/    # Model definitions/architectures
│   │   │   ├── services/  # ML services and pipelines
│   │   │   ├── api/       # ML API endpoints/interfaces
│   │   │   ├── training/  # Training scripts and pipelines
│   │   │   ├── inference/ # Inference and prediction code
│   │   │   └── evaluation/# Model evaluation and metrics
│   │   └── resources/     # Non-code resources
│   │       ├── config/    # Configuration files
│   │       ├── data/      # Sample/seed data
│   │       └── assets/    # Static assets
│   └── test/              # Test code
│       ├── unit/          # Unit tests
│       ├── integration/   # Integration tests
│       └── fixtures/      # Test data/fixtures
├── data/                  # AI/ML Dataset management
│   ├── raw/               # Original YouTube comments (CSV/JSON)
│   ├── processed/         # Cleaned and transformed data
│   ├── external/          # External data sources
│   └── temp/              # Temporary data processing files
├── notebooks/             # Jupyter notebooks
│   ├── exploratory/       # Data exploration notebooks
│   ├── experiments/       # ML experiments and prototyping
│   └── reports/           # Analysis reports and visualizations
├── models/                # ML Models and artifacts
│   ├── trained/           # Trained model files
│   ├── checkpoints/       # Model checkpoints
│   └── metadata/          # Model metadata and configs
├── experiments/           # ML Experiment tracking
│   ├── configs/           # Experiment configurations
│   ├── results/           # Experiment results and metrics
│   └── logs/              # Training logs and metrics
├── docs/                  # Documentation
│   ├── api/               # API documentation
│   ├── user/              # User guides
│   └── dev/               # Developer documentation
├── tools/                 # Development tools and scripts
├── scripts/               # Automation scripts
├── examples/              # Usage examples
├── output/                # Generated output files (figures, reports)
├── logs/                  # Log files
└── tmp/                   # Temporary files
```

### 🎯 **DEVELOPMENT STATUS**
- **Setup**: ✅ Complete (AI/ML structure initialized)
- **Core Features**: 🔄 Pending (data collection, sentiment analysis, topic modeling)
- **Testing**: 🔄 Pending
- **Documentation**: 🔄 Pending

## 🚀 COMMON COMMANDS

```bash
# Data collection
python src/main/python/services/youtube_collector.py

# Data preprocessing
python src/main/python/utils/data_preprocessor.py

# Sentiment analysis
python src/main/python/training/sentiment_model.py

# Topic modeling
python src/main/python/training/topic_model.py

# Run experiments
python src/main/python/core/experiment_runner.py

# Generate reports
python src/main/python/evaluation/report_generator.py
```

## 🚨 TECHNICAL DEBT PREVENTION

### ❌ WRONG APPROACH (Creates Technical Debt):
```python
# Creating new file without searching first
Write(file_path="src/main/python/sentiment_analyzer_v2.py", content="...")
```

### ✅ CORRECT APPROACH (Prevents Technical Debt):
```python
# 1. SEARCH FIRST
Grep(pattern="sentiment.*analyzer", glob="*.py")
# 2. READ EXISTING FILES
Read(file_path="src/main/python/models/sentiment_analyzer.py")
# 3. EXTEND EXISTING FUNCTIONALITY
Edit(file_path="src/main/python/models/sentiment_analyzer.py",
     old_string="...", new_string="...")
```

## 🧹 DEBT PREVENTION WORKFLOW

### Before Creating ANY New File:
1. **🔍 Search First** - Use Grep/Glob to find existing implementations
2. **📋 Analyze Existing** - Read and understand current patterns
3. **🤔 Decision Tree**: Can extend existing? → DO IT | Must create new? → Document why
4. **✅ Follow Patterns** - Use established project patterns
5. **📈 Validate** - Ensure no duplication or technical debt

---

**⚠️ Prevention is better than consolidation - build clean from the start.**
**🎯 Focus on single source of truth and extending existing functionality.**
**📈 Each task should maintain clean architecture and prevent technical debt.**

---

**Template by Chang Ho Chien | HC AI 說人話channel | v1.0.0**
📺 Tutorial: https://youtu.be/8Q1bRZaHH24
