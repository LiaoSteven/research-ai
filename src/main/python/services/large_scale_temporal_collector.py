#!/usr/bin/env python3
"""
大规模时间序列数据采集器 (2022-2025)

采集策略：
1. 时间分层抽样：按季度均匀分布（2022Q1 - 2025Q4，共16个季度）
2. AI/非AI平衡：50% AI生成内容 vs 50% 传统内容
3. 关键时间节点重点采样：
   - 2022Q4: ChatGPT 发布（2022年11月）
   - 2023Q1-Q2: AI 工具爆发期
   - 2024-2025: AI 内容成熟期

目标：100,000 条评论
- 每季度：~6,250 条评论
- 每季度 AI 内容：~3,125 条
- 每季度非 AI 内容：~3,125 条

使用方法：
    python large_scale_temporal_collector.py --total 100000 --start-date 2022-01-01 --end-date 2025-10-31
"""

import sys
from pathlib import Path
import argparse
import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import random

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 导入模块
from src.main.python.services.youtube_collector import YouTubeCollector
from src.main.python.services.ai_comparison_collector import ComparisonCollector


class TemporalSamplingStrategy:
    """时间分层采样策略"""

    # 关键时间节点（AI 技术发展里程碑）
    KEY_MILESTONES = {
        '2022-11-30': 'ChatGPT Launch',
        '2023-03-14': 'GPT-4 Release',
        '2023-05-10': 'Google Bard Launch',
        '2024-02-15': 'Sora Announcement',
        '2024-05-13': 'GPT-4o Release'
    }

    def __init__(self, start_date: str, end_date: str, total_comments: int):
        """
        初始化采样策略

        Args:
            start_date: 起始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            total_comments: 目标总评论数
        """
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.total_comments = total_comments

        # 生成季度分布
        self.quarters = self._generate_quarters()
        self.sampling_plan = self._create_sampling_plan()

    def _generate_quarters(self) -> List[Dict]:
        """生成所有季度"""
        quarters = []
        current = self.start_date

        while current <= self.end_date:
            year = current.year
            month = current.month
            quarter = (month - 1) // 3 + 1

            # 计算季度的起止日期
            q_start = datetime(year, (quarter-1)*3 + 1, 1)
            if quarter < 4:
                q_end = datetime(year, quarter*3 + 1, 1) - timedelta(days=1)
            else:
                q_end = datetime(year, 12, 31)

            # 确保在采样范围内
            q_start = max(q_start, self.start_date)
            q_end = min(q_end, self.end_date)

            quarter_key = f"{year}Q{quarter}"
            quarters.append({
                'key': quarter_key,
                'year': year,
                'quarter': quarter,
                'start': q_start,
                'end': q_end,
                'is_milestone': self._is_milestone_quarter(q_start, q_end)
            })

            # 移动到下一个季度
            if quarter < 4:
                current = datetime(year, quarter*3 + 1, 1)
            else:
                current = datetime(year + 1, 1, 1)

        return quarters

    def _is_milestone_quarter(self, q_start: datetime, q_end: datetime) -> bool:
        """检查季度是否包含关键里程碑"""
        for milestone_date in self.KEY_MILESTONES.keys():
            m_date = datetime.strptime(milestone_date, '%Y-%m-%d')
            if q_start <= m_date <= q_end:
                return True
        return False

    def _create_sampling_plan(self) -> List[Dict]:
        """创建采样计划"""
        num_quarters = len(self.quarters)
        base_per_quarter = self.total_comments // num_quarters
        remainder = self.total_comments % num_quarters

        plan = []
        for idx, quarter_info in enumerate(self.quarters):
            # 为里程碑季度分配更多样本
            if quarter_info['is_milestone']:
                allocation = int(base_per_quarter * 1.2)  # 增加 20%
            else:
                allocation = base_per_quarter

            # 分配剩余样本
            if idx < remainder:
                allocation += 1

            # AI vs 非AI 分配 (50/50)
            ai_allocation = allocation // 2
            non_ai_allocation = allocation - ai_allocation

            plan.append({
                **quarter_info,
                'total_target': allocation,
                'ai_target': ai_allocation,
                'non_ai_target': non_ai_allocation,
                'collected_ai': 0,
                'collected_non_ai': 0
            })

        return plan

    def get_sampling_plan(self) -> List[Dict]:
        """获取完整采样计划"""
        return self.sampling_plan

    def print_plan(self):
        """打印采样计划"""
        print("\n" + "="*80)
        print(" 时间分层采样计划 (Temporal Stratified Sampling Plan)")
        print("="*80)
        print(f"\n📅 时间范围: {self.start_date.date()} 至 {self.end_date.date()}")
        print(f"🎯 目标评论数: {self.total_comments:,} 条")
        print(f"📊 季度数量: {len(self.quarters)}")
        print(f"⚖️ AI/非AI 比例: 50% / 50%")

        print("\n" + "-"*80)
        print(f"{'季度':<10} {'日期范围':<25} {'总数':<8} {'AI':<8} {'非AI':<8} {'里程碑':<10}")
        print("-"*80)

        total_ai = 0
        total_non_ai = 0

        for q in self.sampling_plan:
            milestone_mark = "⭐" if q['is_milestone'] else ""
            date_range = f"{q['start'].date()} ~ {q['end'].date()}"
            print(f"{q['key']:<10} {date_range:<25} {q['total_target']:<8} "
                  f"{q['ai_target']:<8} {q['non_ai_target']:<8} {milestone_mark:<10}")
            total_ai += q['ai_target']
            total_non_ai += q['non_ai_target']

        print("-"*80)
        print(f"{'总计':<10} {'':<25} {total_ai + total_non_ai:<8} "
              f"{total_ai:<8} {total_non_ai:<8}")
        print("="*80)

        # 显示关键里程碑
        print("\n⭐ 关键时间节点:")
        for date, event in self.KEY_MILESTONES.items():
            if self.start_date <= datetime.strptime(date, '%Y-%m-%d') <= self.end_date:
                print(f"   • {date}: {event}")
        print()


