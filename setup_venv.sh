#!/bin/bash
# 设置 Python 虚拟环境

echo "=================================="
echo " 设置 Python 虚拟环境"
echo "=================================="
echo ""

# 检查 python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 python3"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境（给出提示）
echo ""
echo "=================================="
echo " 下一步："
echo "=================================="
echo ""
echo "1. 激活虚拟环境："
echo "   source venv/bin/activate"
echo ""
echo "2. 安装依赖："
echo "   pip install -r requirements-minimal.txt"
echo ""
echo "3. 测试 API 密钥："
echo "   python test_api_key.py"
echo ""
echo "4. 采集数据："
echo "   python collect_trending.py"
echo ""
