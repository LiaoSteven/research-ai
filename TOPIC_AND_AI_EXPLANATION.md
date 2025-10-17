# 主题标签和 AI vs 非AI 说明文档

**日期**: 2025-10-17
**问题**: 为什么主题是数字？AI和非AI看不出来？

---

## 问题1: 为什么主题是 0, 1, 2, 3, 4？✅ 已解决

### 原因

**LDA（主题建模算法）只能识别统计模式，不能自动命名主题。**

- 算法自动将评论分成5组（主题 0-4）
- 每组有相似的词汇模式
- 但算法**不知道**这些主题是关于什么的
- 需要人工分析关键词后命名

### 解决方案 ✅

**已创建**: `scripts/label_topics.py` - 主题标签工具

根据关键词分析，给每个主题赋予了有意义的名称：

| 主题ID | 原名称 | 新名称（中文） | 新名称（英文） | 描述 |
|-------|--------|---------------|---------------|------|
| 0 | Topic 0 | **Destiny游戏讨论** | Destiny Game Discussion | Destiny游戏、账号、升级 |
| 1 | Topic 1 | **游戏与宝可梦** | Gaming & Pokemon | 游戏讨论、宝可梦、僵尸模式 |
| 2 | Topic 2 | **Cazzu音乐与文化** | Cazzu Music & Culture | Cazzu歌手、音乐、西班牙语内容 |
| 3 | Topic 3 | **游戏技术讨论** | Gaming Technical | 技术讨论、时间戳、特定玩家 |
| 4 | Topic 4 | **通用互动讨论** | General Engagement | 混合讨论，互动度最高 |

### 如何使用带标签的数据

```bash
# 1. 运行标签工具（已运行）
python scripts/label_topics.py \
  --input data/processed/comments_sentiment_topics.csv \
  --output data/processed/comments_labeled_topics.csv

# 2. 查看带标签的报告
cat data/output/reports/topic_analysis_labeled_report.txt

# 3. 使用带标签的数据进行分析
python analyze.py --input data/processed/comments_labeled_topics.csv
```

### 关键发现

**主题特征分析**:

1. **Destiny游戏讨论** (18.6%)
   - 关键词: account, foltyn, destiny, upgrade
   - 平均点赞: 2.04
   - 情感: 82.6% 中性

2. **游戏与宝可梦** (19.1%)
   - 关键词: pokemon, game, zombies, better
   - 平均点赞: 0.42
   - 情感: 78.2% 中性

3. **Cazzu音乐与文化** (15.0%)
   - 关键词: cazzu, music, hermosa, mujer
   - 平均点赞: 0.49
   - 情感: 70.8% 中性，**25.4% 积极**（最高）

4. **游戏技术讨论** (11.2%)
   - 关键词: josh, jandel, omega, owner
   - 平均点赞: 0.22
   - 情感: 86.6% 中性（最高）

5. **通用互动讨论** (36.0%) ⭐ **最大主题**
   - 关键词: this, like, game, looks, people
   - 平均点赞: **5.91**（最高）
   - 情感: **28.6% 积极**

---

## 问题2: AI 和 非AI 看不出来？❌ 数据中没有

### 原因

**当前的1000条评论数据没有 AI vs 非AI 标签！**

#### 为什么没有？

1. **数据来源**:
   - 这1000条评论是从**热门视频**（trending）采集的
   - 使用的工具: `collect_trending.py`
   - 这个工具**不检测** AI 内容

2. **缺少的字段**:
   - 没有 `video_type` 字段（ai_generated / non_ai）
   - 没有 `ai_confidence` 字段（AI检测置信度）
   - 没有 `ai_indicators` 字段（AI指标）

3. **对比分析需要的数据**:
   ```
   需要两组数据:
   ├── AI 生成视频的评论
   │   └── video_type = "ai_generated"
   └── 非AI 视频的评论
       └── video_type = "non_ai"
   ```

### 解决方案

#### 方案1: 采集新的 AI vs 非AI 对比数据（推荐）⭐

使用专门的对比采集器：

```bash
# 自动采集 AI vs 非AI 两组数据
python collect_ai_comparison.py \
  --ai-comments 1000 \
  --non-ai-comments 1000 \
  --per-video 50 \
  --threshold 0.3

# 这将生成:
# data/raw/comments_ai_generated_*.json
# data/raw/comments_non_ai_*.json
```

**特点**:
- ✅ 自动搜索 AI 相关视频
- ✅ 自动验证视频类型（使用AI检测器）
- ✅ 自动标记 `video_type` 字段
- ✅ 自动添加 `ai_confidence` 置信度

#### 方案2: 检测现有视频是否为 AI 内容

对已采集的20个视频进行 AI 检测：

```bash
# Step 1: 提取视频ID列表
python -c "
import pandas as pd
df = pd.read_csv('data/processed/comments_labeled_topics.csv')
video_ids = df['video_id'].unique()
with open('video_ids.txt', 'w') as f:
    for vid in video_ids:
        f.write(vid + '\n')
"

# Step 2: 批量检测
python detect_ai_content.py --file video_ids.txt --verbose

# Step 3: 根据结果手动标注
# (但这批视频可能都不是 AI 内容)
```

**局限性**:
- ⚠️ 这批热门视频可能**都不是 AI 内容**
- ⚠️ 无法进行真正的对比分析
- ⚠️ 需要重新采集数据

#### 方案3: 使用小规模测试数据

快速测试 AI 对比流程：

```bash
# 采集少量数据进行测试
python collect_ai_comparison.py \
  --ai-comments 100 \
  --non-ai-comments 100 \
  --per-video 20

# 然后运行完整分析流程
# (参考 COMPARISON_WORKFLOW.md)
```

