#!/bin/bash
#
# 监控数据采集进度
#

echo "================================================================================"
echo " 数据采集进度监控"
echo "================================================================================"
echo ""

# 检查检查点文件
if [ -d "data/raw" ]; then
    echo "📁 检查点文件:"
    ls -lh data/raw/checkpoint_*.json 2>/dev/null | tail -5
    echo ""

    echo "📊 最新采集统计:"
    latest_checkpoint=$(ls -t data/raw/checkpoint_*.json 2>/dev/null | head -1)
    if [ -f "$latest_checkpoint" ]; then
        echo "最新检查点: $(basename $latest_checkpoint)"

        # 提取关键统计信息
        collected=$(jq -r '.stats.collected_comments // 0' "$latest_checkpoint" 2>/dev/null)
        ai_comments=$(jq -r '.stats.ai_comments // 0' "$latest_checkpoint" 2>/dev/null)
        non_ai_comments=$(jq -r '.stats.non_ai_comments // 0' "$latest_checkpoint" 2>/dev/null)
        quarter=$(jq -r '.stats.quarter // "unknown"' "$latest_checkpoint" 2>/dev/null)

        echo "  季度: $quarter"
        echo "  已采集: $collected 条"
        echo "  AI内容: $ai_comments 条"
        echo "  非AI: $non_ai_comments 条"

        if [ "$collected" -gt 0 ]; then
            ai_ratio=$(echo "scale=1; $ai_comments * 100 / $collected" | bc)
            echo "  AI占比: ${ai_ratio}%"
        fi
    else
        echo "  暂无检查点文件"
    fi
    echo ""

    echo "📈 采集进度:"
    checkpoint_count=$(ls data/raw/checkpoint_*.json 2>/dev/null | wc -l)
    echo "  已完成季度: $checkpoint_count / 16"

    if [ $checkpoint_count -gt 0 ]; then
        progress=$(echo "scale=1; $checkpoint_count * 100 / 16" | bc)
        echo "  总体进度: ${progress}%"
    fi
else
    echo "❌ data/raw 目录不存在"
fi

echo ""
echo "================================================================================"
echo "运行此脚本查看最新进度: bash scripts/monitor_collection.sh"
echo "================================================================================"
