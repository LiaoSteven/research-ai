#!/bin/bash
#
# 采集 10 万条 YouTube Shorts 评论 (2022-2025)
#
# 采样策略:
# - 时间范围: 2022年1月 - 2025年10月
# - 总评论数: 100,000 条
# - AI vs 非AI: 50% / 50%
# - 按季度分层采样 (16个季度)
# - 关键里程碑季度重点采样
#
# 使用方法:
#   bash scripts/collect_100k_comments.sh
#

set -e  # 遇到错误立即退出

echo "================================================================================"
echo " YouTube Shorts 大规模数据采集"
echo " 目标: 100,000 条评论 (2022-2025)"
echo "================================================================================"
echo ""

# 检查 API 密钥
if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "❌ 错误: 未设置 YOUTUBE_API_KEY 环境变量"
    echo ""
    echo "请先设置 YouTube API 密钥:"
    echo "  export YOUTUBE_API_KEY=your_api_key_here"
    echo ""
    echo "或者在 .env 文件中添加:"
    echo "  YOUTUBE_API_KEY=your_api_key_here"
    exit 1
fi

echo "✅ YouTube API 密钥已设置"
echo ""

# 确认开始
echo "⚠️  注意事项:"
echo "  • 此操作将采集 100,000 条评论"
echo "  • 预计耗时: 数小时到数天"
echo "  • 将消耗大量 YouTube API 配额"
echo "  • 每个季度会自动保存检查点"
echo ""
read -p "是否继续? (yes/no): " confirm

if [ "$confirm" != "yes" ] && [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "🚀 开始采集..."
echo ""

# 运行采集脚本
python3 src/main/python/services/large_scale_temporal_collector.py \
    --total 100000 \
    --start-date 2022-01-01 \
    --end-date 2025-10-31 \
    --checkpoint-interval 1 \
    --output-dir data/raw

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo " ✅ 采集完成!"
    echo "================================================================================"
    echo ""
    echo "📁 数据保存在: data/raw/"
    echo ""
    echo "下一步操作:"
    echo "  1. 查看采集结果: ls -lh data/raw/"
    echo "  2. 预处理数据: bash scripts/preprocess_100k.sh"
    echo "  3. 运行分析: bash scripts/analyze_100k.sh"
    echo ""
else
    echo ""
    echo "================================================================================"
    echo " ❌ 采集中断或失败"
    echo "================================================================================"
    echo ""
    echo "检查点文件已保存在 data/raw/"
    echo "可以稍后重新运行脚本继续采集"
    echo ""
fi

exit $exit_code
