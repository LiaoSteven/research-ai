#!/usr/bin/env python3
"""
快速测试 - 直接使用 .env 文件中的 API 密钥
"""

import sys
from pathlib import Path

# 直接读取 .env 文件
env_file = Path(__file__).parent / '.env'
api_key = None

if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith('YOUTUBE_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                break

if not api_key:
    print("❌ 未在 .env 文件中找到 YOUTUBE_API_KEY")
    sys.exit(1)

print(f"✅ 找到 API 密钥: {api_key[:10]}...{api_key[-4:]}")

# 测试 API
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    print("✅ google-api-python-client 已安装")

    youtube = build('youtube', 'v3', developerKey=api_key)
    print("✅ YouTube API 客户端初始化成功")

    # 测试查询
    request = youtube.videos().list(
        part='snippet,statistics',
        id='dQw4w9WgXcQ'
    )
    response = request.execute()

    if response.get('items'):
        video = response['items'][0]
        print(f"\n✅ API 测试成功！")
        print(f"标题: {video['snippet']['title']}")
        print(f"观看次数: {video['statistics'].get('viewCount', 'N/A')}")
        print("\n🎉 您的 API 密钥工作正常！")
        print("现在可以运行: python collect_trending.py")
    else:
        print("❌ API 返回空结果")

except ImportError as e:
    print(f"❌ 缺少库: {e}")
    print("请先安装: pip install google-api-python-client")
except HttpError as e:
    print(f"❌ HTTP 错误: {e}")
    print("\n可能的原因：")
    print("1. API 密钥无效或未启用 YouTube Data API v3")
    print("2. 配额已用完")
    print("3. 访问 https://console.cloud.google.com/apis/dashboard 检查")
except Exception as e:
    print(f"❌ 错误: {e}")
