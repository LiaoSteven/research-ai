# 用户指南

> **版本**: 1.0
> **最后更新**: 2025-10-17
> **项目**: research-ai

本目录包含项目使用指南，帮助用户快速上手并充分利用系统功能。

---

## 📚 文档索引

### 1. [快速入门](quickstart.md) 🔄 待完成
- 系统概述
- 5 分钟快速体验
- 基础概念介绍
- Hello World 示例

### 2. [数据收集教程](data_collection.md) 🔄 待完成
- YouTube 视频链接准备
- 配置数据采集参数
- 运行数据收集脚本
- 查看采集结果

### 3. [分析功能使用](analysis.md) 🔄 待完成
- 情感分析使用指南
- 主题建模操作步骤
- 互动模式分析
- 时间序列分析

### 4. [可视化与报告](visualization.md) 🔄 待完成
- 生成分析图表
- 导出报告
- 交互式仪表板使用

### 5. [常见问题解决](troubleshooting.md) 🔄 待完成
- 安装问题
- API 配额问题
- 数据质量问题
- 性能优化建议

---

## 🎯 项目简介

**research-ai** 是一个用于分析 YouTube 短视频评论的研究工具。通过对比 AI 生成内容与非 AI 生成内容的观众反应，本项目致力于揭示：

- 📊 **观众情绪差异** - AI 生成视频 vs 传统视频的情感倾向
- 💬 **讨论主题偏好** - 不同类型视频引发的话题分布
- 🔄 **互动模式分析** - 评论区互动行为的差异
- ⏱️ **时间演变趋势** - 2022年以来观众反应的变化

---

## 🚀 快速开始

### 第一步：准备数据

1. **收集视频链接**
   - 准备 AI 生成短视频的 YouTube 链接列表
   - 准备对照组（非 AI 生成）短视频链接列表

2. **配置 API 密钥**
   ```bash
   # 复制配置模板
   cp .env.example .env

   # 编辑配置文件，添加 YouTube API 密钥
   # YOUTUBE_API_KEY=your_api_key_here
   ```

### 第二步：运行数据采集

```bash
# 采集评论数据
python src/main/python/services/youtube_collector.py \
  --video-list data/raw/video_links.txt \
  --output data/raw/comments.csv
```

### 第三步：运行分析

```bash
# 数据预处理
python src/main/python/utils/data_preprocessor.py

# 情感分析
python src/main/python/training/sentiment_model.py

# 主题建模
python src/main/python/training/topic_model.py

# 生成报告
python src/main/python/evaluation/report_generator.py
```

### 第四步：查看结果

分析结果将保存在：
- **图表**: `output/figures/`
- **报告**: `output/reports/`
- **数据**: `data/processed/`

---

## 📊 功能概览

### 1. 情感分析 (Sentiment Analysis)

分析评论的情感倾向（积极、消极、中性），对比 AI 生成内容与传统内容的情感分布差异。

```python
# 示例：运行情感分析
from src.main.python.models.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
result = analyzer.analyze("这个视频真是太棒了！")
print(result)  # {'sentiment': 'positive', 'score': 0.95}
```

### 2. 主题建模 (Topic Modeling)

识别评论中讨论的核心主题，揭示不同视频类型引发的话题偏好。

```python
# 示例：主题建模
from src.main.python.models.topic_model import TopicModel

model = TopicModel(n_topics=10)
topics = model.fit_transform(comments_data)
model.print_topics()
```

### 3. 互动模式分析 (Interaction Patterns)

分析评论的互动行为（回复数、点赞数、发布时间分布等）。

```python
# 示例：互动分析
from src.main.python.core.interaction_analyzer import InteractionAnalyzer

analyzer = InteractionAnalyzer()
patterns = analyzer.analyze(comments_data)
print(patterns.summary())
```

### 4. 时间序列分析 (Time-Series Analysis)

追踪 2022 年以来观众反应的演变趋势。

```python
# 示例：时间序列分析
from src.main.python.core.time_series_analyzer import TimeSeriesAnalyzer

analyzer = TimeSeriesAnalyzer()
trends = analyzer.analyze_trends(comments_data, start_date='2022-01-01')
analyzer.plot_trends()
```

---

## 🎨 数据可视化

### 生成分析图表

```bash
# 生成所有可视化图表
python src/main/python/evaluation/visualizer.py \
  --input data/processed/analysis_results.csv \
  --output output/figures/
```

### 可用图表类型
- 📊 **情感分布对比图** - AI vs 非AI 视频情感差异
- 📈 **时间序列趋势图** - 情感演变时间线
- 🗺️ **主题分布热力图** - 话题偏好可视化
- 🔗 **互动网络图** - 评论互动关系

---

## ⚙️ 配置选项

### 数据采集配置

编辑 `src/main/resources/config/collection.yaml`:

```yaml
youtube:
  api_key: ${YOUTUBE_API_KEY}
  max_comments: 100
  include_replies: true

rate_limit:
  requests_per_second: 1
  daily_quota: 10000
```

### 模型配置

编辑 `src/main/resources/config/model.yaml`:

```yaml
sentiment:
  model_name: "bert-base-chinese"
  batch_size: 32

topic_modeling:
  n_topics: 10
  algorithm: "LDA"
```

---

## 📖 使用场景示例

### 场景 1: 对比分析单个视频

```bash
# 分析单个 AI 生成视频
python scripts/analyze_single_video.py \
  --video-id "abc123" \
  --type "ai-generated"
```

### 场景 2: 批量分析视频集合

```bash
# 批量分析多个视频
python scripts/analyze_batch.py \
  --video-list data/raw/video_list.csv \
  --output data/processed/batch_results/
```

### 场景 3: 导出研究报告

```bash
# 生成学术报告
python scripts/generate_report.py \
  --format "academic" \
  --output output/reports/research_report.pdf
```

---

## 🔍 数据格式说明

### 输入数据格式

视频链接列表 (`data/raw/video_links.txt`):
```
https://youtube.com/shorts/abc123
https://youtube.com/shorts/def456
```

### 输出数据格式

评论数据 (`data/raw/comments.csv`):
```csv
video_id,comment_id,author,text,likes,published_at
abc123,xyz789,User1,很棒的视频！,10,2024-01-15T10:30:00Z
```

---

## 🆘 获取帮助

### 遇到问题？

1. 查看 [常见问题解决](troubleshooting.md)
2. 查看 [开发者指南](../dev/README.md)
3. 提交 GitHub Issue
4. 联系项目维护者

### 有用的资源

- [API 文档](../api/README.md) - 技术细节
- [研究方法论](../research/methodology.md) - 学术背景
- [YouTube API 文档](https://developers.google.com/youtube/v3) - 官方参考

---

## 💡 最佳实践

### 数据收集建议
- ✅ 合理控制 API 请求频率，避免超出配额
- ✅ 定期备份原始数据
- ✅ 记录数据采集的时间戳和参数

### 分析建议
- ✅ 先进行小规模测试，验证流程
- ✅ 对照组样本应与实验组规模相当
- ✅ 注意时间因素对结果的影响

### 结果解读
- ✅ 结合统计显著性检验
- ✅ 考虑样本偏差和局限性
- ✅ 多维度交叉验证结论

---

## 🔄 更新日志

查看 [CHANGELOG.md](../../CHANGELOG.md)（如有）了解版本更新历史。

---

**项目主页**: [README.md](../../README.md) | **开发规范**: [CLAUDE.md](../../CLAUDE.md)
