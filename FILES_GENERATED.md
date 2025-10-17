# 生成文件清单 (Generated Files List)

**基于1000条评论生成的所有文件**

生成时间: 2025-10-17
原始评论: 1000条 → 有效评论: 910条

---

## 📊 数据文件 (Data Files)

### 原始数据 (data/raw/)
| 文件名 | 大小 | 说明 |
|--------|------|------|
| `comments_20251017_184926.json` | 520KB | 1000条原始评论数据 |
| `videos_20251017_184926.json` | 29KB | 21个视频的元数据 |

### 处理后数据 (data/processed/)
| 文件名 | 大小 | 列数 | 说明 |
|--------|------|------|------|
| `comments.csv` | 359KB | 24列 | 预处理后的910条评论 |
| `comments_sentiment.csv` | 394KB | 27列 | 910条评论 + 情感分析结果 |
| `comments_sentiment_topics.csv` | 436KB | 30列 | 910条评论 + 情感 + 主题标签 |
| `preprocessing_stats.json` | 437B | - | 预处理统计信息 |

**数据列说明** (`comments_sentiment_topics.csv` - 30列):
1. video_id - 视频ID
2. comment_id - 评论ID
3. parent_id - 父评论ID
4. author - 作者名
5. author_channel_id - 作者频道ID
6. text - 原始文本
7. like_count - 点赞数
8. published_at - 发布时间
9. updated_at - 更新时间
10. reply_count - 回复数
11. is_reply - 是否为回复
12. collected_at - 采集时间
13. category - 类别
14. region - 地区
15. text_clean - 清洗后文本
16. text_length - 文本长度
17. word_count - 词数
18. published_datetime - 发布日期时间
19. published_date - 发布日期
20. published_year - 发布年份
21. published_month - 发布月份
22. published_day_of_week - 星期几
23. published_hour - 发布小时
24. preprocessed_at - 预处理时间
25. **sentiment** - **情感标签** (positive/negative/neutral)
26. **sentiment_confidence** - **情感置信度**
27. sentiment_analyzed_at - 情感分析时间
28. **topic** - **主题ID** (0-4)
29. **topic_probability** - **主题概率**
30. topic_analyzed_at - 主题分析时间

---

## 📈 可视化文件 (Visualization Files)

### 图表文件 (output/figures/)
| 文件名 | 大小 | 说明 |
|--------|------|------|
| `sentiment_distribution_pie.png` | 87KB | 情感分布饼图 |
| `sentiment_distribution_bar.png` | 81KB | 情感分布柱状图 |
| `sentiment_confidence_distribution.png` | 97KB | 情感置信度分布直方图 |
| `sentiment_over_time.png` | 186KB | 情感时间序列图 |
| `sentiment_vs_likes.png` | 86KB | 情感与点赞数关系箱线图 |
| `sentiment_report.txt` | 741B | 情感分析统计报告 |

**图表说明**:
- **饼图/柱状图**: 展示 75.9% 中性、20.1% 积极、4.0% 消极的分布
- **置信度分布**: 展示情感分类的置信度分布
- **时间序列**: 展示每日情感变化趋势
- **点赞关系**: 展示积极评论获得更多点赞 (8.52 vs 1.11)

---

## 📝 研究报告 (Research Reports)

### 报告文件 (output/reports/)
| 文件名 | 大小 | 行数 | 说明 |
|--------|------|------|------|
| `analysis_report_20251017_191552.txt` | 6.5KB | 217行 | 综合分析研究报告 |

**报告章节**:
1. 数据概览 (Data Overview)
2. 情感分析结果 (Sentiment Analysis)
3. 主题建模结果 (Topic Modeling)
4. 时间分析 (Temporal Analysis)
5. 热门评论分析 (Popular Comments)
6. 研究发现总结 (Key Findings)
7. 方法论 (Methodology)
8. 结论与建议 (Conclusions)

---

## 🔬 核心分析结果

### 情感分析结果
- **中性 (Neutral)**: 691条 (75.9%)
- **积极 (Positive)**: 183条 (20.1%)
- **消极 (Negative)**: 36条 (4.0%)

