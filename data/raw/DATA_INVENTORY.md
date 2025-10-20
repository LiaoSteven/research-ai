# Data Inventory

**生成时间**: 2025-10-20 21:45:00

## 📊 活跃数据集 (active/)

- `dataset_2022Q1_6280comments.json` - 4.3M (6,280条评论, 2022Q1)
- `metadata_2022Q1.json` - 50K
- `dataset_2024-2025_1000comments.json` - 683K (1,000条评论, 8个季度)
- `metadata_2024-2025.json` - 13K

**总计**: 7,280 条评论

## 💾 Checkpoints (checkpoints/)

- `checkpoint_2022Q1.json` - 4.6M (有效)
- `checkpoint_2022Q4.json` - 4.6M (有效)

**说明**: 其他checkpoint文件过小（<100KB），已被跳过

## 🗃️ 归档数据 (archive/)

- `comments_20251017_184926.json` - 520K
- `comments_ai_generated_20251017_203109.json` - 342K
- `comments_non_ai_20251017_203109.json` - 517K
- `videos_20251017_184926.json` - 29K
- `videos_ai_generated_20251017_203109.json` - 29K
- `videos_non_ai_20251017_203109.json` - 22K

**总计**: 6个旧文件已归档

## 📋 数据清单

### 核心数据集

| 数据集 | 文件 | 评论数 | 时期 | AI占比 | 状态 |
|--------|------|--------|------|--------|------|
| Dataset 1 | `active/dataset_2022Q1_6280comments.json` | 6,280 | 2022Q1 | 29% | ✅ 已分析 |
| Dataset 2 | `active/dataset_2024-2025_1000comments.json` | 1,000 | 2024-2025 | 18% | ✅ 完整 |

### 分析产出

- **主题建模**: `../../output/topics/` (5个主题)
- **基础分析**: `../../output/analysis/`

## 🔄 下一步

1. 明天配额重置后运行: `bash scripts/collect_optimized.sh`
2. 预期采集: ~40万条评论
3. 完成时间: 约半天

## 📚 文档

- 数据管理指南: `../../docs/DATA_MANAGEMENT.md`
- API配额优化: `../../docs/API_QUOTA_OPTIMIZATION.md`
