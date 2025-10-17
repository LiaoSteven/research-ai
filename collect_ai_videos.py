#!/usr/bin/env python3
"""
采集 AI 生成内容视频的评论

专门搜索和采集 AI 相关视频（AI generated, AI art, AI music 等）的评论

使用方法：
    python collect_ai_videos.py --max-comments 1000
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


class AIVideoCollector:
    """专门采集 AI 相关视频评论"""

    # AI 相关搜索关键词
    AI_KEYWORDS = [
        'AI generated',
        'AI art',
        'AI music',
        'AI animation',
        'AI video',
        'artificial intelligence',
        'midjourney',
        'stable diffusion',
        'dall-e',
        'chatgpt',
        'AI created',
        'made with AI',
        'AI assisted',
        'generative AI',
        'AI shorts',
        'AI content'
    ]

    # 非 AI 关键词（用于对照组）
    NON_AI_KEYWORDS = [
        'handmade',
        'hand drawn',
        'traditional art',
        'real footage',
        'live action',
        'filmed',
        'recorded',
        'original content',
        'human made'
    ]

    def __init__(self, api_key: str):
        """初始化采集器"""
        self.collector = YouTubeCollector(api_key=api_key)
        self.youtube = self.collector.youtube

    def search_ai_videos(
        self,
        max_results: int = 50,
        keywords: list = None,
        region: str = 'US'
    ) -> list:
        """
        搜索 AI 相关视频

        Args:
            max_results: 最多返回多少个视频
            keywords: 搜索关键词列表
            region: 地区代码

        Returns:
            视频 ID 列表
        """
        if keywords is None:
            keywords = self.AI_KEYWORDS

        video_ids = []
        found_videos = set()

        print(f"\n🤖 搜索 AI 相关视频...")
        print(f"   关键词数量: {len(keywords)}")
        print(f"   地区: {region}")

        for keyword in keywords:
            if len(video_ids) >= max_results:
                break

            print(f"\n   搜索关键词: '{keyword}'")

            try:
                # 构建搜索参数
                search_params = {
                    'part': 'id,snippet',
                    'type': 'video',
                    'q': f'{keyword} shorts',
                    'videoDuration': 'short',  # 短视频
                    'maxResults': 10,
                    'order': 'relevance',
                    'regionCode': region,
                    'relevanceLanguage': 'en'  # 英文内容
                }

                request = self.youtube.search().list(**search_params)
                response = request.execute()

                for item in response.get('items', []):
                    if 'videoId' in item['id']:
                        video_id = item['id']['videoId']
                        if video_id not in found_videos:
                            found_videos.add(video_id)
                            video_ids.append(video_id)
                            print(f"      ✓ 找到: {video_id}")

                time.sleep(1)  # 速率限制

            except Exception as e:
                print(f"      ✗ 搜索错误: {e}")
                continue

        print(f"\n✅ 共找到 {len(video_ids)} 个 AI 相关视频")
        return video_ids[:max_results]

    def verify_ai_content(self, video_id: str) -> dict:
        """
        验证视频是否真的是 AI 内容

        通过标题、描述、标签来判断

        Args:
            video_id: 视频 ID

        Returns:
            包含验证结果的字典
        """
        try:
            video_info = self.collector.get_video_info(video_id)

            # 检查标题和描述中的 AI 关键词
            title_lower = video_info['title'].lower()
            desc_lower = video_info.get('description', '').lower()
            tags = video_info.get('tags', [])

            ai_indicators = 0
            found_keywords = []

            # 检查标题
            for keyword in self.AI_KEYWORDS:
                if keyword.lower() in title_lower:
                    ai_indicators += 2  # 标题权重更高
                    found_keywords.append(f"title:{keyword}")

            # 检查描述
            for keyword in self.AI_KEYWORDS:
                if keyword.lower() in desc_lower:
                    ai_indicators += 1
                    found_keywords.append(f"desc:{keyword}")

            # 检查标签
            for tag in tags:
                if any(kw.lower() in tag.lower() for kw in ['ai', 'artificial', 'generated']):
                    ai_indicators += 1
                    found_keywords.append(f"tag:{tag}")

            is_likely_ai = ai_indicators >= 2

            return {
                'video_id': video_id,
                'is_likely_ai': is_likely_ai,
                'confidence': min(ai_indicators / 5, 1.0),  # 0-1 置信度
                'ai_indicators': ai_indicators,
                'found_keywords': found_keywords,
                'title': video_info['title']
            }

        except Exception as e:
            print(f"   ⚠️  验证失败: {e}")
            return {
                'video_id': video_id,
                'is_likely_ai': False,
                'confidence': 0.0,
                'ai_indicators': 0,
                'found_keywords': [],
                'error': str(e)
            }


def main():
    parser = argparse.ArgumentParser(description='采集 AI 生成内容视频评论')
    parser.add_argument('--max-comments', type=int, default=1000,
                       help='总共采集多少条评论（默认 1000）')
    parser.add_argument('--per-video', type=int, default=50,
                       help='每个视频采集多少条评论（默认 50）')
    parser.add_argument('--region', type=str, default='US',
                       help='地区代码（默认 US）')
    parser.add_argument('--type', type=str, default='ai',
                       choices=['ai', 'non_ai'],
                       help='采集类型：ai=AI生成内容，non_ai=非AI内容')
    parser.add_argument('--verify', action='store_true',
                       help='验证视频是否真的是 AI 内容')

    args = parser.parse_args()

    print("\n" + "="*70)
    print(" AI 视频评论采集工具")
    print("="*70 + "\n")

    # 检查 API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ 错误：未找到 YouTube API 密钥")
        print("\n请在 .env 文件中设置 YOUTUBE_API_KEY")
        return 1

    # 初始化采集器
    try:
        ai_collector = AIVideoCollector(api_key=api_key)
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
    print(f"   采集类型：{args.type}")
    print(f"   地区代码：{args.region}")
    print(f"   验证模式：{'开启' if args.verify else '关闭'}")

    # 选择搜索关键词
    if args.type == 'ai':
        keywords = ai_collector.AI_KEYWORDS
        label = 'ai_generated'
    else:
        keywords = ai_collector.NON_AI_KEYWORDS
        label = 'non_ai'

    # 搜索视频
    video_ids = ai_collector.search_ai_videos(
        max_results=videos_needed * 2,  # 多搜索一些，因为有些可能不合格
        keywords=keywords,
        region=args.region
    )

    if not video_ids:
        print("❌ 没有找到视频")
        return 1

    # 验证视频（如果启用）
    verified_videos = []
    if args.verify:
        print(f"\n🔍 验证视频内容...")
        for video_id in video_ids:
            result = ai_collector.verify_ai_content(video_id)
            if result['is_likely_ai']:
                verified_videos.append(result)
                print(f"   ✓ {result['video_id']}: {result['title'][:50]}...")
                print(f"      置信度: {result['confidence']:.2f}, 指标: {result['ai_indicators']}")
            else:
                print(f"   ✗ {result['video_id']}: 不确定是 AI 内容")

            if len(verified_videos) >= videos_needed:
                break

        video_ids = [v['video_id'] for v in verified_videos]
        print(f"\n✅ 验证通过 {len(video_ids)} 个视频")

    if not video_ids:
        print("❌ 没有通过验证的视频")
        return 1

    print(f"\n🎬 准备从 {len(video_ids[:videos_needed])} 个视频中采集评论...\n")

    # 采集评论
    all_comments = []
    video_info_list = []

    for idx, video_id in enumerate(video_ids[:videos_needed], 1):
        if len(all_comments) >= args.max_comments:
            print(f"\n✅ 已达到目标评论数 {args.max_comments}，停止采集")
            break

        print(f"[{idx}/{min(len(video_ids), videos_needed)}] 处理视频: {video_id}")

        try:
            # 获取视频信息
            video_info = ai_collector.collector.get_video_info(video_id)
            video_info['video_type'] = label
            video_info['region'] = args.region

            title = video_info['title'][:40] + "..." if len(video_info['title']) > 40 else video_info['title']
            print(f"  标题: {title}")
            print(f"  评论数: {video_info['comment_count']}")

            video_info_list.append(video_info)

            # 获取评论
            comments = ai_collector.collector.get_video_comments(
                video_id,
                max_comments=args.per_video,
                include_replies=True
            )

            # 添加标签
            for comment in comments:
                comment['video_type'] = label
                comment['region'] = args.region

            all_comments.extend(comments)
            print(f"  ✓ 采集了 {len(comments)} 条评论（总计: {len(all_comments)}）")

            time.sleep(1)

        except Exception as e:
            print(f"  ✗ 采集失败: {e}")
            continue

    # 保存结果
    if all_comments:
        output_dir = Path('data/raw')
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comments_file = output_dir / f'comments_{label}_{timestamp}.json'
        videos_file = output_dir / f'videos_{label}_{timestamp}.json'

        with open(comments_file, 'w', encoding='utf-8') as f:
            json.dump(all_comments, f, ensure_ascii=False, indent=2)

        with open(videos_file, 'w', encoding='utf-8') as f:
            json.dump(video_info_list, f, ensure_ascii=False, indent=2)

        print("\n" + "="*70)
        print(" 采集完成！")
        print("="*70)
        print(f"\n📊 统计信息：")
        print(f"  总评论数：{len(all_comments)}")
        print(f"  处理视频：{len(video_info_list)}")
        print(f"  类型标签：{label}")
        print(f"  地区：{args.region}")

        print(f"\n💾 文件保存位置：")
        print(f"  评论数据：{comments_file}")
        print(f"  视频信息：{videos_file}")

        print(f"\n📝 评论样本（前 3 条）：")
        for i, comment in enumerate(all_comments[:3], 1):
            text = comment['text'][:60] + "..." if len(comment['text']) > 60 else comment['text']
            print(f"  {i}. {comment['author']}: {text}")

        print("\n✨ 下一步：")
        print(f"  1. 采集对照组：")
        if args.type == 'ai':
            print(f"     python collect_ai_videos.py --type non_ai --max-comments {args.max_comments}")
        else:
            print(f"     python collect_ai_videos.py --type ai --max-comments {args.max_comments}")
        print(f"  2. 预处理数据：python scripts/preprocess_data.py --input {comments_file}")
        print(f"  3. 对比分析：比较 ai_generated vs non_ai 的情感和主题差异")

        print()
        return 0
    else:
        print("\n❌ 没有采集到任何评论")
        return 1


if __name__ == '__main__':
    sys.exit(main())
