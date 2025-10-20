#!/usr/bin/env python3
"""
预览采样计划 - 查看详细的季度分配策略
"""

from datetime import datetime, timedelta
from typing import List, Dict

# 复制关键类定义
class TemporalSamplingStrategy:
    """时间分层采样策略"""

    KEY_MILESTONES = {
        '2022-11-30': 'ChatGPT Launch',
        '2023-03-14': 'GPT-4 Release',
        '2023-05-10': 'Google Bard Launch',
        '2024-02-15': 'Sora Announcement',
        '2024-05-13': 'GPT-4o Release'
    }

    def __init__(self, start_date: str, end_date: str, total_comments: int):
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.total_comments = total_comments
        self.quarters = self._generate_quarters()
        self.sampling_plan = self._create_sampling_plan()

    def _generate_quarters(self) -> List[Dict]:
        quarters = []
        current = self.start_date

        while current <= self.end_date:
            year = current.year
            month = current.month
            quarter = (month - 1) // 3 + 1

            q_start = datetime(year, (quarter-1)*3 + 1, 1)
            if quarter < 4:
                q_end = datetime(year, quarter*3 + 1, 1) - timedelta(days=1)
            else:
                q_end = datetime(year, 12, 31)

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

            if quarter < 4:
                current = datetime(year, quarter*3 + 1, 1)
            else:
                current = datetime(year + 1, 1, 1)

        return quarters

    def _is_milestone_quarter(self, q_start: datetime, q_end: datetime) -> bool:
        for milestone_date in self.KEY_MILESTONES.keys():
            m_date = datetime.strptime(milestone_date, '%Y-%m-%d')
            if q_start <= m_date <= q_end:
                return True
        return False

    def _create_sampling_plan(self) -> List[Dict]:
        num_quarters = len(self.quarters)
        base_per_quarter = self.total_comments // num_quarters
        remainder = self.total_comments % num_quarters

        plan = []
        for idx, quarter_info in enumerate(self.quarters):
            if quarter_info['is_milestone']:
                allocation = int(base_per_quarter * 1.2)
            else:
                allocation = base_per_quarter

            if idx < remainder:
                allocation += 1

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
        return self.sampling_plan

    def print_plan(self):
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

        print("\n⭐ 关键时间节点:")
        for date, event in self.KEY_MILESTONES.items():
            if self.start_date <= datetime.strptime(date, '%Y-%m-%d') <= self.end_date:
                print(f"   • {date}: {event}")
        print()


def main():
    print("\n" + "="*80)
    print(" 采样计划预览")
    print("="*80)

    # 创建采样策略
    strategy = TemporalSamplingStrategy(
        start_date='2022-01-01',
        end_date='2025-10-31',
        total_comments=100000
    )

    # 显示计划
    strategy.print_plan()

    # 额外统计
    plan = strategy.get_sampling_plan()

    print("\n📊 额外统计:")
    print("-"*80)

    # 按年度汇总
    yearly_stats = {}
    for q in plan:
        year = q['year']
        if year not in yearly_stats:
            yearly_stats[year] = {'total': 0, 'ai': 0, 'non_ai': 0, 'quarters': 0}
        yearly_stats[year]['total'] += q['total_target']
        yearly_stats[year]['ai'] += q['ai_target']
        yearly_stats[year]['non_ai'] += q['non_ai_target']
        yearly_stats[year]['quarters'] += 1

    print("\n年度汇总:")
    print(f"{'年份':<8} {'季度数':<8} {'总评论':<10} {'AI':<10} {'非AI':<10}")
    print("-"*80)
    for year in sorted(yearly_stats.keys()):
        stats = yearly_stats[year]
        print(f"{year:<8} {stats['quarters']:<8} {stats['total']:<10,} "
              f"{stats['ai']:<10,} {stats['non_ai']:<10,}")

    # 里程碑季度统计
    milestone_quarters = [q for q in plan if q['is_milestone']]
    regular_quarters = [q for q in plan if not q['is_milestone']]

    milestone_total = sum(q['total_target'] for q in milestone_quarters)
    regular_total = sum(q['total_target'] for q in regular_quarters)

    print(f"\n里程碑季度 vs 常规季度:")
    print(f"  里程碑季度: {len(milestone_quarters)} 个, {milestone_total:,} 条评论")
    print(f"  常规季度: {len(regular_quarters)} 个, {regular_total:,} 条评论")

    print("\n" + "="*80)
    print("✅ 预览完成")
    print("="*80)
    print("\n准备开始采集?")
    print("  运行: bash scripts/collect_100k_comments.sh")
    print()

if __name__ == '__main__':
    main()
