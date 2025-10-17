#!/usr/bin/env python3
"""
采集 AI vs 非AI 视频评论进行对比研究

自动检测视频是否包含 AI 内容，并采集两组数据进行对比分析

使用方法：
    python collect_ai_comparison.py --ai-videos 500 --non-ai-videos 500
"""

import sys
from pathlib import Path
import argparse
import os
import json
import time
from datetime import datetime

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src" / "main" / "python"))

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 导入模块
import services.youtube_collector as yt_module
YouTubeCollector = yt_module.YouTubeCollector

# 导入 AI 检测器
from detect_ai_content import AIContentDetector


class ComparisonCollector:
    """采集 AI vs 非AI 视频评论用于对比研究"""

    # AI 相关搜索关键词
    AI_SEARCH_QUERIES = [
        'AI generated shorts',
        'AI art shorts',
        'AI animation shorts',
        'midjourney shorts',
        'stable diffusion shorts',
        'AI video shorts',
        'generative AI shorts'
    ]

    # 非 AI 搜索关键词
    NON_AI_SEARCH_QUERIES = [
        'handmade shorts',
        'traditional art shorts',
        'real footage shorts',
        'vlog shorts',
        'cooking shorts',
        'DIY shorts',
        'tutorial shorts'
    ]

    def __init__(self, api_key: str):
        """初始化采集器"""
        self.collector = YouTubeCollector(api_key=api_key)
        self.detector = AIContentDetector(api_key=api_key)
        self.youtube = self.collector.youtube

    def search_videos(
        self,
        queries: list,
        max_results: int = 50,
        region: str = 'US'
    ) -> list:
        """
        搜索视频

        Args:
            queries: 搜索关键词列表
            max_results: 最多返回多少个视频
            region: 地区代码

        Returns:
            视频 ID 列表
        """
        video_ids = []
        found_videos = set()

        print(f"\n🔍 搜索视频...")
        print(f"   关键词数量: {len(queries)}")

        for query in queries:
            if len(video_ids) >= max_results:
                break

            print(f"   搜索: '{query}'")

            try:
                search_params = {
                    'part': 'id,snippet',
                    'type': 'video',
                    'q': query,
                    'videoDuration': 'short',
                    'maxResults': min(10, max_results - len(video_ids)),
                    'order': 'relevance',
                    'regionCode': region
                }

                request = self.youtube.search().list(**search_params)
                response = request.execute()

                for item in response.get('items', []):
                    if 'videoId' in item['id']:
                        video_id = item['id']['videoId']
                        if video_id not in found_videos:
                            found_videos.add(video_id)
                            video_ids.append(video_id)
                            print(f"      ✓ {video_id}")

                time.sleep(1)

            except Exception as e:
                print(f"      ✗ 错误: {e}")
                continue

        print(f"✅ 找到 {len(video_ids)} 个视频")
        return video_ids

    def collect_with_detection(
        self,
        target_type: str,  # 'ai' or 'non_ai'
        max_comments: int = 500,
        per_video: int = 50,
        region: str = 'US',
        verify_threshold: float = 0.3
    ) -> tuple:
        """
        采集并验证视频类型

        Args:
            target_type: 'ai' 或 'non_ai'
            max_comments: 目标评论数
            per_video: 每视频评论数
            region: 地区代码
            verify_threshold: AI 检测置信度阈值

        Returns:
            (comments, video_info_list)
        """
        print(f"\n{'='*70}")
        print(f" 采集 {target_type.upper()} 内容视频评论")
        print(f"{'='*70}")

        # 选择搜索关键词
        if target_type == 'ai':
            queries = self.AI_SEARCH_QUERIES
            label = 'ai_generated'
        else:
            queries = self.NON_AI_SEARCH_QUERIES
            label = 'non_ai'

        # 计算需要的视频数
        videos_needed = (max_comments // per_video) * 2  # 多搜索一些备用

        # 搜索视频
        video_ids = self.search_videos(queries, videos_needed, region)

        if not video_ids:
            print("❌ 没有找到视频")
            return [], []

        # 验证和过滤
        print(f"\n🔍 验证视频内容...")
        verified_videos = []

        for video_id in video_ids:
            result = self.detector.detect_ai_content(video_id, verbose=False)

            # 判断是否符合目标类型
            if target_type == 'ai':
                # 需要是 AI 内容
                if result['confidence'] >= verify_threshold:
                    verified_videos.append(result)
                    print(f"   ✓ {video_id}: AI 内容 (置信度 {result['confidence']:.2f})")
            else:
                # 需要不是 AI 内容
                if result['confidence'] < verify_threshold:
                    verified_videos.append(result)
                    print(f"   ✓ {video_id}: 非 AI 内容 (置信度 {result['confidence']:.2f})")

            if len(verified_videos) >= (max_comments // per_video):
                break

        print(f"\n✅ 验证通过 {len(verified_videos)} 个视频")

        if not verified_videos:
            print("❌ 没有通过验证的视频")
            return [], []

        # 采集评论
        print(f"\n📝 开始采集评论...")
        all_comments = []
        video_info_list = []

        for idx, result in enumerate(verified_videos, 1):
            if len(all_comments) >= max_comments:
                print(f"\n✅ 已达到目标评论数 {max_comments}")
                break

            video_id = result['video_id']
            print(f"\n[{idx}/{len(verified_videos)}] 处理: {video_id}")
            print(f"  标题: {result['title'][:50]}...")
            print(f"  AI 置信度: {result['confidence']:.2f}")

            try:
                # 获取视频信息
                video_info = self.collector.get_video_info(video_id)
                video_info['video_type'] = label
                video_info['ai_confidence'] = result['confidence']
                video_info['ai_indicators'] = result['indicators']
                video_info_list.append(video_info)

                # 获取评论
                comments = self.collector.get_video_comments(
                    video_id,
                    max_comments=per_video,
                    include_replies=True
                )

                # 添加标签
                for comment in comments:
                    comment['video_type'] = label
                    comment['ai_confidence'] = result['confidence']

                all_comments.extend(comments)
                print(f"  ✓ 采集 {len(comments)} 条评论 (总计: {len(all_comments)})")

                time.sleep(1)

            except Exception as e:
                print(f"  ✗ 失败: {e}")
                continue

        return all_comments, video_info_list


def main():
    parser = argparse.ArgumentParser(description='采集 AI vs 非AI 视频评论进行对比研究')
    parser.add_argument('--ai-comments', type=int, default=500,
                       help='AI 内容评论数（默认 500）')
    parser.add_argument('--non-ai-comments', type=int, default=500,
                       help='非 AI 内容评论数（默认 500）')
    parser.add_argument('--per-video', type=int, default=50,
                       help='每视频评论数（默认 50）')
    parser.add_argument('--region', type=str, default='US',
                       help='地区代码（默认 US）')
    parser.add_argument('--threshold', type=float, default=0.3,
                       help='AI 检测置信度阈值（默认 0.3）')

    args = parser.parse_args()

    print("\n" + "="*70)
    print(" AI vs 非AI 视频评论对比采集工具")
    print("="*70)

    # 检查 API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("\n❌ 错误：未找到 YouTube API 密钥")
        print("请在 .env 文件中设置 YOUTUBE_API_KEY")
        return 1

    # 初始化采集器
    try:
        collector = ComparisonCollector(api_key=api_key)
        print("\n✅ YouTube API 连接成功")
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        return 1

    print(f"\n📊 采集参数:")
    print(f"  AI 内容评论: {args.ai_comments}")
    print(f"  非 AI 评论: {args.non_ai_comments}")
    print(f"  每视频评论: {args.per_video}")
    print(f"  检测阈值: {args.threshold}")
    print(f"  地区: {args.region}")

    # 1. 采集 AI 内容评论
    ai_comments, ai_videos = collector.collect_with_detection(
        target_type='ai',
        max_comments=args.ai_comments,
        per_video=args.per_video,
        region=args.region,
        verify_threshold=args.threshold
    )

    # 2. 采集非 AI 内容评论
    non_ai_comments, non_ai_videos = collector.collect_with_detection(
        target_type='non_ai',
        max_comments=args.non_ai_comments,
        per_video=args.per_video,
        region=args.region,
        verify_threshold=args.threshold
    )

    # 保存结果
    output_dir = Path('data/raw')
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if ai_comments:
        ai_comments_file = output_dir / f'comments_ai_generated_{timestamp}.json'
        ai_videos_file = output_dir / f'videos_ai_generated_{timestamp}.json'

        with open(ai_comments_file, 'w', encoding='utf-8') as f:
            json.dump(ai_comments, f, ensure_ascii=False, indent=2)
        with open(ai_videos_file, 'w', encoding='utf-8') as f:
            json.dump(ai_videos, f, ensure_ascii=False, indent=2)

        print(f"\n💾 AI 内容数据已保存:")
        print(f"  评论: {ai_comments_file}")
        print(f"  视频: {ai_videos_file}")

    if non_ai_comments:
        non_ai_comments_file = output_dir / f'comments_non_ai_{timestamp}.json'
        non_ai_videos_file = output_dir / f'videos_non_ai_{timestamp}.json'

        with open(non_ai_comments_file, 'w', encoding='utf-8') as f:
            json.dump(non_ai_comments, f, ensure_ascii=False, indent=2)
        with open(non_ai_videos_file, 'w', encoding='utf-8') as f:
            json.dump(non_ai_videos, f, ensure_ascii=False, indent=2)

        print(f"\n💾 非 AI 内容数据已保存:")
        print(f"  评论: {non_ai_comments_file}")
        print(f"  视频: {non_ai_videos_file}")

    # 统计结果
    print("\n" + "="*70)
    print(" 采集完成！")
    print("="*70)
    print(f"\n📊 统计:")
    print(f"  AI 内容评论: {len(ai_comments)} 条 (来自 {len(ai_videos)} 个视频)")
    print(f"  非 AI 评论: {len(non_ai_comments)} 条 (来自 {len(non_ai_videos)} 个视频)")
    print(f"  总计: {len(ai_comments) + len(non_ai_comments)} 条评论")

    print(f"\n✨ 下一步:")
    print(f"  1. 预处理数据:")
    if ai_comments:
        print(f"     python scripts/preprocess_data.py --input {ai_comments_file}")
    if non_ai_comments:
        print(f"     python scripts/preprocess_data.py --input {non_ai_comments_file}")
    print(f"  2. 合并两组数据进行对比分析")
    print(f"  3. 运行情感分析和主题建模")
    print(f"  4. 比较 AI vs 非AI 的差异")

    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