---

## 完整的 AI vs 非AI 对比流程

### 前置条件

需要采集**带 AI 标签**的数据：

```bash
# 使用对比采集器（推荐）
python collect_ai_comparison.py \
  --ai-comments 1000 \
  --non-ai-comments 1000
```

### 完整流程（8步）

参考 `COMPARISON_WORKFLOW.md`:

```
1. 数据采集 (collect_ai_comparison.py) ✅ 生成 AI 标签
   ↓
2. 数据预处理 (preprocess_data.py)
   ↓
3. 情感分析 (run_sentiment.py)
   ↓
4. 主题建模 (run_topic_model.py)
   ↓
5. 主题标签 (label_topics.py) ✅ 新增
   ↓
6. AI vs 非AI 对比 (compare_ai_nonai.py)
   ↓
7. 时间序列分析 (analyze_time_series.py)
   ↓
8. 对比可视化 (visualize_comparison.py)
```

### 预期输出

**对比分析报告** 将包含：

1. **情感差异**
   - AI 视频: X% 积极
   - 非AI 视频: Y% 积极
   - 卡方检验: p-value = ?

2. **主题差异**
   - AI 视频主要讨论: [主题列表]
   - 非AI 视频主要讨论: [主题列表]
   - 主题分布对比图

3. **互动差异**
   - AI 视频平均点赞: X
   - 非AI 视频平均点赞: Y
   - Mann-Whitney U 检验: p-value = ?

4. **时间演变**
   - 2022-2025 AI 内容占比变化
   - 观众对 AI 内容的情感演变

---

## 数据文件对比

### 当前数据（1000条评论）

**文件**: `data/processed/comments_labeled_topics.csv`

**包含的字段**:
```
✅ video_id - 视频ID
✅ text - 评论文本
✅ like_count - 点赞数
✅ sentiment - 情感（positive/neutral/negative）
✅ topic - 主题ID（0-4）
✅ topic_name - 主题名称（英文）✅ 新增
✅ topic_name_zh - 主题名称（中文）✅ 新增
✅ topic_description - 主题描述 ✅ 新增

❌ video_type - AI vs 非AI 标签（缺失）
❌ ai_confidence - AI 检测置信度（缺失）
```

**适用于**:
- ✅ 情感分析
- ✅ 主题建模
- ✅ 互动分析
- ✅ 时间序列分析
- ❌ AI vs 非AI 对比（需要新数据）

### AI 对比数据（需要采集）

**文件**: `comments_ai_generated_*.json` 和 `comments_non_ai_*.json`

**将包含的字段**:
```
✅ video_id
✅ text
✅ like_count
✅ sentiment（分析后）
✅ topic（分析后）
✅ topic_name（分析后）
✅ video_type - "ai_generated" 或 "non_ai" ⭐
✅ ai_confidence - 0.0 到 1.0 ⭐
✅ ai_indicators - 检测到的AI指标 ⭐
```

**适用于**:
- ✅ 情感分析
- ✅ 主题建模
- ✅ 互动分析
- ✅ 时间序列分析
- ✅ **AI vs 非AI 对比** ⭐

---

## 快速行动指南

### 如果你想看主题名称 ✅ 已完成

```bash
# 查看带标签的报告
cat data/output/reports/topic_analysis_labeled_report.txt

# 或使用带标签的数据
head data/processed/comments_labeled_topics.csv
```

### 如果你想做 AI vs 非AI 对比 ⏳ 需要新数据

```bash
# Step 1: 采集 AI 对比数据（需要30-60分钟）
python collect_ai_comparison.py \
  --ai-comments 1000 \
  --non-ai-comments 1000

# Step 2: 运行完整分析流程
# 参考 COMPARISON_WORKFLOW.md

# Step 3: 生成对比报告
python scripts/compare_ai_nonai.py \
  --ai data/processed/comments_ai_sentiment_topics.csv \
  --non-ai data/processed/comments_non_ai_sentiment_topics.csv
```

---

## 总结

### 主题标签问题 ✅ 已解决

| 之前 | 现在 |
|------|------|
| Topic 0 | **Destiny游戏讨论** (Destiny Game Discussion) |
| Topic 1 | **游戏与宝可梦** (Gaming & Pokemon) |
| Topic 2 | **Cazzu音乐与文化** (Cazzu Music & Culture) |
| Topic 3 | **游戏技术讨论** (Gaming Technical) |
| Topic 4 | **通用互动讨论** (General Engagement) |

**工具**: `scripts/label_topics.py`
**输出**: `data/processed/comments_labeled_topics.csv`
**报告**: `data/output/reports/topic_analysis_labeled_report.txt`

### AI vs 非AI 对比 ⏳ 需要新数据

**现状**:
- ❌ 当前1000条评论**没有** AI 标签
- ❌ 无法直接进行 AI vs 非AI 对比

**解决方案**:
- ✅ 使用 `collect_ai_comparison.py` 采集新数据
- ✅ 按照 `COMPARISON_WORKFLOW.md` 运行分析
- ✅ 所有工具已准备好（9个脚本）

**预计时间**:
- 数据采集: 30-60分钟
- 完整分析: 10-15分钟
- 总计: ~1小时

---

## 相关文档

- `COMPARISON_WORKFLOW.md` - AI 对比完整流程
- `AI_DETECTION_GUIDE.md` - AI 检测详细说明
- `REPORTS_GENERATED.md` - 当前报告清单
- `PROGRESS.md` - 项目进度

---

**生成时间**: 2025-10-17 20:30
**状态**: 主题标签✅完成，AI对比⏳待数据

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
