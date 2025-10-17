# AI vs 非AI 对比分析完整工作流程

**完成度**: 85%
**最后更新**: 2025-10-17

本文档提供完整的 AI 与非AI 内容对比分析工作流程，包括数据采集、分析和可视化。

---

## 🎯 工作流程概览

```
1. 数据采集
   ↓
2. 数据预处理
   ↓
3. 情感分析
   ↓
4. 主题建模
   ↓
5. 对比分析 (AI vs 非AI)
   ↓
6. 时间序列分析
   ↓
7. 可视化与报告生成
```

---

## 📚 已完成的工具

### ✅ 数据采集工具

1. **detect_ai_content.py** - AI 内容检测器
   - 多语言支持（中文、英文、西班牙语、日语）
   - 检测官方 AI 声明
   - 识别 AI 工具名称（Midjourney, DALL-E, etc.）
   - 置信度评分系统（0-1）

2. **collect_ai_videos.py** - AI 视频采集器
   - 基于关键词搜索 AI 视频
   - 可选验证模式
   - 自动采集评论

3. **collect_ai_comparison.py** - 对比数据采集器（推荐）
   - 自动采集 AI vs 非AI 两组数据
   - 自动验证视频类型
   - 标记 video_type 和 ai_confidence

### ✅ 分析工具

4. **scripts/preprocess_data.py** - 数据预处理
   - 清洗和标准化文本
   - 过滤垃圾评论
   - 提取特征

5. **scripts/run_sentiment.py** - 情感分析
   - 多语言情感分类
   - 置信度评分
   - 支持 BERT 和规则基础方法

6. **scripts/run_topic_model.py** - 主题建模
   - LDA 主题提取
   - 多语言停用词
   - 主题分布分析

7. **scripts/compare_ai_nonai.py** - AI vs 非AI 对比
   - 统计显著性检验（卡方、t检验、Mann-Whitney U）
   - 情感分布对比
   - 互动数据对比
   - 主题差异分析

8. **scripts/analyze_time_series.py** - 时间序列分析
   - 情感演变趋势
   - 互动模式变化
   - 主题分布演变
   - 年度对比分析

9. **scripts/visualize_comparison.py** - 对比可视化
   - 情感对比图
   - 互动对比图
   - 主题对比图
   - 综合仪表板

10. **scripts/generate_report.py** - 综合报告生成
    - 数据概览
    - 情感分析
    - 主题建模
    - 关键发现

---

## 🚀 完整执行流程

### Step 1: 采集对比数据

```bash
# 方法 A: 使用自动化对比采集器（推荐）
python collect_ai_comparison.py \
  --ai-comments 1000 \
  --non-ai-comments 1000 \
  --per-video 50 \
  --threshold 0.3 \
  --region US

# 方法 B: 分别采集 AI 和非AI 数据
python collect_ai_videos.py --type ai --max-comments 1000 --verify
python collect_ai_videos.py --type non_ai --max-comments 1000 --verify
```

**输出文件**:
- `data/raw/comments_ai_generated_YYYYMMDD_HHMMSS.json`
- `data/raw/comments_non_ai_YYYYMMDD_HHMMSS.json`
- `data/raw/videos_ai_generated_YYYYMMDD_HHMMSS.json`
- `data/raw/videos_non_ai_YYYYMMDD_HHMMSS.json`

---

### Step 2: 预处理数据

```bash
# 预处理 AI 数据
python scripts/preprocess_data.py \
  --input data/raw/comments_ai_generated_20251017_120000.json \
  --output data/processed/comments_ai.csv

# 预处理非 AI 数据
python scripts/preprocess_data.py \
  --input data/raw/comments_non_ai_20251017_120000.json \
  --output data/processed/comments_non_ai.csv
```

**输出文件**:
- `data/processed/comments_ai.csv`
- `data/processed/comments_non_ai.csv`
- `data/processed/preprocessing_stats.json`

---

### Step 3: 情感分析

```bash
# AI 数据情感分析
python scripts/run_sentiment.py \
  --input data/processed/comments_ai.csv \
  --output data/processed/comments_ai_sentiment.csv

# 非AI 数据情感分析
python scripts/run_sentiment.py \
  --input data/processed/comments_non_ai.csv \
  --output data/processed/comments_non_ai_sentiment.csv
```

