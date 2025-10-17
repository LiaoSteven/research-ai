#!/usr/bin/env python3
"""
检测 YouTube 视频是否包含 AI 生成内容

使用 YouTube Data API v3 检查视频的描述、标签和元数据，
判断视频是否声明包含 AI/合成内容

使用方法：
    python detect_ai_content.py VIDEO_ID
    python detect_ai_content.py --file video_ids.txt
"""

import sys
import os
import argparse
from pathlib import Path

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class AIContentDetector:
    """检测视频中的 AI 生成内容"""

    # YouTube 官方 AI 标注关键词（多语言）
    AI_DISCLOSURE_KEYWORDS = {
        'chinese': [
            '此影片包含變造或合成內容',
            '此视频包含变造或合成内容',
            'AI 生成',
            '人工智能生成',
            '合成内容',
            '變造內容'
        ],
        'english': [
            'altered or synthetic content',
            'AI-generated',
            'AI generated',
            'synthetic content',
            'artificially generated',
            'created with AI',
            'made with AI',
            'AI-created'
        ],
        'spanish': [
            'contenido alterado o sintético',
            'generado por IA',
            'contenido sintético'
        ],
        'japanese': [
            '変更または合成されたコンテンツ',
            'AI生成',
            '合成コンテンツ'
        ]
    }

    # 常见 AI 工具和平台名称
    AI_TOOLS = [
        'midjourney',
        'stable diffusion',
        'dall-e',
        'dalle',
        'chatgpt',
        'gpt-4',
        'runway',
        'synthesia',
        'pictory',
        'invideo',
        'fliki',
        'lumen5',
        'descript',
        'wonder dynamics',
        'pika labs',
        'gen-2',
        'firefly',
        'adobe firefly',
        'bing image creator',
        'leonardo ai'
    ]

    # AI 内容相关标签
    AI_TAGS = [
        'ai',
        'artificial intelligence',
        'ai generated',
        'ai art',
        'generative ai',
        'machine learning',
        'neural network',
        'text to image',
        'text to video',
        'ai animation'
    ]

    def __init__(self, api_key: str):
        """
        初始化检测器

        Args:
            api_key: YouTube Data API v3 密钥
        """
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_video_metadata(self, video_id: str) -> dict:
        """
        获取视频完整元数据

        Args:
            video_id: YouTube 视频 ID

        Returns:
            包含视频元数据的字典
        """
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics,status',
                id=video_id
            )
            response = request.execute()

            if not response.get('items'):
                return None

            video = response['items'][0]
            snippet = video['snippet']

            return {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'view_count': video['statistics'].get('viewCount', 0),
                'like_count': video['statistics'].get('likeCount', 0),
                'comment_count': video['statistics'].get('commentCount', 0),
                'duration': video['contentDetails'].get('duration', ''),
                'made_for_kids': video['status'].get('madeForKids', False)
            }

        except HttpError as e:
            print(f"❌ API 错误: {e}")
            return None
        except Exception as e:
            print(f"❌ 错误: {e}")
            return None

    def detect_ai_content(self, video_id: str, verbose: bool = True) -> dict:
        """
        检测视频是否包含 AI 生成内容

        Args:
            video_id: YouTube 视频 ID
            verbose: 是否显示详细信息

        Returns:
            检测结果字典
        """
        metadata = self.get_video_metadata(video_id)

        if not metadata:
            return {
                'video_id': video_id,
                'is_ai_content': False,
                'confidence': 0.0,
                'error': 'Failed to fetch metadata'
            }

        title = metadata['title'].lower()
        description = metadata['description'].lower()
        tags = [tag.lower() for tag in metadata['tags']]

        # 检测结果
        indicators = {
            'official_disclosure': False,
            'ai_tools_mentioned': [],
            'ai_keywords_in_title': [],
            'ai_keywords_in_description': [],
            'ai_tags': [],
            'confidence_score': 0.0
        }

        score = 0

        # 1. 检查官方 AI 内容声明（最高权重）
        for lang, keywords in self.AI_DISCLOSURE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in description or keyword.lower() in title:
                    indicators['official_disclosure'] = True
                    score += 50  # 官方声明权重非常高
                    if verbose:
                        print(f"   ✓ 发现官方声明: '{keyword}' ({lang})")
                    break

        # 2. 检查 AI 工具名称
        for tool in self.AI_TOOLS:
            if tool in title or tool in description:
                indicators['ai_tools_mentioned'].append(tool)
                score += 10
                if verbose:
                    print(f"   ✓ 发现 AI 工具: {tool}")

        # 3. 检查标题中的 AI 关键词
        ai_keywords = ['ai', 'artificial intelligence', 'generated', 'synthetic']
        for keyword in ai_keywords:
            if keyword in title:
                indicators['ai_keywords_in_title'].append(keyword)
                score += 8  # 标题权重较高
                if verbose:
                    print(f"   ✓ 标题包含: {keyword}")

        # 4. 检查描述中的 AI 关键词
        for keyword in ai_keywords:
            if keyword in description:
                indicators['ai_keywords_in_description'].append(keyword)
                score += 3
                if verbose:
                    print(f"   ✓ 描述包含: {keyword}")

        # 5. 检查标签
        for tag in tags:
            if any(ai_tag in tag for ai_tag in self.AI_TAGS):
                indicators['ai_tags'].append(tag)
                score += 5
                if verbose:
                    print(f"   ✓ AI 相关标签: {tag}")

        # 计算置信度 (0-1)
        confidence = min(score / 100.0, 1.0)
        indicators['confidence_score'] = confidence

        # 判断是否为 AI 内容（置信度 > 0.3）
        is_ai_content = confidence >= 0.3

        result = {
            'video_id': video_id,
            'title': metadata['title'],
            'channel': metadata['channel_title'],
            'is_ai_content': is_ai_content,
            'confidence': confidence,
            'score': score,
            'indicators': indicators,
            'view_count': metadata['view_count'],
            'like_count': metadata['like_count'],
            'comment_count': metadata['comment_count']
        }

        return result

    def batch_detect(self, video_ids: list, verbose: bool = False) -> list:
        """
        批量检测多个视频

        Args:
            video_ids: 视频 ID 列表
            verbose: 是否显示详细信息

        Returns:
            检测结果列表
        """
        results = []

        for i, video_id in enumerate(video_ids, 1):
            print(f"\n[{i}/{len(video_ids)}] 检测视频: {video_id}")
            result = self.detect_ai_content(video_id, verbose=verbose)
            results.append(result)

            if result['is_ai_content']:
                print(f"   🤖 AI 内容 (置信度: {result['confidence']:.2f})")
            else:
                print(f"   👤 非 AI 内容 (置信度: {result['confidence']:.2f})")

        return results


