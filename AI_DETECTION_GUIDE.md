# AI 内容检测与对比采集指南

**使用 YouTube Data API v3 检测和采集 AI 生成内容**

---

## 🎯 概述

我们实现了三种方法来识别和采集 AI 生成的 YouTube 视频评论：

1. **AI 内容检测器** - 分析视频元数据判断是否为 AI 内容
2. **AI 视频采集器** - 基于关键词搜索 AI 相关视频
3. **对比采集器** - 自动采集 AI vs 非AI 两组数据

---

## 📚 已安装的 Google API 包

```bash
✓ google-api-python-client  2.184.0
✓ google-auth               2.41.1
✓ google-auth-httplib2      0.2.0
✓ google-auth-oauthlib      1.2.2   # 新安装
```

---

## 🔍 方法 1: AI 内容检测器

### 功能特性

检测器通过以下指标判断视频是否为 AI 内容：

#### 1. **官方 YouTube AI 声明** (权重最高: +50分)
检测视频描述中的官方标注，支持多语言：

**中文**:
- "此影片包含變造或合成內容"
- "此视频包含变造或合成内容"
- "AI 生成"、"人工智能生成"

**English**:
- "altered or synthetic content"
- "AI-generated"、"synthetic content"
- "created with AI"、"made with AI"

**西班牙语**:
- "contenido alterado o sintético"
- "generado por IA"

**日语**:
- "変更または合成されたコンテンツ"
- "AI生成"

#### 2. **AI 工具名称** (权重: +10分/个)
检测是否提及以下 AI 工具：
- Midjourney
- Stable Diffusion
- DALL-E / Dalle
- ChatGPT / GPT-4
- Runway
- Synthesia
- Pika Labs
- Adobe Firefly
- Leonardo AI
- 等等...

#### 3. **标题关键词** (权重: +8分/个)
检测标题中的 AI 相关词：
- "AI"、"artificial intelligence"
- "generated"、"synthetic"

#### 4. **描述关键词** (权重: +3分/个)
检测描述中的 AI 关键词

#### 5. **视频标签** (权重: +5分/个)
检测 AI 相关标签：
- "#ai"、"#aiart"
- "#generativeai"
- "#aianimation"

### 置信度计算

```
置信度 = min(总分 / 100, 1.0)

判断标准:
- 置信度 >= 0.3: 认定为 AI 内容
- 置信度 < 0.3: 认定为非 AI 内容
```

### 使用方法

```bash
# 激活环境
source venv/bin/activate

# 检测单个视频
python detect_ai_content.py VIDEO_ID --verbose

# 批量检测（从文件读取视频 ID）
python detect_ai_content.py --file video_ids.txt --verbose

# 保存结果到 JSON
python detect_ai_content.py VIDEO_ID --output results.json
```

### 示例输出

```
======================================================================
 YouTube AI 内容检测工具
======================================================================

✅ YouTube API 连接成功

📊 准备检测 1 个视频

[1/1] 检测视频: xyz123abc
   ✓ 发现官方声明: 'altered or synthetic content' (english)
   ✓ 发现 AI 工具: midjourney
   ✓ 标题包含: ai
   ✓ AI 相关标签: aiart
   🤖 AI 内容 (置信度: 0.73)

======================================================================
 检测结果统计
======================================================================

总视频数: 1
AI 内容: 1 (100.0%)
非 AI 内容: 0 (0.0%)

🤖 检测到的 AI 内容视频:

  视频 ID: xyz123abc
  标题: Amazing AI Generated Art - Midjourney Tutorial
  置信度: 0.73
  指标:
    ✓ 官方 AI 内容声明
    ✓ AI 工具: midjourney
    ✓ AI 标签: aiart, generativeai
```

---

## 🎬 方法 2: AI 视频采集器

### 搜索关键词

**AI 内容搜索词**:
- "AI generated"
- "AI art"
- "AI animation"
- "midjourney"
- "stable diffusion"
- "AI video"
- 等等...

**非 AI 内容搜索词**:
- "handmade"
- "hand drawn"
- "traditional art"
- "real footage"
- "vlog"
- 等等...

### 使用方法

