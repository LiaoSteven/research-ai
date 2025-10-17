#!/usr/bin/env python3
"""
从 YouTube 热门视频自动采集评论

自动从不同类别的热门 Shorts 视频中采集评论数据

使用方法：
1. 设置环境变量：
   export YOUTUBE_API_KEY=your_api_key_here  # Linux/Mac
   set YOUTUBE_API_KEY=your_api_key_here     # Windows

2. 运行：
   python collect_trending.py

可选参数：
   --max-comments 1000    # 总共采集多少条评论（默认 1000）
   --per-video 50         # 每个视频采集多少条（默认 50）
   --category all         # 类别：all, gaming, music, tech, education, entertainment
   --region US            # 地区代码：US, CN, JP, KR, GB 等
"""

import sys
from pathlib import Path
import argparse

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src" / "main" / "python"))

import os
import json
import time
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


class TrendingCollector:
    """从热门视频采集评论"""

    # YouTube 视频类别 ID
    CATEGORIES = {
        'all': None,
        'film': '1',
        'autos': '2',
        'music': '10',
        'pets': '15',
        'sports': '17',
        'travel': '19',
        'gaming': '20',
        'people': '22',
        'comedy': '23',
        'entertainment': '24',
        'news': '25',
        'education': '27',
        'tech': '28'
    }

    def __init__(self, api_key: str):
        """初始化采集器"""
        self.collector = YouTubeCollector(api_key=api_key)
        self.youtube = self.collector.youtube

    def search_shorts_videos(
        self,
        max_results: int = 50,
        category: str = 'all',
        region: str = 'US'
    ) -> list:
        """
        搜索热门 Shorts 视频

        Args:
            max_results: 最多返回多少个视频
            category: 视频类别
            region: 地区代码

        Returns:
            视频 ID 列表
        """
        video_ids = []

        try:
            print(f"\n🔍 搜索热门 Shorts 视频...")
            print(f"   类别: {category}")
            print(f"   地区: {region}")

            # 构建搜索参数
            search_params = {
                'part': 'id,snippet',
                'type': 'video',
                'videoDuration': 'short',  # 短视频（< 4分钟）
                'maxResults': min(max_results, 50),  # API 限制
                'order': 'viewCount',  # 按观看次数排序
                'relevanceLanguage': 'zh',  # 中文内容优先
                'regionCode': region
            }

            # 添加类别过滤
            if category != 'all' and category in self.CATEGORIES:
                search_params['videoCategoryId'] = self.CATEGORIES[category]

            # 使用多个热门关键词搜索
            search_queries = [
                'shorts',
                'viral shorts',
                'trending shorts',
                'popular shorts'
            ]

            for query in search_queries:
                if len(video_ids) >= max_results:
                    break

                search_params['q'] = query

                try:
                    request = self.youtube.search().list(**search_params)
                    response = request.execute()

                    for item in response.get('items', []):
                        if 'videoId' in item['id']:
                            video_id = item['id']['videoId']
                            if video_id not in video_ids:
                                video_ids.append(video_id)

                    print(f"   找到 {len(video_ids)} 个视频...")
                    time.sleep(1)  # 速率限制

                except Exception as e:
                    print(f"   搜索错误: {e}")
                    continue

            print(f"✅ 共找到 {len(video_ids)} 个热门视频\n")
            return video_ids[:max_results]

        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return video_ids

    def get_trending_videos(
        self,
        max_results: int = 50,
        category: str = 'all',
        region: str = 'US'
    ) -> list:
        """
        获取热门视频列表

        Args:
            max_results: 最多返回多少个视频
            category: 视频类别
            region: 地区代码

        Returns:
            视频 ID 列表
        """
        video_ids = []

        try:
            print(f"\n🔥 获取热门视频...")

            # 使用 videos.list API 获取热门视频
            params = {
                'part': 'id,snippet,statistics',
                'chart': 'mostPopular',
                'regionCode': region,
                'maxResults': min(max_results, 50)
            }

            # 添加类别过滤
            if category != 'all' and category in self.CATEGORIES:
                params['videoCategoryId'] = self.CATEGORIES[category]

            request = self.youtube.videos().list(**params)
            response = request.execute()

            # 筛选出短视频（Shorts 通常 < 60秒）
            for item in response.get('items', []):
                video_id = item['id']
                # 简单检查，实际 Shorts 需要通过其他方式识别
                video_ids.append(video_id)

            print(f"✅ 找到 {len(video_ids)} 个热门视频\n")
            return video_ids

        except Exception as e:
            print(f"❌ 获取热门视频失败: {e}")
            return video_ids


