#!/usr/bin/env python3
"""
时间序列分析脚本

分析 2022-2025 年间观众对 YouTube Shorts 评论的情感、主题、互动模式的时间演变

Usage:
    python scripts/analyze_time_series.py \
        --input data/processed/comments_sentiment_topics.csv \
        --output output/figures
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def load_and_prepare_data(input_file: str) -> pd.DataFrame:
    """
    加载数据并准备时间序列分析

    Args:
        input_file: 输入 CSV 文件路径

    Returns:
        处理后的 DataFrame
    """
    print(f"\n📊 加载数据: {input_file}")

    df = pd.read_csv(input_file)

    # 转换时间字段
    if 'published_at' in df.columns:
        df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')

    # 提取时间特征
    df['year'] = df['published_at'].dt.year
    df['month'] = df['published_at'].dt.month
    df['year_month'] = df['published_at'].dt.to_period('M')
    df['quarter'] = df['published_at'].dt.to_period('Q')

    # 过滤有效数据
    df_valid = df[df['published_at'].notna()].copy()

    print(f"  总评论数: {len(df)}")
    print(f"  有效时间戳: {len(df_valid)}")
    print(f"  时间范围: {df_valid['published_at'].min()} 到 {df_valid['published_at'].max()}")

    return df_valid


def analyze_sentiment_over_time(df: pd.DataFrame, output_dir: Path):
    """
    分析情感随时间的变化

    Args:
        df: 输入数据
        output_dir: 输出目录
    """
    print(f"\n📈 分析情感时间序列...")

    # 按月统计情感分布
    sentiment_by_month = df.groupby(['year_month', 'sentiment']).size().unstack(fill_value=0)
    sentiment_by_month_pct = sentiment_by_month.div(sentiment_by_month.sum(axis=1), axis=0) * 100

    # 绘制情感演变图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # 1. 绝对数量
    sentiment_by_month.plot(
        kind='area',
        stacked=True,
        alpha=0.7,
        ax=ax1,
        color=['#d32f2f', '#757575', '#388e3c']  # red, gray, green
    )
    ax1.set_title('评论情感分布随时间变化（绝对数量）', fontsize=14, fontweight='bold')
    ax1.set_xlabel('时间', fontsize=12)
    ax1.set_ylabel('评论数', fontsize=12)
    ax1.legend(title='情感', labels=['Negative', 'Neutral', 'Positive'], loc='upper left')
    ax1.grid(True, alpha=0.3)

    # 2. 百分比
    sentiment_by_month_pct.plot(
        kind='line',
        ax=ax2,
        marker='o',
        linewidth=2,
        color=['#d32f2f', '#757575', '#388e3c']
    )
    ax2.set_title('评论情感比例随时间变化', fontsize=14, fontweight='bold')
    ax2.set_xlabel('时间', fontsize=12)
    ax2.set_ylabel('百分比 (%)', fontsize=12)
    ax2.legend(title='情感', labels=['Negative', 'Neutral', 'Positive'], loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)

    plt.tight_layout()
    output_file = output_dir / 'sentiment_time_series.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")

    # 保存统计数据
    stats = {
        'sentiment_by_month': sentiment_by_month.to_dict(),
        'sentiment_by_month_percentage': sentiment_by_month_pct.to_dict()
    }

    return stats


def analyze_engagement_over_time(df: pd.DataFrame, output_dir: Path):
    """
    分析互动数据随时间的变化

    Args:
        df: 输入数据
        output_dir: 输出目录
    """
    print(f"\n💬 分析互动时间序列...")

    # 按月统计互动数据
    engagement_by_month = df.groupby('year_month').agg({
        'like_count': ['mean', 'median', 'sum'],
        'text': 'count'  # 评论数
    }).reset_index()

    engagement_by_month.columns = ['year_month', 'mean_likes', 'median_likes', 'total_likes', 'comment_count']

    # 绘制互动演变图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # 1. 平均点赞数
    ax1.plot(engagement_by_month['year_month'].astype(str),
             engagement_by_month['mean_likes'],
             marker='o', linewidth=2, color='#1976d2', label='平均点赞数')
    ax1.plot(engagement_by_month['year_month'].astype(str),
             engagement_by_month['median_likes'],
             marker='s', linewidth=2, color='#ff9800', label='中位数点赞数', linestyle='--')
    ax1.set_title('平均点赞数随时间变化', fontsize=14, fontweight='bold')
    ax1.set_xlabel('时间', fontsize=12)
    ax1.set_ylabel('点赞数', fontsize=12)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)

    # 2. 评论数量
    ax2.bar(engagement_by_month['year_month'].astype(str),
            engagement_by_month['comment_count'],
            color='#4caf50', alpha=0.7)
    ax2.set_title('评论数量随时间变化', fontsize=14, fontweight='bold')
    ax2.set_xlabel('时间', fontsize=12)
    ax2.set_ylabel('评论数', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    output_file = output_dir / 'engagement_time_series.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")

    stats = {
        'engagement_by_month': engagement_by_month.to_dict(orient='records')
    }

    return stats


def analyze_topics_over_time(df: pd.DataFrame, output_dir: Path):
    """
    分析主题分布随时间的变化

    Args:
        df: 输入数据
        output_dir: 输出目录
    """
    print(f"\n🏷️  分析主题时间序列...")

    if 'topic' not in df.columns:
        print("  ⚠️  未找到主题字段，跳过主题时间序列分析")
        return {}

    # 过滤有效主题
    df_topics = df[df['topic'] >= 0].copy()

    if len(df_topics) == 0:
        print("  ⚠️  没有有效的主题数据")
        return {}

    # 按月统计主题分布
    topic_by_month = df_topics.groupby(['year_month', 'topic']).size().unstack(fill_value=0)
    topic_by_month_pct = topic_by_month.div(topic_by_month.sum(axis=1), axis=0) * 100

    # 绘制主题演变图
    fig, ax = plt.subplots(figsize=(14, 8))

    topic_by_month_pct.plot(
        kind='area',
        stacked=True,
        alpha=0.7,
        ax=ax,
        colormap='tab10'
    )

    ax.set_title('主题分布随时间变化', fontsize=14, fontweight='bold')
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('百分比 (%)', fontsize=12)
    ax.legend(title='主题', labels=[f'Topic {i}' for i in topic_by_month_pct.columns],
              loc='center left', bbox_to_anchor=(1, 0.5))
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)

    plt.tight_layout()
    output_file = output_dir / 'topics_time_series.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")

    stats = {
        'topic_by_month_percentage': topic_by_month_pct.to_dict()
    }

    return stats


def analyze_ai_content_evolution(df: pd.DataFrame, output_dir: Path):
    """
    分析 AI 内容随时间的演变（如果有 video_type 字段）

    Args:
        df: 输入数据
        output_dir: 输出目录
    """
    print(f"\n🤖 分析 AI 内容时间演变...")

    if 'video_type' not in df.columns:
        print("  ⚠️  未找到 video_type 字段，跳过 AI 内容演变分析")
        return {}

    # 按月统计 AI vs 非AI
    ai_by_month = df.groupby(['year_month', 'video_type']).size().unstack(fill_value=0)

    if ai_by_month.empty:
        print("  ⚠️  没有 AI 类型数据")
        return {}

    ai_by_month_pct = ai_by_month.div(ai_by_month.sum(axis=1), axis=0) * 100

    # 绘制 AI 内容比例演变
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # 1. 绝对数量
    ai_by_month.plot(kind='bar', stacked=True, ax=ax1, color=['#ff6b6b', '#4ecdc4'])
    ax1.set_title('AI vs 非AI 内容数量随时间变化', fontsize=14, fontweight='bold')
    ax1.set_xlabel('时间', fontsize=12)
    ax1.set_ylabel('评论数', fontsize=12)
    ax1.legend(title='内容类型', labels=['AI Generated', 'Non-AI'], loc='upper left')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3, axis='y')

    # 2. 百分比
    ai_by_month_pct.plot(kind='line', marker='o', linewidth=2, ax=ax2, color=['#ff6b6b', '#4ecdc4'])
    ax2.set_title('AI 内容比例随时间变化', fontsize=14, fontweight='bold')
    ax2.set_xlabel('时间', fontsize=12)
    ax2.set_ylabel('百分比 (%)', fontsize=12)
    ax2.legend(title='内容类型', labels=['AI Generated', 'Non-AI'], loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)

    plt.tight_layout()
    output_file = output_dir / 'ai_content_evolution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")

    stats = {
        'ai_by_month': ai_by_month.to_dict(),
        'ai_by_month_percentage': ai_by_month_pct.to_dict()
    }

    return stats


def analyze_yearly_comparison(df: pd.DataFrame, output_dir: Path):
    """
    年度对比分析

    Args:
        df: 输入数据
        output_dir: 输出目录
    """
    print(f"\n📅 年度对比分析...")

    # 按年统计
    yearly_stats = df.groupby('year').agg({
        'text': 'count',
        'like_count': ['mean', 'median', 'sum'],
        'sentiment': lambda x: (x == 'positive').sum() / len(x) * 100
    }).reset_index()

    yearly_stats.columns = ['year', 'comment_count', 'mean_likes', 'median_likes',
                            'total_likes', 'positive_ratio']

    # 绘制年度对比图
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. 评论数量
    axes[0, 0].bar(yearly_stats['year'], yearly_stats['comment_count'],
                   color='#2196f3', alpha=0.7)
    axes[0, 0].set_title('年度评论数量', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('年份', fontsize=10)
    axes[0, 0].set_ylabel('评论数', fontsize=10)
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    # 2. 平均点赞数
    axes[0, 1].plot(yearly_stats['year'], yearly_stats['mean_likes'],
                    marker='o', linewidth=2, color='#ff9800', markersize=8)
    axes[0, 1].set_title('年度平均点赞数', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('年份', fontsize=10)
    axes[0, 1].set_ylabel('平均点赞', fontsize=10)
    axes[0, 1].grid(True, alpha=0.3)

    # 3. 积极情感比例
    axes[1, 0].plot(yearly_stats['year'], yearly_stats['positive_ratio'],
                    marker='s', linewidth=2, color='#4caf50', markersize=8)
    axes[1, 0].set_title('年度积极情感比例', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('年份', fontsize=10)
    axes[1, 0].set_ylabel('积极比例 (%)', fontsize=10)
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_ylim(0, 100)

    # 4. 总点赞数
    axes[1, 1].bar(yearly_stats['year'], yearly_stats['total_likes'],
                   color='#9c27b0', alpha=0.7)
    axes[1, 1].set_title('年度总点赞数', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('年份', fontsize=10)
    axes[1, 1].set_ylabel('总点赞', fontsize=10)
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = output_dir / 'yearly_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")

    stats = {
        'yearly_stats': yearly_stats.to_dict(orient='records')
    }

    return stats


def generate_time_series_report(all_stats: dict, df: pd.DataFrame, output_dir: Path):
    """
    生成时间序列分析报告

    Args:
        all_stats: 所有统计数据
        df: 原始数据
        output_dir: 输出目录
    """
    print(f"\n📝 生成时间序列分析报告...")

    report = []

    report.append("=" * 80)
    report.append("时间序列分析报告")
    report.append("YouTube Shorts 评论时间演变分析 (2022-2025)")
    report.append("=" * 80)
    report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # 1. 数据概览
    report.append("=" * 80)
    report.append("1. 数据概览")
    report.append("=" * 80)
    report.append(f"\n总评论数: {len(df):,}")
    report.append(f"时间范围: {df['published_at'].min()} 到 {df['published_at'].max()}")
    report.append(f"跨度: {(df['published_at'].max() - df['published_at'].min()).days} 天")

    # 年度分布
    year_counts = df['year'].value_counts().sort_index()
    report.append(f"\n年度分布:")
    for year, count in year_counts.items():
        report.append(f"  {int(year)}: {count:,} 条评论")
    report.append("")

    # 2. 情感演变
    report.append("=" * 80)
    report.append("2. 情感演变趋势")
    report.append("=" * 80)
    report.append("")

    # 计算情感趋势
    sentiment_trend = df.groupby('year')['sentiment'].value_counts(normalize=True).unstack(fill_value=0) * 100
    report.append("年度情感分布:")
    for year in sentiment_trend.index:
        report.append(f"\n  {int(year)} 年:")
        for sentiment in ['positive', 'neutral', 'negative']:
            if sentiment in sentiment_trend.columns:
                report.append(f"    {sentiment}: {sentiment_trend.loc[year, sentiment]:.1f}%")
    report.append("")

    # 3. 互动演变
    report.append("=" * 80)
    report.append("3. 互动数据演变")
    report.append("=" * 80)
    report.append("")

    engagement_yearly = df.groupby('year')['like_count'].agg(['mean', 'median', 'sum'])
    report.append("年度点赞数据:")
    for year in engagement_yearly.index:
        report.append(f"\n  {int(year)} 年:")
        report.append(f"    平均点赞: {engagement_yearly.loc[year, 'mean']:.2f}")
        report.append(f"    中位数: {engagement_yearly.loc[year, 'median']:.0f}")
        report.append(f"    总点赞: {engagement_yearly.loc[year, 'sum']:,.0f}")
    report.append("")

    # 4. 关键发现
    report.append("=" * 80)
    report.append("4. 关键发现")
    report.append("=" * 80)
    report.append("")

    findings = []

    # 情感变化
    if len(sentiment_trend) >= 2:
        years = sorted(sentiment_trend.index)
        first_year = years[0]
        last_year = years[-1]

        if 'positive' in sentiment_trend.columns:
            pos_change = sentiment_trend.loc[last_year, 'positive'] - sentiment_trend.loc[first_year, 'positive']
            if abs(pos_change) > 5:
                direction = "上升" if pos_change > 0 else "下降"
                findings.append(f"• 积极情感比例从 {int(first_year)} 到 {int(last_year)} {direction}了 {abs(pos_change):.1f}%")

    # 互动变化
    if len(engagement_yearly) >= 2:
        years = sorted(engagement_yearly.index)
        first_year = years[0]
        last_year = years[-1]

        engagement_change = ((engagement_yearly.loc[last_year, 'mean'] / engagement_yearly.loc[first_year, 'mean']) - 1) * 100
        if abs(engagement_change) > 10:
            direction = "增长" if engagement_change > 0 else "下降"
            findings.append(f"• 平均点赞数从 {int(first_year)} 到 {int(last_year)} {direction}了 {abs(engagement_change):.1f}%")

    if findings:
        report.extend(findings)
    else:
        report.append("• 未发现显著的时间趋势变化")

    report.append("")
    report.append("=" * 80)
    report.append("报告结束")
    report.append("=" * 80)

    # 保存报告
    report_text = '\n'.join(report)
    report_file = output_dir / f'time_series_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"  ✓ 保存: {report_file}")

    return report_text


def main():
    parser = argparse.ArgumentParser(description='时间序列分析')
    parser.add_argument('--input', required=True, help='输入 CSV 文件')
    parser.add_argument('--output', default='output/figures', help='输出目录')

    args = parser.parse_args()

    print("=" * 80)
    print(" 时间序列分析工具")
    print("=" * 80)

    # 加载数据
    df = load_and_prepare_data(args.input)

    if len(df) == 0:
        print("\n❌ 没有有效的时间戳数据")
        return 1

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 执行各项分析
    all_stats = {}

    all_stats['sentiment'] = analyze_sentiment_over_time(df, output_dir)
    all_stats['engagement'] = analyze_engagement_over_time(df, output_dir)
    all_stats['topics'] = analyze_topics_over_time(df, output_dir)
    all_stats['ai_evolution'] = analyze_ai_content_evolution(df, output_dir)
    all_stats['yearly'] = analyze_yearly_comparison(df, output_dir)

    # 生成报告
    report_text = generate_time_series_report(all_stats, df, output_dir)

    # 保存统计数据
    stats_file = output_dir / f'time_series_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(all_stats, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n✅ 时间序列分析完成！")
    print(f"\n📊 生成的文件:")
    print(f"  - sentiment_time_series.png")
    print(f"  - engagement_time_series.png")
    print(f"  - topics_time_series.png")
    print(f"  - yearly_comparison.png")
    print(f"  - time_series_report_*.txt")
    print(f"  - time_series_stats_*.json")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
