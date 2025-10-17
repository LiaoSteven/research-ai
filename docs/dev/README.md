# 开发者指南

> **版本**: 1.0
> **最后更新**: 2025-10-17
> **项目**: research-ai

本目录包含项目开发相关的技术文档，帮助开发者快速上手并遵循最佳实践。

---

## 📚 文档索引

### 1. [环境搭建](setup.md) 🔄 待完成
- 系统要求
- Python 环境配置
- 依赖安装
- IDE 配置推荐

### 2. [系统架构设计](architecture.md) 🔄 待完成
- 整体架构图
- 模块划分与职责
- 数据流向
- 技术选型说明

### 3. [数据处理流程](data_pipeline.md) 🔄 待完成
- 数据采集流程
- 数据清洗步骤
- 数据存储策略
- ETL 管道设计

### 4. [机器学习模型文档](ml_models.md) 🔄 待完成
- 模型架构说明
- 训练流程
- 超参数调优
- 模型评估指标

### 5. [代码规范](coding_standards.md) 🔄 待完成
- Python 代码风格（PEP 8）
- 命名约定
- 注释规范
- 类型注解

### 6. [贡献指南](contributing.md) 🔄 待完成
- 分支策略
- 提交信息规范
- Pull Request 流程
- 代码审查标准

---

## 🏗️ 项目架构概览

```
研究项目架构
├── 数据层 (Data Layer)
│   ├── YouTube API 数据采集
│   ├── 数据存储 (raw/processed)
│   └── 数据验证与质量控制
│
├── 处理层 (Processing Layer)
│   ├── 数据清洗与预处理
│   ├── 特征工程
│   └── 数据转换
│
├── 模型层 (Model Layer)
│   ├── 情感分析模型
│   ├── 主题建模
│   └── 互动模式分析
│
├── 分析层 (Analysis Layer)
│   ├── 统计分析
│   ├── 时间序列分析
│   └── 可视化
│
└── 服务层 (Service Layer)
    ├── API 服务
    ├── 批处理任务
    └── 实验管理
```

---

## 🚀 快速开始

### 环境配置

```bash
# 克隆项目
git clone https://github.com/your-username/research-ai.git
cd research-ai

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥
cp .env.example .env
# 编辑 .env 文件，添加 YouTube API 密钥
```

### 运行第一个示例

```python
# TODO: 示例代码待补充
from src.main.python.services.youtube_collector import YouTubeCollector

# 初始化并测试
collector = YouTubeCollector()
print("✅ 环境配置成功！")
```

---

## 🧪 开发工作流

### 1. 任务开始前
- 查看 [CLAUDE.md](../../CLAUDE.md) 的强制性规则
- 运行 pre-task compliance check
- 搜索现有实现，避免重复代码

### 2. 开发过程中
- 遵循单一数据源原则
- 优先扩展现有文件，避免创建 v2/enhanced 版本
- 使用 Task agents 处理长时间运行任务（>30秒）

### 3. 任务完成后
- 运行测试
- 提交代码并推送到 GitHub
- 更新相关文档

---

## 🧰 开发工具

### 推荐工具
- **IDE**: VS Code / PyCharm
- **版本控制**: Git + GitHub
- **代码格式化**: black, isort
- **类型检查**: mypy
- **测试框架**: pytest
- **Notebook**: Jupyter Lab

### VS Code 扩展推荐
- Python
- Pylance
- Jupyter
- Git Graph
- GitHub Copilot (可选)

---

## 📊 技术栈

| 类别 | 技术 | 用途 |
|------|------|------|
| **语言** | Python 3.x | 主要开发语言 |
| **ML/NLP** | TBD | 机器学习与自然语言处理 |
| **数据处理** | pandas, numpy | 数据操作与分析 |
| **可视化** | matplotlib, seaborn | 数据可视化 |
| **API** | YouTube Data API v3 | 数据采集 |
| **版本控制** | Git, GitHub | 代码管理 |

---

## 🔍 代码组织原则

### 目录结构规范

```python
# ✅ 正确：使用模块化结构
src/main/python/
  ├── models/sentiment_analyzer.py
  ├── services/youtube_collector.py
  └── utils/data_cleaner.py

# ❌ 错误：在根目录创建文件
sentiment_analyzer.py  # 不要这样！
youtube_collector.py   # 不要这样！
```

### 单一数据源原则

```python
# ✅ 正确：扩展现有功能
# 文件：src/main/python/models/sentiment_analyzer.py
class SentimentAnalyzer:
    def analyze(self, text):
        # 现有实现
        pass

    def analyze_batch(self, texts):  # 新增功能
        # 新实现
        pass

# ❌ 错误：创建重复文件
# 文件：src/main/python/models/sentiment_analyzer_v2.py
# 不要创建这样的文件！
```

---

## 📝 文档更新指南

在开发过程中，请及时更新以下文档：

- **代码注释**: 关键函数和类的 docstring
- **API 文档**: 新增 API 端点时更新 [docs/api/](../api/)
- **变更日志**: 重要变更记录在 CHANGELOG.md（如有）
- **README**: 新增功能时更新项目 README

---

## 🐛 问题排查

### 常见问题
1. **API 配额超限** → 查看 YouTube API 配额管理
2. **依赖冲突** → 使用虚拟环境隔离
3. **数据格式问题** → 参考 [docs/research/data_schema.md](../research/data_schema.md)

### 获取帮助
- 查看 [用户指南](../user/troubleshooting.md)
- 提交 Issue 到 GitHub
- 查看项目 Wiki（如有）

---

## 📖 相关资源

- [CLAUDE.md](../../CLAUDE.md) - 开发规范与强制性规则
- [README.md](../../README.md) - 项目概览
- [API 文档](../api/README.md) - API 使用指南
- [研究文档](../research/README.md) - 研究方法论

---

**项目主页**: [README.md](../../README.md) | **开发规范**: [CLAUDE.md](../../CLAUDE.md)
