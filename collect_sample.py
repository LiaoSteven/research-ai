#!/usr/bin/env python3
"""
简单的数据采集脚本 - 采集 1000 条评论样本

使用方法：
1. 设置环境变量：
   export YOUTUBE_API_KEY=your_api_key_here  # Linux/Mac
   set YOUTUBE_API_KEY=your_api_key_here     # Windows

2. 创建视频列表文件 video_urls.txt，每行一个 YouTube 链接，例如：
   https://youtube.com/shorts/abc123
   https://youtube.com/shorts/def456

3. 运行：
   python collect_sample.py
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src" / "main" / "python"))

import os
import json
from datetime import datetime

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 导入我们的模块
import services.youtube_collector as yt_module
YouTubeCollector = yt_module.YouTubeCollector


def main():
    print("\n" + "="*70)
    print(" YouTube 评论采集工具")
    print("="*70 + "\n")

    # 检查 API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ 错误：未找到 YouTube API 密钥")
        print("\n请设置环境变量：")
        print("  Linux/Mac: export YOUTUBE_API_KEY=your_api_key_here")
        print("  Windows:   set YOUTUBE_API_KEY=your_api_key_here")
        print("\n或者在 .env 文件中设置 YOUTUBE_API_KEY=your_api_key_here")
        return 1

    # 读取视频 URL
    video_file = 'video_urls.txt'
    if not Path(video_file).exists():
        print(f"❌ 错误：未找到 {video_file}")
        print(f"\n请创建 {video_file} 文件，每行一个 YouTube 视频链接，例如：")
        print("  https://youtube.com/shorts/abc123")
        print("  https://youtube.com/shorts/def456")
        print("  https://youtu.be/xyz789")
        return 1

    with open(video_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not urls:
        print(f"❌ 错误：{video_file} 文件是空的")
        return 1

    print(f"📋 找到 {len(urls)} 个视频链接")

    # 初始化采集器
    try:
        collector = YouTubeCollector(api_key=api_key)
        print("✅ YouTube API 连接成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return 1

    # 提取视频 ID
    video_ids = []
    for url in urls:
        video_id = collector.extract_video_id(url)
        if video_id:
            video_ids.append(video_id)
            print(f"  ✓ 视频 ID: {video_id}")
        else:
            print(f"  ✗ 无法解析: {url}")

    if not video_ids:
        print("❌ 没有有效的视频 ID")
        return 1

    print(f"\n📊 准备采集评论...")
    print(f"   目标：每个视频 100 条评论")
    print(f"   预计总数：约 {len(video_ids) * 100} 条\n")

    # 采集评论
    all_comments = []
    video_info_list = []

    for idx, video_id in enumerate(video_ids, 1):
        print(f"\n[{idx}/{len(video_ids)}] 处理视频: {video_id}")

        try:
            # 获取视频信息
            video_info = collector.get_video_info(video_id)
            print(f"  标题: {video_info['title'][:50]}...")
            print(f"  评论数: {video_info['comment_count']}")
            video_info_list.append(video_info)

            # 获取评论
            comments = collector.get_video_comments(
                video_id,
                max_comments=100,  # 每个视频 100 条
                include_replies=True
            )

            all_comments.extend(comments)
            print(f"  ✓ 采集了 {len(comments)} 条评论")

            # 如果已经达到 1000 条，就停止
            if len(all_comments) >= 1000:
                print(f"\n✅ 已采集 {len(all_comments)} 条评论，达到目标！")
                break

        except Exception as e:
            print(f"  ✗ 采集失败: {e}")
            continue

    # 保存结果
    if all_comments:
        # 创建输出目录
        output_dir = Path('data/raw')
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comments_file = output_dir / f'comments_sample_{timestamp}.json'
        videos_file = output_dir / f'videos_info_{timestamp}.json'

        # 保存评论
        with open(comments_file, 'w', encoding='utf-8') as f:
            json.dump(all_comments, f, ensure_ascii=False, indent=2)

        # 保存视频信息
        with open(videos_file, 'w', encoding='utf-8') as f:
            json.dump(video_info_list, f, ensure_ascii=False, indent=2)

        print("\n" + "="*70)
        print(" 采集完成！")
        print("="*70)
        print(f"\n📊 统计信息：")
        print(f"  总评论数：{len(all_comments)}")
        print(f"  处理视频：{len(video_info_list)}")
        print(f"\n💾 文件保存位置：")
        print(f"  评论数据：{comments_file}")
        print(f"  视频信息：{videos_file}")

        # 显示一些样本
        print(f"\n📝 评论样本（前 3 条）：")
        for i, comment in enumerate(all_comments[:3], 1):
            text = comment['text'][:60] + "..." if len(comment['text']) > 60 else comment['text']
            print(f"  {i}. {comment['author']}: {text}")

        print("\n✨ 下一步：")
        print(f"  1. 查看数据：cat {comments_file}")
        print(f"  2. 预处理：python scripts/preprocess_data.py --input {comments_file} --output data/processed/comments.csv")
        print(f"  3. 分析：使用 Jupyter Notebook 或 pandas 进行探索性分析")
        print()

        return 0
    else:
        print("\n❌ 没有采集到任何评论")
        return 1


if __name__ == '__main__':
    sys.exit(main())
