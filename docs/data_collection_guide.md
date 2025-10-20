# 大规模数据采集指南

## 📋 概述

本指南介绍如何采集 100,000 条 YouTube Shorts 评论数据，用于 AI vs 非AI 内容对比研究（2022-2025）。

## 🎯 采样策略

### 时间分层采样 (Temporal Stratified Sampling)

- **时间范围**: 2022年1月1日 - 2025年10月31日
- **总评论数**: 100,000 条
- **季度覆盖**: 16 个季度
- **AI/非AI 比例**: 50% / 50% (各 50,000 条)

### 关键特点

1. **均匀时间分布**: 每季度约 6,250 条评论
2. **里程碑季度加权**: 包含重大 AI 事件的季度增加 20% 采样量
3. **AI 内容检测**: 自动验证视频类型，确保标签准确性
4. **检查点机制**: 每季度自动保存进度，防止数据丢失

### 关键时间节点 ⭐

| 日期 | 事件 | 影响 |
|------|------|------|
| 2022-11-30 | ChatGPT Launch | 生成式 AI 爆发起点 |
| 2023-03-14 | GPT-4 Release | 多模态 AI 能力提升 |
| 2023-05-10 | Google Bard Launch | AI 竞争加剧 |
| 2024-02-15 | Sora Announcement | AI 视频生成技术突破 |
| 2024-05-13 | GPT-4o Release | 实时多模态交互 |

## 🚀 快速开始

### 前置要求

1. **YouTube Data API v3 密钥**
   ```bash
   # 获取 API 密钥: https://console.cloud.google.com/apis/credentials

   # 设置环境变量
   export YOUTUBE_API_KEY="your_api_key_here"

   # 或在 .env 文件中添加
   echo "YOUTUBE_API_KEY=your_api_key_here" >> .env
   ```

2. **Python 依赖**
   ```bash
   pip install google-api-python-client python-dotenv
   ```

### 第一步：预览采样计划

```bash
python3 scripts/preview_sampling_plan.py
```

**输出示例**:
```
================================================================================
 时间分层采样计划 (Temporal Stratified Sampling Plan)
================================================================================

📅 时间范围: 2022-01-01 至 2025-10-31
🎯 目标评论数: 100,000 条
📊 季度数量: 16
⚖️ AI/非AI 比例: 50% / 50%

季度         日期范围                      总数       AI       非AI      里程碑
--------------------------------------------------------------------------------
2022Q1     2022-01-01 ~ 2022-03-31   6250     3125     3125
2022Q4     2022-10-01 ~ 2022-12-31   7500     3750     3750     ⭐
...
```

### 第二步：开始采集

```bash
bash scripts/collect_100k_comments.sh
```

**预计耗时**:
- 取决于 API 配额限制
- 建议: 数小时到数天
- 自动检查点: 每季度保存一次

### 第三步：监控进度

采集过程中会显示实时进度：

```
[1/16] 采集季度: 2022Q1
================================================================================
日期: 2022-01-01 ~ 2022-03-31
目标: AI 3125 条 + 非AI 3125 条
⭐ 里程碑季度 - 重点采样
================================================================================

[1/2] 采集 AI 内容...
🔍 搜索 AI 视频...
   ✓ 找到 157 个视频
🔍 验证视频内容...
   ✓ 验证通过 125 个视频
📝 开始采集评论...
   ✓ 采集 3,125 条评论

[2/2] 采集非 AI 内容...
   ✓ 采集 3,125 条评论

✅ 2022Q1 完成: 6,250 条评论

📊 总体进度:
   已采集: 6,250 / 100,000 (6.3%)
   AI 内容: 3,125
   非 AI: 3,125
   完成季度: 1/16
```

## 📁 输出文件结构

```
data/raw/
├── comments_ai_2022-2025_20251020_123456.json          # AI 内容评论
├── comments_non_ai_2022-2025_20251020_123456.json      # 非AI 评论
├── comments_all_2022-2025_20251020_123456.json         # 全部评论
├── sampling_metadata_20251020_123456.json              # 采样元数据
├── checkpoint_2022Q1.json                              # 季度检查点
├── checkpoint_2022Q2.json
└── ...
```

### 评论数据格式

```json
{
  "comment_id": "UgxKj...",
  "video_id": "abc123",
  "text": "This AI art is amazing!",
  "author": "User123",
  "likes": 42,
  "published_at": "2023-05-15T10:30:00Z",
  "video_type": "ai_generated",
  "ai_confidence": 0.85,
  "quarter": "2023Q2",
  "year": 2023,
  "is_milestone_quarter": true
}
```

## 🔧 高级配置

### 自定义采集参数

```bash
python3 src/main/python/services/large_scale_temporal_collector.py \
    --total 50000 \                    # 目标评论数
    --start-date 2023-01-01 \          # 起始日期
    --end-date 2024-12-31 \            # 结束日期
    --checkpoint-interval 2 \          # 每2个季度保存检查点
    --output-dir data/custom           # 自定义输出目录
```

### 修改搜索关键词

编辑 `src/main/python/services/large_scale_temporal_collector.py`:

