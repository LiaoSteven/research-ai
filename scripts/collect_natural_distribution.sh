#!/bin/bash
#
# 自然分布采样 - 10万条评论（不预设AI/非AI比例）
#
# 核心理念：
# - 按时间均匀采样，不偏向任何内容类型
# - 自动检测每个视频是否AI生成
# - AI占比本身就是研究发现
#
# 使用方法:
#   bash scripts/collect_natural_distribution.sh
#

set -e

echo "================================================================================"
echo " YouTube Shorts 自然分布采样"
echo " 目标: 100,000 条评论 | 策略: 真实世界分布"
echo "================================================================================"
echo ""

# 检查 API 密钥
if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "❌ 错误: 未设置 YOUTUBE_API_KEY 环境变量"
    echo ""
    echo "请先设置 YouTube API 密钥:"
    echo "  export YOUTUBE_API_KEY=your_api_key_here"
    echo ""
    echo "或在 .env 文件中添加:"
    echo "  YOUTUBE_API_KEY=your_api_key_here"
    exit 1
fi

echo "✅ YouTube API 密钥已设置"
echo ""

# 说明采样策略
echo "📊 采样策略说明:"
echo "  • 不预设AI/非AI比例"
echo "  • 按时间均匀分布采样（2022-2025，共16季度）"
echo "  • 每个视频自动检测是否AI生成"
echo "  • AI占比由数据自然呈现"
echo ""

echo "🔍 AI检测方法:"
echo "  • 基于视频标题、描述、标签的关键词匹配"
echo "  • 检测工具名称: ChatGPT, Midjourney, DALL-E, Sora等"
echo "  • 检测描述性词汇: 'AI generated', 'created with AI'等"
echo "  • 置信度阈值: ≥0.2"
echo ""

# 确认开始
read -p "是否开始采集? (yes/no): " confirm

if [ "$confirm" != "yes" ] && [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "🚀 开始采集..."
echo ""

# 运行采集
python3 src/main/python/services/natural_distribution_collector.py \
    --total 100000 \
    --start-date 2022-01-01 \
    --end-date 2025-10-31 \
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
    echo "🔬 查看AI占比演变:"
    echo "  python3 scripts/analyze_ai_ratio.py --input data/raw/metadata_*.json"
    echo ""
    echo "📊 下一步分析:"
    echo "  1. 预处理: python scripts/preprocess_data.py"
    echo "  2. 情感分析: python scripts/run_sentiment_analysis.py"
    echo "  3. 主题建模: python scripts/run_topic_modeling.py"
    echo "  4. AI占比趋势: python scripts/plot_ai_ratio_evolution.py"
    echo ""
else
    echo ""
    echo "================================================================================"
    echo " ❌ 采集中断或失败"
    echo "================================================================================"
    echo ""
    echo "检查点文件已保存，可稍后继续"
    echo ""
fi

exit $exit_code
