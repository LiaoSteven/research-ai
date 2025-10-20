# 数据管理指南

**版本**: 1.0
**更新时间**: 2025-10-20

## 📊 当前数据概况

### 主要数据集

| 数据集 | 文件名 | 评论数 | 大小 | 时期 | 状态 |
|--------|--------|--------|------|------|------|
| Dataset 1 | `comments_natural_distribution_20251020_203923.json` | 6,280 | 4.3 MB | 2022Q1 | ✅ 已分析 |
| Dataset 2 | `comments_natural_distribution_20251020_200458.json` | 1,000 | 683 KB | 2024-2025 | ✅ 完整 |
| **合计** | - | **7,280** | **~5 MB** | 2022-2025 | - |

### 衍生数据

| 类型 | 文件 | 说明 | 是否保留 |
|------|------|------|----------|
| AI评论 | `comments_ai_*.json` | 从主数据集筛选 | ⚠️ 可重新生成 |
| 非AI评论 | `comments_non_ai_*.json` | 从主数据集筛选 | ⚠️ 可重新生成 |
| Checkpoints | `checkpoint_*.json` | 采集检查点 | ✅ 保留（恢复用） |
| 元数据 | `metadata_*.json` | 采集统计 | ✅ 保留 |
| 旧数据 | `*20251017*.json` | 旧版本数据 | 🗑️ 可归档 |

---

## 🎯 数据整理策略

### 推荐的目录结构

```
data/
├── raw/                           # 原始数据
│   ├── active/                    # 活跃的主数据集
│   │   ├── dataset_2022Q1_6280comments.json
│   │   ├── metadata_2022Q1.json
│   │   ├── dataset_2024-2025_1000comments.json
│   │   └── metadata_2024-2025.json
│   ├── checkpoints/               # 采集检查点（用于恢复）
│   │   ├── checkpoint_2022Q1.json
│   │   ├── checkpoint_2024Q1.json
│   │   └── ...
│   ├── archive/                   # 归档旧数据
│   │   └── 20251017_old_data/
│   └── DATA_INVENTORY.md         # 数据清单
├── processed/                     # 处理后的数据
│   ├── comments_clean.csv        # 清洗后的评论
│   ├── comments_sentiment.csv    # 情感分析结果
│   └── comments_topics.csv       # 主题建模结果
└── external/                      # 外部数据源
```

---

## 🚀 快速整理

### 方法1: 使用自动整理脚本（推荐）

```bash
# 运行整理脚本
bash scripts/organize_data.sh
```

**脚本会自动**：
1. ✅ 创建新的目录结构（active/checkpoints/archive）
2. ✅ 重命名主数据集为清晰的名称
3. ✅ 移动checkpoint文件到专门目录
4. ✅ 归档旧数据（20251017）
5. ✅ 生成数据清单文档
6. ⚠️ 询问是否删除可重新生成的文件

**安全性**：
- 所有操作使用 `cp`（复制）而非 `mv`（移动）
- 原始文件保留在原位置
- 可以随时回滚

### 方法2: 手动整理

```bash
cd data/raw

# 1. 创建目录
mkdir -p active checkpoints archive

# 2. 复制主数据集
cp comments_natural_distribution_20251020_203923.json active/dataset_2022Q1_6280comments.json
cp comments_natural_distribution_20251020_200458.json active/dataset_2024-2025_1000comments.json

# 3. 复制元数据
cp metadata_natural_distribution_20251020_203923.json active/metadata_2022Q1.json
cp metadata_natural_distribution_20251020_200458.json active/metadata_2024-2025.json

# 4. 移动checkpoints
mv checkpoint_*.json checkpoints/

# 5. 归档旧数据
mv *20251017*.json archive/
```

---

## 📋 数据清单

### Dataset 1: 2022Q1 数据集

- **文件**: `active/dataset_2022Q1_6280comments.json`
- **评论数**: 6,280
- **AI占比**: 29%
- **采集日期**: 2025-10-20
- **时间范围**: 2022-01-01 ~ 2022-03-31
- **状态**: ✅ 已完成主题建模分析

**分析产出**:
- 主题建模: `output/topics/` (5个主题)
- 基础分析: `output/analysis/`

### Dataset 2: 2024-2025 数据集

- **文件**: `active/dataset_2024-2025_1000comments.json`
- **评论数**: 1,000
- **AI占比**: 18%
- **采集日期**: 2025-10-20
- **时间范围**: 2024-01-01 ~ 2025-10-31 (8个季度)
- **状态**: ✅ 采集完整，待分析

**季度分布**:
| 季度 | 评论数 | AI占比 |
|------|--------|--------|
| 2024Q1 | 125 | 24% |
| 2024Q2 | 125 | 24% |
| 2024Q3 | 125 | 0% |
| 2024Q4 | 125 | 0% |
| 2025Q1 | 125 | 24% |
| 2025Q2 | 125 | 0% |
| 2025Q3 | 125 | 24% |
| 2025Q4 | 125 | 48% |