```python
AI_SEARCH_QUERIES = [
    'AI generated shorts',
    'AI art shorts',
    '你的自定义关键词'  # 添加更多关键词
]

NON_AI_SEARCH_QUERIES = [
    'vlog shorts',
    'cooking shorts',
    '你的自定义关键词'
]
```

### 调整 AI 检测阈值

```python
# 在 collect_quarter() 方法中
ai_comments, _ = self.comparison_collector.collect_with_detection(
    target_type='ai',
    max_comments=quarter_plan['ai_target'],
    per_video=20,
    region='US',
    verify_threshold=0.5  # 调整阈值 (默认 0.3)
)
```

## 📊 采集后处理流程

### 1. 数据预处理

```bash
python3 scripts/preprocess_data.py \
    --input data/raw/comments_all_2022-2025_*.json \
    --output data/processed/comments_cleaned.csv
```

### 2. 情感分析

```bash
python3 src/main/python/training/sentiment_model.py \
    --input data/processed/comments_cleaned.csv \
    --output data/processed/comments_sentiment.csv
```

### 3. 主题建模

```bash
python3 src/main/python/training/topic_model.py \
    --input data/processed/comments_sentiment.csv \
    --num-topics 10 \
    --output data/processed/comments_topics.csv
```

### 4. 时间序列分析

```bash
python3 scripts/run_time_series_analysis.py \
    --input data/processed/comments_topics.csv \
    --output output/figures/
```

### 5. AI vs 非AI 对比

```bash
python3 scripts/compare_ai_vs_nonai.py \
    --input data/processed/comments_topics.csv \
    --output output/reports/
```

## ⚠️ 注意事项

### API 配额限制

YouTube Data API v3 配额限制：
- **默认配额**: 10,000 units/day
- **评论请求**: 1 unit/request
- **搜索请求**: 100 units/request

**建议**:
1. 申请配额提升: https://support.google.com/youtube/contact/yt_api_form
2. 使用多个 API 密钥轮换
3. 分批次采集（每天采集一部分）

### 数据质量控制

1. **AI 检测准确性**:
   - 基于标题、描述、标签的关键词匹配
   - 建议人工抽查 5-10% 样本验证准确性

2. **时间范围验证**:
   - 确保视频发布时间在目标季度内
   - 检查 `published_at` 字段

3. **去重**:
   - 使用 `comment_id` 去除重复评论
   - 检查同一视频的重复采集

### 中断恢复

如果采集过程中断：

```bash
# 1. 查看已保存的检查点
ls -lh data/raw/checkpoint_*.json

# 2. 查看最后完成的季度
tail -20 data/raw/checkpoint_2023Q2.json

# 3. 修改脚本从特定季度继续
# 编辑 large_scale_temporal_collector.py
# 在 collect_all() 方法中添加 start_quarter 参数
```

## 📈 预期结果

### 最终数据集规模

- **总评论数**: ~100,000 条
- **AI 内容**: ~50,000 条
- **非 AI 内容**: ~50,000 条
- **时间跨度**: 2022-2025 (4年)
- **季度覆盖**: 16 个季度
- **预估 Tokens**: ~20M tokens

### 数据分布目标

| 年份 | 季度数 | 总评论 | AI 评论 | 非AI 评论 |
|------|--------|--------|---------|-----------|
| 2022 | 4 | 26,250 | 13,125 | 13,125 |
| 2023 | 4 | 27,500 | 13,750 | 13,750 |
| 2024 | 4 | 27,500 | 13,750 | 13,750 |
| 2025 | 4 | 25,000 | 12,500 | 12,500 |
| **总计** | **16** | **106,250** | **53,125** | **53,125** |

## 🐛 故障排除

### 问题 1: API 密钥未找到

```
❌ 错误：未找到 YouTube API 密钥
```

**解决**:
```bash
export YOUTUBE_API_KEY="your_key_here"
# 或
echo "YOUTUBE_API_KEY=your_key_here" > .env
```

### 问题 2: 配额超限

```
googleapiclient.errors.HttpError: <HttpError 403 when requesting ... returned "The request cannot be completed because you have exceeded your quota.">
```

**解决**:
1. 等待配额重置（每日 UTC 00:00）
2. 申请配额提升
3. 使用多个 API 密钥

### 问题 3: 找不到视频

```
✓ 找到 0 个视频
```

**解决**:
1. 调整搜索关键词
2. 扩大时间范围
3. 更改 `regionCode` 参数

### 问题 4: AI 检测准确率低

```
验证通过 5 个视频 (目标 100)
```

**解决**:
1. 降低 `verify_threshold` (默认 0.3)
2. 添加更多 AI 检测关键词
3. 使用更精确的搜索词

## 📚 参考资料

- [YouTube Data API v3 文档](https://developers.google.com/youtube/v3)
- [API 配额管理](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)
- [采样方法论](docs/sampling_methodology.md)
- [数据预处理指南](docs/preprocessing_guide.md)

## 🆘 获取帮助

如遇问题，请：
1. 查看日志文件: `logs/collection.log`
2. 检查检查点文件: `data/raw/checkpoint_*.json`
3. 提交 Issue: https://github.com/LiaoSteven/research-ai/issues

---

**创建日期**: 2025-10-20
**版本**: 1.0
**维护者**: Steven Liao