**输出文件**:
- `data/processed/comments_ai_sentiment.csv`
- `data/processed/comments_non_ai_sentiment.csv`
- `output/figures/sentiment_distribution.png`

---

### Step 4: 主题建模

```bash
# AI 数据主题建模
python scripts/run_topic_model.py \
  --input data/processed/comments_ai_sentiment.csv \
  --output data/processed/comments_ai_sentiment_topics.csv \
  --num-topics 5

# 非AI 数据主题建模
python scripts/run_topic_model.py \
  --input data/processed/comments_non_ai_sentiment.csv \
  --output data/processed/comments_non_ai_sentiment_topics.csv \
  --num-topics 5
```

**输出文件**:
- `data/processed/comments_ai_sentiment_topics.csv`
- `data/processed/comments_non_ai_sentiment_topics.csv`
- `models/trained/topic_model_lda.pkl`
- `output/figures/topic_distribution.png`

---

### Step 5: AI vs 非AI 对比分析

```bash
python scripts/compare_ai_nonai.py \
  --ai data/processed/comments_ai_sentiment_topics.csv \
  --non-ai data/processed/comments_non_ai_sentiment_topics.csv \
  --output output/reports
```

**输出文件**:
- `output/reports/ai_vs_nonai_comparison_YYYYMMDD_HHMMSS.txt`
- `output/reports/ai_vs_nonai_stats_YYYYMMDD_HHMMSS.json`

**分析内容**:
- ✅ 情感分布对比（卡方检验）
- ✅ 情感置信度对比（t检验）
- ✅ 互动数据对比（Mann-Whitney U 检验）
- ✅ 主题分布对比
- ✅ 文本长度对比
- ✅ 情感-主题交叉分析

---

### Step 6: 时间序列分析

```bash
# 分析 AI 内容时间演变
python scripts/analyze_time_series.py \
  --input data/processed/comments_ai_sentiment_topics.csv \
  --output output/figures

# 分析非AI 内容时间演变
python scripts/analyze_time_series.py \
  --input data/processed/comments_non_ai_sentiment_topics.csv \
  --output output/figures

# 如果有合并数据，分析整体时间趋势
python scripts/analyze_time_series.py \
  --input data/processed/comments_all_sentiment_topics.csv \
  --output output/figures
```

**输出文件**:
- `output/figures/sentiment_time_series.png` - 情感演变图
- `output/figures/engagement_time_series.png` - 互动演变图
- `output/figures/topics_time_series.png` - 主题演变图
- `output/figures/ai_content_evolution.png` - AI 内容比例演变
- `output/figures/yearly_comparison.png` - 年度对比图
- `output/figures/time_series_report_YYYYMMDD_HHMMSS.txt` - 时间序列报告
- `output/figures/time_series_stats_YYYYMMDD_HHMMSS.json` - 统计数据

**分析内容**:
- ✅ 2022-2025 情感趋势
- ✅ 互动模式变化
- ✅ 主题演变分析
- ✅ AI 内容占比变化
- ✅ 年度对比统计

---

### Step 7: 对比可视化

```bash
python scripts/visualize_comparison.py \
  --ai data/processed/comments_ai_sentiment_topics.csv \
  --non-ai data/processed/comments_non_ai_sentiment_topics.csv \
  --output output/figures
```

**输出文件**:
- `output/figures/sentiment_comparison.png` - 情感对比图（饼图+柱状图）
- `output/figures/engagement_comparison.png` - 互动对比图（4子图）
- `output/figures/topic_comparison.png` - 主题对比图
- `output/figures/comprehensive_dashboard.png` - 综合仪表板

**可视化内容**:
- ✅ 情感分布对比（饼图、柱状图）
- ✅ 点赞数对比（箱线图、直方图、小提琴图）
- ✅ 评论长度分布
- ✅ 主题分布对比
- ✅ 主题-情感交叉分析
- ✅ 综合仪表板（6个子图）

---

### Step 8: 生成综合报告

