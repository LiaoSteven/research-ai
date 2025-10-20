#!/bin/bash
# 数据整理脚本 - 清理和组织data/raw目录

set -e

echo "================================================================================"
echo " 📁 数据整理工具"
echo "================================================================================"

cd data/raw

echo ""
echo "📊 当前数据概况:"
echo "  总文件数: $(ls -1 | wc -l)"
echo "  总大小: $(du -sh . | cut -f1)"

# 创建目录结构
echo ""
echo "🏗️  创建新的目录结构..."
mkdir -p active checkpoints archive

# 1. 识别并移动主要数据集
echo ""
echo "1️⃣ 整理主要数据集..."

if [ -f "comments_natural_distribution_20251020_203923.json" ]; then
    echo "  ✅ 发现 2022Q1 数据集 (6,280条)"
    cp comments_natural_distribution_20251020_203923.json active/dataset_2022Q1_6280comments.json
    cp metadata_natural_distribution_20251020_203923.json active/metadata_2022Q1.json
    echo "     → 复制到 active/"
fi

if [ -f "comments_natural_distribution_20251020_200458.json" ]; then
    echo "  ✅ 发现 2024-2025 数据集 (1,000条)"
    cp comments_natural_distribution_20251020_200458.json active/dataset_2024-2025_1000comments.json
    cp metadata_natural_distribution_20251020_200458.json active/metadata_2024-2025.json
    echo "     → 复制到 active/"
fi

# 2. 整理checkpoint文件
echo ""
echo "2️⃣ 整理checkpoint文件..."

checkpoint_count=0
for f in checkpoint_*.json; do
    if [ -f "$f" ]; then
        size=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null || echo 0)
        if [ "$size" -gt 100000 ]; then
            cp "$f" checkpoints/
            checkpoint_count=$((checkpoint_count + 1))
            echo "  ✅ 保留: $f ($(du -h "$f" | cut -f1))"
        else
            echo "  ⚠️  跳过: $f (文件过小，可能失败)"
        fi
    fi
done

if [ $checkpoint_count -eq 0 ]; then
    echo "  ℹ️  没有找到有效的checkpoint文件"
fi

# 3. 归档旧数据
echo ""
echo "3️⃣ 归档旧数据..."

archived_count=0
for f in *20251017*.json; do
    if [ -f "$f" ]; then
        mv "$f" archive/
        archived_count=$((archived_count + 1))
        echo "  🗃️  归档: $f"
    fi
done

if [ $archived_count -eq 0 ]; then
    echo "  ✅ 没有需要归档的旧数据"
fi

# 4. 清理split数据（可重新生成）
echo ""
echo "4️⃣ 清理可重新生成的文件..."

echo "  ℹ️  以下文件可从主数据集重新生成:"
for f in comments_ai_*.json comments_non_ai_*.json; do
    if [ -f "$f" ] && [[ ! "$f" =~ "active/" ]]; then
        size=$(du -h "$f" | cut -f1)
        echo "     • $f ($size)"
    fi
done

read -p "  是否删除这些文件? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    for f in comments_ai_*.json comments_non_ai_*.json; do
        if [ -f "$f" ] && [[ ! "$f" =~ "active/" ]]; then
            rm "$f"
            echo "     ✅ 已删除: $f"
        fi
    done
else
    echo "     ⏭️  跳过删除"
fi

# 5. 生成数据清单
echo ""
echo "5️⃣ 生成数据清单..."

cat > DATA_INVENTORY.md << 'INVENTORY_EOF'
# Data Inventory

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')

## 📊 活跃数据集 (active/)

INVENTORY_EOF

if [ -d "active" ]; then
    for f in active/*.json; do
        if [ -f "$f" ]; then
            size=$(du -h "$f" | cut -f1)
            echo "- \`$(basename "$f")\` - $size" >> DATA_INVENTORY.md
        fi
    done
fi

cat >> DATA_INVENTORY.md << 'INVENTORY_EOF'

## 💾 Checkpoints (checkpoints/)

INVENTORY_EOF

if [ -d "checkpoints" ]; then
    for f in checkpoints/*.json; do
        if [ -f "$f" ]; then
            size=$(du -h "$f" | cut -f1)
            echo "- \`$(basename "$f")\` - $size" >> DATA_INVENTORY.md
        fi
    done
fi

cat >> DATA_INVENTORY.md << 'INVENTORY_EOF'

## 🗃️  归档数据 (archive/)

INVENTORY_EOF

if [ -d "archive" ]; then
    for f in archive/*.json; do
        if [ -f "$f" ]; then
            size=$(du -h "$f" | cut -f1)
            echo "- \`$(basename "$f")\` - $size" >> DATA_INVENTORY.md
        fi
    done
fi

echo "  ✅ 数据清单已生成: data/raw/DATA_INVENTORY.md"

# 6. 显示最终结果
echo ""
echo "================================================================================"
echo " ✅ 数据整理完成！"
echo "================================================================================"

echo ""
echo "📁 新的目录结构:"
echo "  data/raw/"
echo "  ├── active/              (活跃数据集)"
if [ -d "active" ]; then
    ls -1 active/ | sed 's/^/  │   ├── /'
fi
echo "  ├── checkpoints/         (恢复检查点)"
if [ -d "checkpoints" ]; then
    echo "  │   └── $(ls -1 checkpoints/ | wc -l) 个文件"
fi
echo "  └── archive/             (旧数据归档)"
if [ -d "archive" ]; then
    echo "      └── $(ls -1 archive/ | wc -l) 个文件"
fi

echo ""
echo "📊 空间使用:"
echo "  active/: $(du -sh active 2>/dev/null | cut -f1 || echo '0B')"
echo "  checkpoints/: $(du -sh checkpoints 2>/dev/null | cut -f1 || echo '0B')"
echo "  archive/: $(du -sh archive 2>/dev/null | cut -f1 || echo '0B')"

echo ""
echo "📖 查看数据清单:"
echo "  cat data/raw/DATA_INVENTORY.md"

echo ""