def main():
    parser = argparse.ArgumentParser(description='检测 YouTube 视频是否包含 AI 生成内容')
    parser.add_argument('video_id', nargs='?', help='YouTube 视频 ID')
    parser.add_argument('--file', help='包含视频 ID 的文件（每行一个）')
    parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    parser.add_argument('--output', '-o', help='保存结果到 JSON 文件')

    args = parser.parse_args()

    if not args.video_id and not args.file:
        parser.print_help()
        return 1

    print("\n" + "="*70)
    print(" YouTube AI 内容检测工具")
    print("="*70)

    # 检查 API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("\n❌ 错误：未找到 YouTube API 密钥")
        print("请在 .env 文件中设置 YOUTUBE_API_KEY")
        return 1

    # 初始化检测器
    try:
        detector = AIContentDetector(api_key)
        print("\n✅ YouTube API 连接成功")
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        return 1

    # 收集视频 ID
    video_ids = []
    if args.video_id:
        video_ids.append(args.video_id)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                video_ids = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"\n❌ 文件不存在: {args.file}")
            return 1

    print(f"\n📊 准备检测 {len(video_ids)} 个视频\n")

    # 执行检测
    results = detector.batch_detect(video_ids, verbose=args.verbose)

    # 统计结果
    ai_count = sum(1 for r in results if r['is_ai_content'])
    non_ai_count = len(results) - ai_count

    print("\n" + "="*70)
    print(" 检测结果统计")
    print("="*70)
    print(f"\n总视频数: {len(results)}")
    print(f"AI 内容: {ai_count} ({ai_count/len(results)*100:.1f}%)")
    print(f"非 AI 内容: {non_ai_count} ({non_ai_count/len(results)*100:.1f}%)")

    # 显示 AI 内容列表
    if ai_count > 0:
        print(f"\n🤖 检测到的 AI 内容视频:")
        for result in results:
            if result['is_ai_content']:
                print(f"\n  视频 ID: {result['video_id']}")
                print(f"  标题: {result['title'][:60]}...")
                print(f"  置信度: {result['confidence']:.2f}")
                print(f"  指标:")
                ind = result['indicators']
                if ind['official_disclosure']:
                    print(f"    ✓ 官方 AI 内容声明")
                if ind['ai_tools_mentioned']:
                    print(f"    ✓ AI 工具: {', '.join(ind['ai_tools_mentioned'][:3])}")
                if ind['ai_tags']:
                    print(f"    ✓ AI 标签: {', '.join(ind['ai_tags'][:3])}")

    # 保存结果
    if args.output:
        import json
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n💾 结果已保存到: {output_path}")

    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