```bash
python scripts/generate_report.py \
  --input data/processed/comments_sentiment_topics.csv \
  --output output/reports
```

**输出文件**:
- `output/reports/analysis_report_YYYYMMDD_HHMMSS.txt` - 综合研究报告

---

## 📊 一键运行完整流程

创建自动化脚本 `run_full_comparison.sh`:

```bash
#!/bin/bash

echo "=========================================="
echo "AI vs 非AI 对比分析完整流程"
echo "=========================================="

# Step 1: 采集数据
echo -e "\n[1/8] 采集对比数据..."
python collect_ai_comparison.py \
  --ai-comments 1000 \
  --non-ai-comments 1000 \
  --per-video 50 \
  --threshold 0.3

# 获取最新文件名
AI_RAW=$(ls -t data/raw/comments_ai_generated_*.json | head -1)
NON_AI_RAW=$(ls -t data/raw/comments_non_ai_*.json | head -1)

# Step 2: 预处理
echo -e "\n[2/8] 预处理数据..."
python scripts/preprocess_data.py --input "$AI_RAW" --output data/processed/comments_ai.csv
python scripts/preprocess_data.py --input "$NON_AI_RAW" --output data/processed/comments_non_ai.csv

# Step 3: 情感分析
echo -e "\n[3/8] 情感分析..."
python scripts/run_sentiment.py --input data/processed/comments_ai.csv
python scripts/run_sentiment.py --input data/processed/comments_non_ai.csv

# Step 4: 主题建模
echo -e "\n[4/8] 主题建模..."
python scripts/run_topic_model.py --input data/processed/comments_ai_sentiment.csv --num-topics 5
python scripts/run_topic_model.py --input data/processed/comments_non_ai_sentiment.csv --num-topics 5

# Step 5: 对比分析
echo -e "\n[5/8] AI vs 非AI 对比分析..."
python scripts/compare_ai_nonai.py \
  --ai data/processed/comments_ai_sentiment_topics.csv \
  --non-ai data/processed/comments_non_ai_sentiment_topics.csv

# Step 6: 时间序列分析
echo -e "\n[6/8] 时间序列分析..."
python scripts/analyze_time_series.py --input data/processed/comments_ai_sentiment_topics.csv
python scripts/analyze_time_series.py --input data/processed/comments_non_ai_sentiment_topics.csv

# Step 7: 对比可视化
echo -e "\n[7/8] 生成对比可视化..."
python scripts/visualize_comparison.py \
  --ai data/processed/comments_ai_sentiment_topics.csv \
  --non-ai data/processed/comments_non_ai_sentiment_topics.csv

# Step 8: 综合报告
echo -e "\n[8/8] 生成综合报告..."
python scripts/generate_report.py --input data/processed/comments_ai_sentiment_topics.csv
python scripts/generate_report.py --input data/processed/comments_non_ai_sentiment_topics.csv

echo -e "\n=========================================="
echo "✅ 完整流程执行完成！"
echo "=========================================="
echo -e "\n📊 查看结果："
echo "  报告: output/reports/"
echo "  可视化: output/figures/"
echo "  数据: data/processed/"
```

**使用方法**:
```bash
chmod +x run_full_comparison.sh
./run_full_comparison.sh
```

---

## 📈 预期输出文件清单

### 原始数据 (data/raw/)
- comments_ai_generated_*.json
- comments_non_ai_*.json
- videos_ai_generated_*.json
- videos_non_ai_*.json

### 处理后数据 (data/processed/)
- comments_ai.csv
- comments_ai_sentiment.csv
- comments_ai_sentiment_topics.csv
- comments_non_ai.csv
- comments_non_ai_sentiment.csv
- comments_non_ai_sentiment_topics.csv
- preprocessing_stats.json

### 可视化图表 (output/figures/)
- sentiment_comparison.png
- engagement_comparison.png
- topic_comparison.png
- comprehensive_dashboard.png
- sentiment_time_series.png
- engagement_time_series.png
- topics_time_series.png
- ai_content_evolution.png
- yearly_comparison.png