```bash
# 采集 AI 生成视频评论
python collect_ai_videos.py --type ai --max-comments 1000 --verify

# 采集非 AI 视频评论（对照组）
python collect_ai_videos.py --type non_ai --max-comments 1000 --verify

# 不验证直接采集（更快但可能不准确）
python collect_ai_videos.py --type ai --max-comments 1000
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--type` | ai | 采集类型：ai 或 non_ai |
| `--max-comments` | 1000 | 总评论数 |
| `--per-video` | 50 | 每视频评论数 |
| `--region` | US | 地区代码 |
| `--verify` | False | 是否验证视频类型 |

### 输出文件

```
data/raw/comments_ai_generated_TIMESTAMP.json  # AI 内容评论
data/raw/videos_ai_generated_TIMESTAMP.json    # AI 视频信息

data/raw/comments_non_ai_TIMESTAMP.json        # 非 AI 评论
data/raw/videos_non_ai_TIMESTAMP.json          # 非 AI 视频信息
```

---

## 🔬 方法 3: 对比采集器（推荐）

### 特点

- **自动化**: 自动搜索、验证、采集
- **质量保证**: 每个视频都经过 AI 检测验证
- **对照组**: 同时采集 AI 和非 AI 两组数据
- **即用型**: 数据已标记 `video_type` 字段

### 使用方法

```bash
# 采集 AI vs 非AI 对比数据（各 500 条评论）
python collect_ai_comparison.py --ai-comments 500 --non-ai-comments 500

# 采集更大规模数据
python collect_ai_comparison.py --ai-comments 2000 --non-ai-comments 2000

# 调整检测阈值
python collect_ai_comparison.py \
  --ai-comments 1000 \
  --non-ai-comments 1000 \
  --threshold 0.4 \
  --per-video 50
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--ai-comments` | 500 | AI 内容评论数 |
| `--non-ai-comments` | 500 | 非 AI 评论数 |
| `--per-video` | 50 | 每视频评论数 |
| `--threshold` | 0.3 | AI 检测置信度阈值 |
| `--region` | US | 地区代码 |

### 工作流程

```
1. 搜索 AI 相关视频
     ↓
2. 使用检测器验证
     ↓
3. 筛选置信度 >= 0.3 的视频
     ↓
4. 采集评论 → ai_generated 数据集
     ↓
5. 搜索非 AI 视频
     ↓
6. 验证置信度 < 0.3
     ↓
7. 采集评论 → non_ai 数据集
     ↓
8. 保存两组数据
```

---

## 📊 对比分析流程

### 完整流程

```bash
# Step 1: 采集对比数据
python collect_ai_comparison.py --ai-comments 1000 --non-ai-comments 1000

# Step 2: 预处理 AI 数据
python scripts/preprocess_data.py \
  --input data/raw/comments_ai_generated_*.json \
  --output data/processed/comments_ai.csv

# Step 3: 预处理非 AI 数据
python scripts/preprocess_data.py \
  --input data/raw/comments_non_ai_*.json \
  --output data/processed/comments_non_ai.csv

# Step 4: 情感分析
python scripts/run_sentiment.py --input data/processed/comments_ai.csv
python scripts/run_sentiment.py --input data/processed/comments_non_ai.csv

# Step 5: 主题建模
python scripts/run_topic_model.py --input data/processed/comments_ai_sentiment.csv
python scripts/run_topic_model.py --input data/processed/comments_non_ai_sentiment.csv

# Step 6: 生成对比报告
python scripts/generate_comparison_report.py \
  --ai data/processed/comments_ai_sentiment_topics.csv \
  --non-ai data/processed/comments_non_ai_sentiment_topics.csv
```

---

## 📈 数据字段说明

### 原始评论数据字段

所有评论数据会自动添加以下字段：

```json
{
  "video_id": "xyz123",
  "text": "This is amazing!",
  "author": "JohnDoe",
  "like_count": 42,
  "published_at": "2025-10-17T10:00:00Z",

  // 新增字段
  "video_type": "ai_generated",      // 或 "non_ai"
  "ai_confidence": 0.75,              // AI 检测置信度
  "category": "all",
  "region": "US"
}
```

### 视频信息字段

视频元数据会包含：