class LargeScaleTemporalCollector:
    """大规模时间序列采集器"""

    # 扩展的搜索关键词
    AI_SEARCH_QUERIES = [
        # AI 工具相关
        'AI generated shorts', 'AI art shorts', 'AI animation shorts',
        'midjourney shorts', 'stable diffusion shorts', 'dalle shorts',
        'AI video shorts', 'generative AI shorts', 'AI created shorts',

        # AI 技术讨论
        'ChatGPT shorts', 'GPT shorts', 'AI tutorial shorts',
        'machine learning shorts', 'AI demo shorts',

        # 年份特定搜索 (用于时间过滤)
        'AI shorts 2022', 'AI shorts 2023', 'AI shorts 2024', 'AI shorts 2025',
    ]

    NON_AI_SEARCH_QUERIES = [
        # 传统创作
        'handmade shorts', 'traditional art shorts', 'hand drawn shorts',
        'real footage shorts', 'filmed shorts', 'photography shorts',

        # 人工创作内容
        'vlog shorts', 'cooking shorts', 'DIY shorts', 'tutorial shorts',
        'gaming shorts', 'music shorts', 'dance shorts', 'sports shorts',

        # 年份特定搜索
        'vlog 2022', 'vlog 2023', 'vlog 2024', 'vlog 2025',
        'cooking 2022', 'cooking 2023', 'cooking 2024', 'cooking 2025',
    ]

    def __init__(self, api_key: str, sampling_strategy: TemporalSamplingStrategy):
        """
        初始化采集器

        Args:
            api_key: YouTube API 密钥
            sampling_strategy: 采样策略
        """
        self.api_key = api_key
        self.strategy = sampling_strategy
        self.comparison_collector = ComparisonCollector(api_key)
        self.youtube = self.comparison_collector.youtube

        # 进度跟踪
        self.progress = {
            'total_collected': 0,
            'ai_collected': 0,
            'non_ai_collected': 0,
            'quarters_completed': 0
        }

    def search_videos_by_date(
        self,
        queries: List[str],
        after_date: datetime,
        before_date: datetime,
        max_results: int = 50,
        video_type: str = 'ai'
    ) -> List[str]:
        """
        按日期范围搜索视频

        Args:
            queries: 搜索关键词列表
            after_date: 起始日期
            before_date: 结束日期
            max_results: 最多返回视频数
            video_type: 'ai' 或 'non_ai'

        Returns:
            视频 ID 列表
        """
        video_ids = []
        found_videos = set()

        # RFC 3339 格式的日期时间
        published_after = after_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        published_before = before_date.strftime('%Y-%m-%dT%H:%M:%SZ')

        print(f"\n🔍 搜索 {video_type.upper()} 视频...")
        print(f"   时间范围: {after_date.date()} ~ {before_date.date()}")

        for query in queries:
            if len(video_ids) >= max_results:
                break

            try:
                search_params = {
                    'part': 'id,snippet',
                    'type': 'video',
                    'q': query,
                    'videoDuration': 'short',
                    'publishedAfter': published_after,
                    'publishedBefore': published_before,
                    'maxResults': min(50, max_results - len(video_ids)),
                    'order': 'relevance',
                    'regionCode': 'US'
                }

                request = self.youtube.search().list(**search_params)
                response = request.execute()

                for item in response.get('items', []):
                    if 'videoId' in item['id']:
                        video_id = item['id']['videoId']
                        if video_id not in found_videos:
                            found_videos.add(video_id)
                            video_ids.append(video_id)

                time.sleep(1)  # API 限流

            except Exception as e:
                print(f"   ✗ 搜索错误: {e}")
                continue

        print(f"   ✓ 找到 {len(video_ids)} 个视频")
        return video_ids

    def collect_quarter(self, quarter_plan: Dict) -> Tuple[List, List]:
        """
        采集单个季度的数据

        Args:
            quarter_plan: 季度采样计划

        Returns:
            (ai_comments, non_ai_comments)
        """
        print("\n" + "="*80)
        print(f" 采集季度: {quarter_plan['key']}")
        print("="*80)
        print(f" 日期: {quarter_plan['start'].date()} ~ {quarter_plan['end'].date()}")
        print(f" 目标: AI {quarter_plan['ai_target']} 条 + 非AI {quarter_plan['non_ai_target']} 条")
        if quarter_plan['is_milestone']:
            print(" ⭐ 里程碑季度 - 重点采样")
        print("="*80)

        # 1. 采集 AI 内容
        print("\n[1/2] 采集 AI 内容...")
        ai_videos = self.search_videos_by_date(
            self.AI_SEARCH_QUERIES,
            quarter_plan['start'],
            quarter_plan['end'],
            max_results=quarter_plan['ai_target'] // 20,  # 假设每视频20条评论
            video_type='ai'
        )

        ai_comments, _ = self.comparison_collector.collect_with_detection(
            target_type='ai',
            max_comments=quarter_plan['ai_target'],
            per_video=20,
            region='US',
            verify_threshold=0.3
        )

        # 为评论添加季度标签
        for comment in ai_comments:
            comment['quarter'] = quarter_plan['key']
            comment['year'] = quarter_plan['year']
            comment['is_milestone_quarter'] = quarter_plan['is_milestone']

        # 2. 采集非 AI 内容
        print("\n[2/2] 采集非 AI 内容...")
        non_ai_videos = self.search_videos_by_date(
            self.NON_AI_SEARCH_QUERIES,
            quarter_plan['start'],
            quarter_plan['end'],
            max_results=quarter_plan['non_ai_target'] // 20,
            video_type='non_ai'
        )

        non_ai_comments, _ = self.comparison_collector.collect_with_detection(
            target_type='non_ai',
            max_comments=quarter_plan['non_ai_target'],
            per_video=20,
            region='US',
            verify_threshold=0.3
        )

        # 为评论添加季度标签
        for comment in non_ai_comments:
            comment['quarter'] = quarter_plan['key']
            comment['year'] = quarter_plan['year']
            comment['is_milestone_quarter'] = quarter_plan['is_milestone']

        # 更新进度
        quarter_plan['collected_ai'] = len(ai_comments)
        quarter_plan['collected_non_ai'] = len(non_ai_comments)
        self.progress['ai_collected'] += len(ai_comments)
        self.progress['non_ai_collected'] += len(non_ai_comments)
        self.progress['total_collected'] += len(ai_comments) + len(non_ai_comments)
        self.progress['quarters_completed'] += 1

        print(f"\n✅ {quarter_plan['key']} 完成:")
        print(f"   AI: {len(ai_comments)} 条")
        print(f"   非AI: {len(non_ai_comments)} 条")
        print(f"   总计: {len(ai_comments) + len(non_ai_comments)} 条")

        return ai_comments, non_ai_comments

    def collect_all(self, output_dir: Path, checkpoint_interval: int = 1) -> Dict:
        """
        采集所有数据

        Args:
            output_dir: 输出目录
            checkpoint_interval: 检查点间隔（每N个季度保存一次）

        Returns:
            采集结果统计
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        all_ai_comments = []
        all_non_ai_comments = []
        sampling_plan = self.strategy.get_sampling_plan()

        print("\n" + "="*80)
        print(" 开始大规模数据采集")
        print("="*80)

        for idx, quarter_plan in enumerate(sampling_plan, 1):
            print(f"\n进度: [{idx}/{len(sampling_plan)}] 季度")

            try:
                ai_comments, non_ai_comments = self.collect_quarter(quarter_plan)
                all_ai_comments.extend(ai_comments)
                all_non_ai_comments.extend(non_ai_comments)

                # 定期保存检查点
                if idx % checkpoint_interval == 0:
                    self._save_checkpoint(
                        output_dir,
                        all_ai_comments,
                        all_non_ai_comments,
                        quarter_plan['key']
                    )

                # 显示总体进度
                self._print_progress()

            except Exception as e:
                print(f"\n❌ 季度 {quarter_plan['key']} 采集失败: {e}")
                continue

        # 保存最终结果
        final_result = self._save_final_results(
            output_dir,
            all_ai_comments,
            all_non_ai_comments,
            sampling_plan
        )

        return final_result

    def _save_checkpoint(
        self,
        output_dir: Path,
        ai_comments: List,
        non_ai_comments: List,
        checkpoint_name: str
    ):
        """保存检查点"""
        checkpoint_file = output_dir / f'checkpoint_{checkpoint_name}.json'
        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'progress': self.progress,
            'ai_comments_count': len(ai_comments),
            'non_ai_comments_count': len(non_ai_comments),
            'ai_comments': ai_comments,
            'non_ai_comments': non_ai_comments
        }

        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 检查点已保存: {checkpoint_file}")

    def _save_final_results(
        self,
        output_dir: Path,
        ai_comments: List,
        non_ai_comments: List,
        sampling_plan: List[Dict]
    ) -> Dict:
        """保存最终结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存评论数据
        ai_file = output_dir / f'comments_ai_2022-2025_{timestamp}.json'
        non_ai_file = output_dir / f'comments_non_ai_2022-2025_{timestamp}.json'
        all_file = output_dir / f'comments_all_2022-2025_{timestamp}.json'

        with open(ai_file, 'w', encoding='utf-8') as f:
            json.dump(ai_comments, f, ensure_ascii=False, indent=2)

        with open(non_ai_file, 'w', encoding='utf-8') as f:
            json.dump(non_ai_comments, f, ensure_ascii=False, indent=2)

        all_comments = ai_comments + non_ai_comments
        with open(all_file, 'w', encoding='utf-8') as f:
            json.dump(all_comments, f, ensure_ascii=False, indent=2)

        # 保存采样计划和元数据
        metadata_file = output_dir / f'sampling_metadata_{timestamp}.json'
        metadata = {
            'collection_timestamp': datetime.now().isoformat(),
            'total_comments': len(all_comments),
            'ai_comments': len(ai_comments),
            'non_ai_comments': len(non_ai_comments),
            'quarters_covered': len(sampling_plan),
            'sampling_plan': sampling_plan,
            'progress': self.progress,
            'files': {
                'ai_comments': str(ai_file),
                'non_ai_comments': str(non_ai_file),
                'all_comments': str(all_file)
            }
        }

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # 打印最终报告
        self._print_final_report(metadata)

        return metadata

    def _print_progress(self):
        """打印当前进度"""
        total_target = self.strategy.total_comments
        collected = self.progress['total_collected']
        percentage = (collected / total_target * 100) if total_target > 0 else 0

        print(f"\n📊 总体进度:")
        print(f"   已采集: {collected:,} / {total_target:,} ({percentage:.1f}%)")
        print(f"   AI 内容: {self.progress['ai_collected']:,}")
        print(f"   非 AI: {self.progress['non_ai_collected']:,}")
        print(f"   完成季度: {self.progress['quarters_completed']}/{len(self.strategy.quarters)}")

    def _print_final_report(self, metadata: Dict):
        """打印最终报告"""
        print("\n" + "="*80)
        print(" 采集完成！")
        print("="*80)
        print(f"\n📊 采集统计:")
        print(f"   总评论数: {metadata['total_comments']:,}")
        print(f"   AI 内容: {metadata['ai_comments']:,} ({metadata['ai_comments']/metadata['total_comments']*100:.1f}%)")
        print(f"   非 AI: {metadata['non_ai_comments']:,} ({metadata['non_ai_comments']/metadata['total_comments']*100:.1f}%)")
        print(f"   季度覆盖: {metadata['quarters_covered']} 个季度")

        print(f"\n💾 文件保存:")
        print(f"   AI 评论: {metadata['files']['ai_comments']}")
        print(f"   非 AI 评论: {metadata['files']['non_ai_comments']}")
        print(f"   全部评论: {metadata['files']['all_comments']}")

        print(f"\n✨ 下一步:")
        print(f"   1. 数据预处理: python scripts/preprocess_large_scale.py")
        print(f"   2. 情感分析: python scripts/run_sentiment_analysis.py")
        print(f"   3. 主题建模: python scripts/run_topic_modeling.py")
        print(f"   4. 时间序列分析: python scripts/run_time_series_analysis.py")
        print(f"   5. AI vs 非AI 对比: python scripts/compare_ai_vs_nonai.py")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='大规模时间序列数据采集器 (2022-2025)'
    )
    parser.add_argument('--total', type=int, default=100000,
                       help='目标总评论数 (默认 100,000)')
    parser.add_argument('--start-date', type=str, default='2022-01-01',
                       help='起始日期 YYYY-MM-DD (默认 2022-01-01)')
    parser.add_argument('--end-date', type=str, default='2025-10-31',
                       help='结束日期 YYYY-MM-DD (默认 2025-10-31)')
    parser.add_argument('--checkpoint-interval', type=int, default=1,
                       help='检查点保存间隔（季度数，默认 1）')
    parser.add_argument('--output-dir', type=str, default='data/raw',
                       help='输出目录 (默认 data/raw)')

    args = parser.parse_args()

    print("\n" + "="*80)
    print(" YouTube Shorts 大规模时间序列数据采集")
    print(" Large-Scale Temporal Data Collection (2022-2025)")
    print("="*80)

    # 检查 API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("\n❌ 错误：未找到 YouTube API 密钥")
        print("请在 .env 文件中设置 YOUTUBE_API_KEY")
        return 1

    # 创建采样策略
    strategy = TemporalSamplingStrategy(
        start_date=args.start_date,
        end_date=args.end_date,
        total_comments=args.total
    )

    # 显示采样计划
    strategy.print_plan()

    # 确认开始
    print("\n⚠️ 注意:")
    print(f"   • 此采集将消耗大量 YouTube API 配额")
    print(f"   • 预计耗时: 数小时到数天（取决于 API 限流）")
    print(f"   • 检查点将每 {args.checkpoint_interval} 个季度保存一次")

    response = input("\n是否开始采集？(yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("已取消")
        return 0

    # 初始化采集器
    try:
        collector = LargeScaleTemporalCollector(
            api_key=api_key,
            sampling_strategy=strategy
        )
        print("\n✅ YouTube API 连接成功")
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        return 1

    # 开始采集
    output_dir = Path(args.output_dir)
    try:
        result = collector.collect_all(
            output_dir=output_dir,
            checkpoint_interval=args.checkpoint_interval
        )
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断采集")
        print("检查点文件已保存，可以稍后继续")
        return 1
    except Exception as e:
        print(f"\n❌ 采集失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