### 主题建模结果
- **主题 0**: 161条 (17.7%) - 游戏/Destiny讨论
- **主题 1**: 165条 (18.1%) - 一般视频讨论
- **主题 2**: 130条 (14.3%) - Cazzu音乐讨论
- **主题 3**: 97条 (10.7%) - 技术讨论
- **主题 4**: 311条 (34.2%) - 混合一般讨论

### 关键发现
⭐ **积极评论获得7.7倍更多点赞**
- 积极: 平均 8.52 赞
- 中性: 平均 1.11 赞
- 消极: 平均 0.31 赞

⭐ **主题4互动最高**
- 积极率: 28.6%
- 平均点赞: 5.91

⭐ **主题3互动最低**
- 积极率: 5.2%
- 平均点赞: 0.22

---

## 📂 文件访问路径

### Windows路径
```
D:\research-ai\data\processed\
D:\research-ai\output\figures\
D:\research-ai\output\reports\
```

### WSL路径
```
/mnt/d/research-ai/data/processed/
/mnt/d/research-ai/output/figures/
/mnt/d/research-ai/output/reports/
```

---

## 🔍 快速查看命令

### 查看数据
```bash
# 查看预处理统计
cat data/processed/preprocessing_stats.json

# 查看前10条数据
head -10 data/processed/comments_sentiment_topics.csv

# 查看数据列名
head -1 data/processed/comments_sentiment_topics.csv | sed 's/,/\n/g'
```

### 查看报告
```bash
# 查看情感统计报告
cat output/figures/sentiment_report.txt

# 查看完整研究报告
cat output/reports/analysis_report_20251017_191552.txt

# 查看报告摘要
head -50 output/reports/analysis_report_20251017_191552.txt
```

### 查看图表
```bash
# 列出所有图表
ls -lh output/figures/*.png

# 在Windows中打开图表
explorer.exe output/figures/
```

---

## 📊 数据处理流程

```
1000条原始评论 (comments_20251017_184926.json)
         ↓
      预处理
         ↓
910条有效评论 (comments.csv, 24列)
         ↓
     情感分析
         ↓
910条 + 情感标签 (comments_sentiment.csv, 27列)
         ↓
     主题建模
         ↓
910条 + 情感 + 主题 (comments_sentiment_topics.csv, 30列)
         ↓
    可视化 + 报告
         ↓
6个PNG图表 + 2个TXT报告
```

---

## 📈 文件使用说明

### 1. 原始数据文件
**用途**: 备份原始数据，可重新处理
- `data/raw/comments_20251017_184926.json`
- `data/raw/videos_20251017_184926.json`

### 2. 处理后数据文件
**用途**: 用于进一步分析和可视化
- **基础分析**: `comments.csv`
- **情感研究**: `comments_sentiment.csv`
- **综合研究**: `comments_sentiment_topics.csv` ⭐ **推荐使用**

### 3. 可视化文件
**用途**: 论文、报告、演示
- 所有PNG图表可直接插入文档
- `sentiment_report.txt` 可用于快速统计

### 4. 研究报告
**用途**: 完整的研究成果总结
- `analysis_report_20251017_191552.txt` - 包含所有分析结果

---

## 🎯 推荐使用方式

### 数据分析
```python
import pandas as pd

# 读取完整分析数据
df = pd.read_csv('data/processed/comments_sentiment_topics.csv')

# 查看情感分布
print(df['sentiment'].value_counts())

# 查看主题分布
print(df['topic'].value_counts())

# 查看情感与点赞关系
print(df.groupby('sentiment')['like_count'].mean())
```

### 报告使用
1. **学术论文**: 使用 `analysis_report_*.txt` 作为参考
2. **数据可视化**: 使用 `output/figures/*.png` 图表
3. **统计数据**: 参考 `sentiment_report.txt`

---

## 📝 文件说明总结

**总计生成文件**: 11个
- 数据文件: 4个 (processed)
- 图表文件: 6个 (5个PNG + 1个TXT)
- 报告文件: 1个 (TXT)

**总数据量**: ~1.5MB
**分析时间**: 2025-10-17
**分析状态**: ✅ 完成

---

**最后更新**: 2025-10-17 19:30
**维护者**: Chang Ho Chien
