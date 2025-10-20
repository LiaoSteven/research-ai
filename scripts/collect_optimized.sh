#!/bin/bash
# 配额优化采集脚本 - 节省87%配额
# 使用方法: bash scripts/collect_optimized.sh

set -e

echo "================================================================================"
echo " 🚀 YouTube 配额优化采集器"
echo "================================================================================"
echo " 配额节省: 35,344 → 4,544 units (87% reduction)"
echo " 采集时间: 3.5 天 → 0.5 天 (7x faster)"
echo " 100K评论可在单日配额内完成！"
echo "================================================================================"

# 检查 API Key
if [ -z "$YOUTUBE_API_KEY" ]; then
    echo ""
    echo "❌ 错误: 未设置 YOUTUBE_API_KEY 环境变量"
    echo ""
    echo "请先设置 YouTube API 密钥:"
    echo "  export YOUTUBE_API_KEY=your_api_key_here"
    echo ""
    exit 1
fi

echo ""
echo "✅ YouTube API Key 已设置"

# 激活虚拟环境
if [ -d "venv" ]; then
    echo "✅ 激活虚拟环境"
    source venv/bin/activate
fi

# 设置 PYTHONPATH
export PYTHONPATH=$(pwd)/src/main/python:$PYTHONPATH
echo "✅ PYTHONPATH 已设置"

# 运行优化版采集器
echo ""
echo "================================================================================"
echo " 开始采集 - 优化模式"
echo "================================================================================"
echo ""

python src/main/python/services/quota_optimized_collector.py \
    --total 100000 \
    --start-date 2022-01-01 \
    --end-date 2025-10-31 \
    --output-dir data/raw

echo ""
echo "================================================================================"
echo " 🎉 采集完成！"
echo "================================================================================"
echo ""
echo "生成的文件位于: data/raw/"
echo "  - comments_optimized_*.json  (所有评论)"
echo "  - comments_ai_*.json         (AI评论)"
echo "  - comments_non_ai_*.json     (非AI评论)"
echo "  - metadata_optimized_*.json  (元数据 + 配额统计)"
echo "  - video_pool_cache.json      (视频池缓存)"
echo ""
echo "下一步："
echo "  1. 数据分析: python scripts/analyze_collected_data.py"
echo "  2. 主题建模: python scripts/topic_modeling_analysis.py"
echo ""