### 分析报告 (output/reports/)
- ai_vs_nonai_comparison_*.txt
- ai_vs_nonai_stats_*.json
- time_series_report_*.txt
- time_series_stats_*.json
- analysis_report_*.txt

### 模型文件 (models/trained/)
- topic_model_lda.pkl
- sentiment_model.pkl (如果使用 BERT)

---

## 🔍 关键分析指标

### 1. 情感分析指标
- 积极/中性/消极情感比例
- 情感置信度
- 情感分布显著性检验（卡方检验）

### 2. 互动指标
- 平均点赞数
- 中位数点赞数
- 点赞数分布（Mann-Whitney U 检验）

### 3. 主题指标
- 主题分布
- 主题-情感交叉分析
- 主题演变趋势

### 4. 时间序列指标
- 年度趋势
- 月度变化
- 季度对比
- 2022-2025 演变轨迹

### 5. 文本特征
- 评论长度
- 词频分布
- 语言使用模式

---

## 🎯 研究问题解答

### Q1: AI 内容是否引起更积极/消极的情感？
**分析方法**:
- compare_ai_nonai.py → 情感分布对比 + 卡方检验
- visualize_comparison.py → 情感对比图

### Q2: AI vs 非AI 视频的讨论主题有何不同？
**分析方法**:
- run_topic_model.py → 主题提取
- compare_ai_nonai.py → 主题分布对比
- visualize_comparison.py → 主题对比图

### Q3: AI 内容的互动率是否不同？
**分析方法**:
- compare_ai_nonai.py → 互动数据对比 + Mann-Whitney U 检验
- visualize_comparison.py → 互动对比图（箱线图、小提琴图）

### Q4: 2022-2025 年观众对 AI 内容的态度变化？
**分析方法**:
- analyze_time_series.py → 情感/互动/主题时间演变
- visualize_comparison.py → 时间序列图

---

## 🛠️ 故障排除

### 问题 1: API 配额不足
```
❌ API 错误: quotaExceeded
```
**解决方案**: YouTube Data API v3 每日配额 10,000 单位，等待次日重置

### 问题 2: 找不到 AI 视频
```
❌ 没有找到视频或验证失败
```
**解决方案**:
- 降低 `--threshold` 参数（如 0.2）
- 更换 `--region` 参数（如 JP, KR, GB）
- 修改搜索关键词

### 问题 3: 数据文件不存在
```
❌ 找不到文件: data/processed/comments_ai.csv
```
**解决方案**: 确保按照流程顺序执行，检查上一步是否成功

### 问题 4: 依赖包缺失
```
❌ ModuleNotFoundError: No module named 'scipy'
```
**解决方案**:
```bash
source venv/bin/activate
pip install scipy matplotlib seaborn
```

---

## 📚 相关文档

- `AI_DETECTION_GUIDE.md` - AI 内容检测详细指南
- `FILES_GENERATED.md` - 已生成文件清单
- `PROGRESS.md` - 项目进度追踪
- `SUMMARY.md` - 项目总结
- `README.md` - 项目概览

---

## 📝 学术引用建议

如果使用此工作流程进行研究，建议在方法论部分说明：

> 本研究使用 YouTube Data API v3 采集 AI 生成内容和非 AI 内容的评论数据。
>
> **AI 内容识别方法**：
> 1. YouTube 官方 AI 内容声明检测
> 2. AI 工具名称识别（Midjourney, DALL-E, Stable Diffusion 等）
> 3. 标题、描述、标签中的 AI 关键词匹配
> 4. 综合置信度评分系统（阈值 0.3）
>
> **分析方法**：
> 1. 情感分析：规则基础 + BERT 多语言模型
> 2. 主题建模：LDA（Latent Dirichlet Allocation）
> 3. 统计检验：卡方检验（情感分布）、t检验（置信度）、Mann-Whitney U 检验（互动数据）
> 4. 时间序列：2022-2025 年度/月度趋势分析
>
> **数据规模**：
> - AI 内容评论：~1,000 条
> - 非 AI 内容评论：~1,000 条
> - 时间跨度：2022-2025

---

**维护者**: Chang Ho Chien
**工具版本**: 1.0.0
**最后更新**: 2025-10-17