```json
{
  "video_id": "xyz123",
  "title": "Amazing AI Art",
  "video_type": "ai_generated",
  "ai_confidence": 0.75,
  "ai_indicators": {
    "official_disclosure": true,
    "ai_tools_mentioned": ["midjourney"],
    "ai_keywords_in_title": ["ai"],
    "ai_tags": ["aiart"]
  },
  "view_count": 100000,
  "like_count": 5000,
  "comment_count": 500
}
```

---

## 🎯 研究应用

### 可以研究的问题

1. **情感对比**
   - AI 内容是否引起更积极/消极的情感？
   - 情感置信度是否有差异？

2. **主题差异**
   - AI vs 非AI 视频的讨论主题有何不同？
   - 哪些主题更多出现在 AI 内容下？

3. **互动模式**
   - AI 内容的点赞率、回复率是否不同？
   - 观众参与度对比

4. **时间演变**
   - 2022-2025 年观众对 AI 内容的态度变化
   - AI 技术发展对评论的影响

### 统计分析示例

```python
import pandas as pd

# 读取数据
ai_df = pd.read_csv('data/processed/comments_ai_sentiment_topics.csv')
non_ai_df = pd.read_csv('data/processed/comments_non_ai_sentiment_topics.csv')

# 情感分布对比
print("AI 内容情感分布:")
print(ai_df['sentiment'].value_counts(normalize=True))

print("\n非 AI 内容情感分布:")
print(non_ai_df['sentiment'].value_counts(normalize=True))

# 平均点赞对比
print(f"\nAI 内容平均点赞: {ai_df['like_count'].mean():.2f}")
print(f"非 AI 内容平均点赞: {non_ai_df['like_count'].mean():.2f}")

# 主题分布对比
print("\nAI 内容主题分布:")
print(ai_df['topic'].value_counts())

print("\n非 AI 内容主题分布:")
print(non_ai_df['topic'].value_counts())
```

---

## 🛠️ 故障排除

### 常见问题

**1. API 配额不足**
```
❌ API 错误: quotaExceeded
```
解决: YouTube Data API v3 每日配额 10,000 单位，等待次日重置

**2. 找不到 AI 视频**
```
❌ 没有找到视频
```
解决:
- 降低 `--threshold` 参数（如 0.2）
- 更换 `--region` 参数
- 修改搜索关键词

**3. 检测结果不准确**
```
⚠️ 置信度过低或过高
```
解决:
- 使用 `--verify` 参数手动验证
- 调整 `--threshold` 阈值
- 检查视频描述是否包含误导性关键词

---

## 📝 最佳实践

### 1. 分批采集
```bash
# 避免一次采集太多，分批进行
python collect_ai_comparison.py --ai-comments 200 --non-ai-comments 200
# 等待一段时间后继续
python collect_ai_comparison.py --ai-comments 200 --non-ai-comments 200
```

### 2. 验证质量
```bash
# 始终使用 --verify 确保数据质量
python collect_ai_videos.py --type ai --verify --max-comments 500
```

### 3. 保存中间结果
```bash
# 使用时间戳文件名，避免覆盖
# 脚本会自动生成类似: comments_ai_generated_20251017_120000.json
```

### 4. 定期备份
```bash
# 备份原始数据
cp -r data/raw data/raw_backup_$(date +%Y%m%d)
```

---

## 📚 相关文档

- `README.md` - 项目概览
- `INSTALL.md` - 安装指南
- `FILES_GENERATED.md` - 生成文件清单
- `SUMMARY.md` - 项目总结

---

## 🎓 学术引用

如果使用此工具进行研究，建议说明：

> 本研究使用 YouTube Data API v3 检测 AI 生成内容。检测方法基于多维度指标：
> 1. YouTube 官方 AI 内容声明
> 2. AI 工具名称识别（Midjourney, DALL-E 等）
> 3. 标题、描述、标签中的 AI 关键词
> 4. 综合置信度评分系统 (0-1)
>
> 置信度阈值设定为 0.3，经人工验证准确率约为 XX%（需根据实际验证结果填写）。

---

**最后更新**: 2025-10-17
**维护者**: Chang Ho Chien
**工具版本**: 1.0.0