---

## 🗑️ 清理建议

### 可以安全删除的文件

1. **Split数据** (可从主数据集重新生成)
   - `comments_ai_*.json`
   - `comments_non_ai_*.json`
   - 节省空间: ~2-3 MB

2. **失败的Checkpoints** (文件过小 < 100KB)
   - `checkpoint_2022Q3.json` (393 bytes)
   - 节省空间: 微量

3. **旧版本数据** (已被新版本替代)
   - `*20251017*.json`
   - 节省空间: ~1-2 MB

**删除命令**（谨慎使用）:
```bash
cd data/raw

# 删除split数据
rm comments_ai_*.json comments_non_ai_*.json

# 删除失败的checkpoints
find . -name "checkpoint_*.json" -size -100k -delete

# 移动旧数据到archive（而非删除）
mv *20251017*.json archive/
```

### 不要删除的文件

❌ **主数据集**
- `comments_natural_distribution_*.json` (核心数据！)

❌ **元数据**
- `metadata_*.json` (记录采集统计)

❌ **有效Checkpoints**
- 大于 100KB 的 checkpoint 文件（用于恢复采集）

---

## 📈 数据使用指南

### 读取数据

```python
import json

# 读取主数据集
with open('data/raw/active/dataset_2022Q1_6280comments.json') as f:
    comments = json.load(f)

print(f"评论总数: {len(comments)}")
print(f"第一条评论: {comments[0]}")
```

### 过滤AI/非AI评论

```python
# 从主数据集分离
ai_comments = [c for c in comments if c.get('video_type') == 'ai_generated']
non_ai_comments = [c for c in comments if c.get('video_type') == 'non_ai']

print(f"AI评论: {len(ai_comments)}")
print(f"非AI评论: {len(non_ai_comments)}")
```

### 按季度筛选

```python
# 筛选特定季度
q1_comments = [c for c in comments if c.get('quarter') == '2022Q1']
print(f"2022Q1 评论数: {len(q1_comments)}")
```

---

## 🔄 数据更新流程

### 新数据采集后

1. **运行采集器** (明天配额重置后)
   ```bash
   bash scripts/collect_optimized.sh
   ```

2. **复制到active**
   ```bash
   cp data/raw/comments_optimized_*.json data/raw/active/dataset_YYYYMMDD.json
   ```

3. **更新数据清单**
   ```bash
   bash scripts/organize_data.sh  # 自动更新 DATA_INVENTORY.md
   ```

4. **提交到Git**
   ```bash
   git add data/raw/active/
   git commit -m "Add new dataset YYYYMMDD"
   ```

---

## 🔒 数据备份

### 重要性

原始数据是**不可再生资源**（API配额限制），必须做好备份！

### 备份方案

**方案1: Git备份** (已配置)
```bash
# 自动通过git保护
git add data/raw/active/
git commit -m "Backup dataset"
git push origin main
```

**方案2: 云存储备份**
```bash
# Google Drive / Dropbox / OneDrive
cp -r data/raw/active/ /path/to/cloud/backup/
```

**方案3: 压缩归档**
```bash
# 创建压缩包
tar -czf backup_$(date +%Y%m%d).tar.gz data/raw/active/

# 保存到安全位置
mv backup_*.tar.gz ~/backups/
```

---

## 📊 数据质量检查

### 检查脚本

```bash
# 检查数据完整性
python scripts/check_data_quality.py
```

### 手动检查

```python
import json

# 检查评论数
with open('data/raw/active/dataset_2022Q1_6280comments.json') as f:
    data = json.load(f)

print(f"评论总数: {len(data)}")

# 检查必需字段
required_fields = ['comment_id', 'text', 'video_type', 'quarter']
for i, comment in enumerate(data[:10]):
    missing = [f for f in required_fields if f not in comment]
    if missing:
        print(f"评论 {i} 缺少字段: {missing}")
```

---

## 🛠️ 故障排查

### 问题: 找不到数据文件

**检查**:
```bash
ls -lh data/raw/active/
```

**修复**:
```bash
bash scripts/organize_data.sh  # 重新整理
```

### 问题: 数据损坏

**检查**:
```bash
python -m json.tool data/raw/active/dataset_2022Q1_6280comments.json > /dev/null
```

**修复**:
- 从checkpoint恢复
- 从Git历史恢复
- 从备份恢复

### 问题: 磁盘空间不足

**检查空间使用**:
```bash
du -sh data/raw/*
```

**清理策略**:
1. 删除可重新生成的split文件
2. 归档旧版本数据
3. 压缩checkpoint文件

---

## 📚 相关文档

- [API配额优化指南](API_QUOTA_OPTIMIZATION.md)
- [主题建模分析报告](../output/topics/topic_analysis_report_20251020_211344.txt)
- [数据采集文档](../README.md)

---

**生成时间**: 2025-10-20
**维护者**: Claude Code
**版本**: 1.0
