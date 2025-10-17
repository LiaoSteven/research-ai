#!/usr/bin/env python3
"""
测试 YouTube API 密钥是否正常工作

运行此脚本来验证您的 API 密钥配置
"""

import os
import sys

def test_api_key():
    print("\n" + "="*70)
    print(" YouTube API 密钥测试")
    print("="*70 + "\n")

    # 1. 检查环境变量
    print("1️⃣  检查环境变量...")
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key:
        print("   ❌ 未找到 YOUTUBE_API_KEY 环境变量")
        print("\n   请设置环境变量：")
        print("   Windows PowerShell:")
        print("     $env:YOUTUBE_API_KEY='你的API密钥'")
        print("\n   或者创建 .env 文件：")
        print("     YOUTUBE_API_KEY=你的API密钥")
        return False

    print(f"   ✅ 找到 API 密钥: {api_key[:10]}...{api_key[-4:]}")
    print(f"   密钥长度: {len(api_key)} 字符")

    # 2. 检查库安装
    print("\n2️⃣  检查必要的库...")
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        print("   ✅ google-api-python-client 已安装")
    except ImportError as e:
        print(f"   ❌ 缺少必要的库: {e}")
        print("\n   请安装：")
        print("     pip install google-api-python-client")
        return False

    # 3. 测试 API 连接
    print("\n3️⃣  测试 YouTube API 连接...")
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        print("   ✅ YouTube API 客户端初始化成功")
    except Exception as e:
        print(f"   ❌ 初始化失败: {e}")
        return False

    # 4. 测试简单查询（获取一个公开视频的信息）
    print("\n4️⃣  测试 API 查询...")
    test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up

    try:
        request = youtube.videos().list(
            part='snippet,statistics',
            id=test_video_id
        )
        response = request.execute()

        if response.get('items'):
            video = response['items'][0]
            print(f"   ✅ API 查询成功！")
            print(f"\n   测试视频信息：")
            print(f"   - 标题: {video['snippet']['title']}")
            print(f"   - 观看次数: {video['statistics'].get('viewCount', 'N/A')}")
            print(f"   - 评论数: {video['statistics'].get('commentCount', 'N/A')}")
        else:
            print("   ⚠️  API 返回空结果")
            return False

    except HttpError as e:
        print(f"   ❌ HTTP 错误: {e}")

        if e.resp.status == 400:
            print("\n   可能的原因：")
            print("   - API 密钥格式错误")
            print("   - API 密钥无效")
        elif e.resp.status == 403:
            print("\n   可能的原因：")
            print("   - API 密钥未授权 YouTube Data API v3")
            print("   - 配额已用完")
            print("\n   解决方案：")
            print("   1. 访问 https://console.cloud.google.com/apis/dashboard")
            print("   2. 确保启用了 'YouTube Data API v3'")
            print("   3. 检查配额限制")
        return False

    except Exception as e:
        print(f"   ❌ 查询失败: {e}")
        return False

    # 5. 测试评论查询
    print("\n5️⃣  测试评论获取...")
    try:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=test_video_id,
            maxResults=1,
            textFormat='plainText'
        )
        response = request.execute()

        if response.get('items'):
            comment = response['items'][0]['snippet']['topLevelComment']['snippet']
            print(f"   ✅ 评论获取成功！")
            print(f"\n   样本评论：")
            print(f"   - 作者: {comment['authorDisplayName']}")
            print(f"   - 内容: {comment['textDisplay'][:50]}...")
        else:
            print("   ⚠️  该视频可能没有评论或评论被禁用")

    except HttpError as e:
        if e.resp.status == 403:
            if 'commentsDisabled' in str(e):
                print("   ℹ️  该视频的评论被禁用（这是正常的）")
            else:
                print(f"   ❌ HTTP 403 错误: {e}")
                return False
        else:
            print(f"   ❌ HTTP 错误: {e}")
            return False
    except Exception as e:
        print(f"   ❌ 评论查询失败: {e}")
        return False

    # 成功
    print("\n" + "="*70)
    print(" ✅ 所有测试通过！您的 API 密钥配置正确")
    print("="*70)
    print("\n📊 API 配额信息：")
    print("   - YouTube Data API v3 默认配额：10,000 单位/天")
    print("   - 查询视频信息：1 单位")
    print("   - 查询评论：1 单位/请求")
    print("   - 预计可采集：约 9,000 条评论/天")
    print("\n🚀 现在可以开始采集数据了！")
    print("   运行: python collect_trending.py")
    print()

    return True


if __name__ == '__main__':
    success = test_api_key()
    sys.exit(0 if success else 1)