def main():
    parser = argparse.ArgumentParser(description='从 YouTube 热门视频采集评论')
    parser.add_argument('--max-comments', type=int, default=1000,
                       help='总共采集多少条评论（默认 1000）')
    parser.add_argument('--per-video', type=int, default=50,
                       help='每个视频采集多少条评论（默认 50）')
    parser.add_argument('--category', type=str, default='all',
                       choices=['all', 'gaming', 'music', 'tech', 'education',
                               'entertainment', 'comedy', 'sports', 'news'],
                       help='视频类别（默认 all）')
    parser.add_argument('--region', type=str, default='US',
                       help='地区代码（默认 US，可选 CN, JP, KR, GB 等）')
    parser.add_argument('--label', type=str, default='',
                       help='数据标签（例如 ai_generated, non_ai）')

    args = parser.parse_args()

    print("\n" + "="*70)
    print(" YouTube 热门视频评论采集工具")
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

    # 初始化采集器
    try:
        trending = TrendingCollector(api_key=api_key)
        print("✅ YouTube API 连接成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return 1

    # 计算需要多少个视频
    videos_needed = (args.max_comments // args.per_video) + 1

    print(f"\n📊 采集参数：")
    print(f"   目标评论数：{args.max_comments}")
    print(f"   每视频评论：{args.per_video}")
    print(f"   需要视频数：约 {videos_needed}")
    print(f"   视频类别：{args.category}")
    print(f"   地区代码：{args.region}")

    # 获取视频列表（先尝试热门，再尝试搜索）
    video_ids = trending.get_trending_videos(
        max_results=videos_needed,
        category=args.category,
        region=args.region
    )

    # 如果热门视频不够，使用搜索补充
    if len(video_ids) < videos_needed:
        print(f"⚠️  热门视频不足，使用搜索补充...")
        search_ids = trending.search_shorts_videos(
            max_results=videos_needed - len(video_ids),
            category=args.category,
            region=args.region
        )
        video_ids.extend(search_ids)

    if not video_ids:
        print("❌ 没有找到视频")
        return 1

    print(f"\n🎬 准备从 {len(video_ids)} 个视频中采集评论...\n")

    # 采集评论
    all_comments = []
    video_info_list = []

    for idx, video_id in enumerate(video_ids, 1):
        if len(all_comments) >= args.max_comments:
            print(f"\n✅ 已达到目标评论数 {args.max_comments}，停止采集")
            break

        print(f"[{idx}/{len(video_ids)}] 处理视频: {video_id}")

        try:
            # 获取视频信息
            video_info = trending.collector.get_video_info(video_id)

            # 添加标签
            if args.label:
                video_info['video_type'] = args.label
            video_info['category'] = args.category
            video_info['region'] = args.region

            title = video_info['title'][:40] + "..." if len(video_info['title']) > 40 else video_info['title']
            print(f"  标题: {title}")
            print(f"  评论数: {video_info['comment_count']}")
            print(f"  观看数: {video_info['view_count']}")

            video_info_list.append(video_info)

            # 获取评论
            comments = trending.collector.get_video_comments(
                video_id,
                max_comments=args.per_video,
                include_replies=True
            )

            # 添加标签
            for comment in comments:
                if args.label:
                    comment['video_type'] = args.label
                comment['category'] = args.category
                comment['region'] = args.region

            all_comments.extend(comments)
            print(f"  ✓ 采集了 {len(comments)} 条评论（总计: {len(all_comments)}）")

            time.sleep(1)  # 速率限制

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
        label_suffix = f"_{args.label}" if args.label else ""
        category_suffix = f"_{args.category}" if args.category != 'all' else ""

        comments_file = output_dir / f'comments{label_suffix}{category_suffix}_{timestamp}.json'
        videos_file = output_dir / f'videos{label_suffix}{category_suffix}_{timestamp}.json'

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
        print(f"  类别：{args.category}")
        print(f"  地区：{args.region}")
        if args.label:
            print(f"  标签：{args.label}")

        print(f"\n💾 文件保存位置：")
        print(f"  评论数据：{comments_file}")
        print(f"  视频信息：{videos_file}")

        # 显示一些样本
        print(f"\n📝 评论样本（前 3 条）：")
        for i, comment in enumerate(all_comments[:3], 1):
            text = comment['text'][:60] + "..." if len(comment['text']) > 60 else comment['text']
            print(f"  {i}. {comment['author']}: {text}")

        print("\n✨ 下一步：")
        print(f"  1. 预处理：python scripts/preprocess_data.py --input {comments_file} --output data/processed/comments.csv")
        print(f"  2. 查看数据：使用 pandas 或 Excel 打开处理后的 CSV")
        print(f"  3. 分析：运行情感分析和主题建模")

        # 如果需要采集对照组
        if args.label:
            print(f"\n💡 提示：")
            print(f"  当前采集的是 '{args.label}' 类型的数据")
            print(f"  如需对照组，请运行：")
            if args.label == 'ai_generated':
                print(f"  python collect_trending.py --label non_ai --category {args.category}")
            else:
                print(f"  python collect_trending.py --label ai_generated --category {args.category}")

        print()
        return 0
    else:
        print("\n❌ 没有采集到任何评论")
        return 1


if __name__ == '__main__':
    sys.exit(main())
