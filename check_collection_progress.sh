#!/bin/bash
# 检查 AI 对比数据采集进度

echo "========================================================================"
echo "AI vs 非AI 数据采集进度检查"
echo "========================================================================"
echo ""

# 检查是否有新的数据文件
echo "📊 检查新生成的数据文件:"
echo ""

AI_FILES=$(ls -t data/raw/comments_ai_generated_*.json 2>/dev/null | head -1)
NON_AI_FILES=$(ls -t data/raw/comments_non_ai_*.json 2>/dev/null | head -1)

if [ -n "$AI_FILES" ]; then
    echo "✅ AI 数据文件:"
    echo "  $AI_FILES"
    AI_COUNT=$(source venv/bin/activate && python -c "import json; data=json.load(open('$AI_FILES')); print(len(data))")
    echo "  评论数: $AI_COUNT"
else
    echo "⏳ AI 数据文件: 尚未生成"
fi

echo ""

if [ -n "$NON_AI_FILES" ]; then
    echo "✅ 非AI 数据文件:"
    echo "  $NON_AI_FILES"
    NON_AI_COUNT=$(source venv/bin/activate && python -c "import json; data=json.load(open('$NON_AI_FILES')); print(len(data))")
    echo "  评论数: $NON_AI_COUNT"
else
    echo "⏳ 非AI 数据文件: 尚未生成"
fi

echo ""
echo "========================================================================"
echo "提示: 采集过程需要 30-60 分钟，请耐心等待"
echo "========================================================================"
