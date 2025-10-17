#!/usr/bin/env python3
"""
情感可视化脚本 - 生成情感分析的可视化图表

Usage:
    python scripts/visualize_sentiment.py --input data/processed/comments_sentiment.csv
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Set matplotlib to use non-GUI backend
import matplotlib
matplotlib.use('Agg')

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def main():
    parser = argparse.ArgumentParser(description='可视化情感分析结果')
    parser.add_argument('--input', required=True, help='输入CSV文件路径')
    parser.add_argument('--output-dir', default='output/figures', help='输出目录')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_path}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print(" 情感分析可视化")
    print("="*70)
    print(f"\n📂 输入文件: {input_path}")
    print(f"📂 输出目录: {output_dir}")

    # 读取数据
    print(f"\n📊 加载数据...")
    df = pd.read_csv(input_path)
    print(f"  - 评论数量: {len(df)}")

    # 确保有sentiment列
    if 'sentiment' not in df.columns:
        print("❌ 输入文件缺少 'sentiment' 列")
        sys.exit(1)

    # 1. 情感分布饼图
    print(f"\n📊 生成情感分布饼图...")
    plt.figure(figsize=(10, 6))
    sentiment_counts = df['sentiment'].value_counts()

    colors = {'positive': '#4CAF50', 'negative': '#F44336', 'neutral': '#9E9E9E'}
    plot_colors = [colors.get(s, '#9E9E9E') for s in sentiment_counts.index]

    plt.pie(sentiment_counts.values, labels=sentiment_counts.index,
            autopct='%1.1f%%', colors=plot_colors, startangle=90)
    plt.title('Sentiment Distribution', fontsize=14, fontweight='bold')
    plt.axis('equal')

    pie_path = output_dir / 'sentiment_distribution_pie.png'
    plt.savefig(pie_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 保存: {pie_path}")

    # 2. 情感分布柱状图
    print(f"\n📊 生成情感分布柱状图...")
    plt.figure(figsize=(10, 6))
    sentiment_counts.plot(kind='bar', color=[colors.get(s, '#9E9E9E') for s in sentiment_counts.index])
    plt.title('Sentiment Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Sentiment', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', alpha=0.3)

    # 添加数值标签
    for i, v in enumerate(sentiment_counts.values):
        plt.text(i, v + 10, str(v), ha='center', va='bottom', fontweight='bold')

    bar_path = output_dir / 'sentiment_distribution_bar.png'
    plt.savefig(bar_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 保存: {bar_path}")

    # 3. 情感置信度分布
    if 'sentiment_confidence' in df.columns:
        print(f"\n📊 生成情感置信度分布...")
        plt.figure(figsize=(12, 6))

        for sentiment in ['positive', 'negative', 'neutral']:
            data = df[df['sentiment'] == sentiment]['sentiment_confidence']
            if len(data) > 0:
                plt.hist(data, bins=20, alpha=0.5, label=sentiment.capitalize(),
                         color=colors.get(sentiment, '#9E9E9E'))

        plt.title('Sentiment Confidence Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('Confidence Score', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)

        conf_path = output_dir / 'sentiment_confidence_distribution.png'
        plt.savefig(conf_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 保存: {conf_path}")

    # 4. 时间序列分析（如果有时间列）
    if 'published_datetime' in df.columns:
        print(f"\n📊 生成情感时间序列...")
        df['published_datetime'] = pd.to_datetime(df['published_datetime'])
        df['published_date'] = df['published_datetime'].dt.date

        # 按日期和情感分组
        daily_sentiment = df.groupby(['published_date', 'sentiment']).size().unstack(fill_value=0)

        plt.figure(figsize=(14, 6))
        for sentiment in daily_sentiment.columns:
            plt.plot(daily_sentiment.index, daily_sentiment[sentiment],
                     marker='o', label=sentiment.capitalize(),
                     color=colors.get(sentiment, '#9E9E9E'))

        plt.title('Sentiment Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Comment Count', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)

        time_path = output_dir / 'sentiment_over_time.png'
        plt.savefig(time_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 保存: {time_path}")

    # 5. 点赞数与情感关系
    if 'like_count' in df.columns:
        print(f"\n📊 生成点赞数与情感关系图...")
        plt.figure(figsize=(10, 6))

        sentiments = ['positive', 'negative', 'neutral']
        like_data = [df[df['sentiment'] == s]['like_count'].values for s in sentiments if s in df['sentiment'].values]
        like_labels = [s.capitalize() for s in sentiments if s in df['sentiment'].values]

        bp = plt.boxplot(like_data, labels=like_labels, patch_artist=True)
        for patch, sentiment in zip(bp['boxes'], like_labels):
            patch.set_facecolor(colors.get(sentiment.lower(), '#9E9E9E'))

        plt.title('Like Count by Sentiment', fontsize=14, fontweight='bold')
        plt.xlabel('Sentiment', fontsize=12)
        plt.ylabel('Like Count', fontsize=12)
        plt.grid(axis='y', alpha=0.3)

        likes_path = output_dir / 'sentiment_vs_likes.png'
        plt.savefig(likes_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✅ 保存: {likes_path}")

    # 生成统计报告
    print(f"\n📝 生成统计报告...")
    report = []
    report.append("="*70)
    report.append("情感分析统计报告")
    report.append("="*70)
    report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"数据文件: {input_path}")
    report.append(f"评论总数: {len(df)}")

    report.append("\n情感分布:")
    for sentiment, count in sentiment_counts.items():
        percentage = count / len(df) * 100
        report.append(f"  {sentiment}: {count} ({percentage:.1f}%)")

    if 'sentiment_confidence' in df.columns:
        report.append(f"\n置信度统计:")
        report.append(f"  平均: {df['sentiment_confidence'].mean():.3f}")
        report.append(f"  中位数: {df['sentiment_confidence'].median():.3f}")
        report.append(f"  最小: {df['sentiment_confidence'].min():.3f}")
        report.append(f"  最大: {df['sentiment_confidence'].max():.3f}")

    if 'like_count' in df.columns:
        report.append(f"\n点赞统计 (按情感):")
        for sentiment in ['positive', 'negative', 'neutral']:
            if sentiment in df['sentiment'].values:
                likes = df[df['sentiment'] == sentiment]['like_count']
                report.append(f"  {sentiment}:")
                report.append(f"    平均点赞: {likes.mean():.2f}")
                report.append(f"    中位数: {likes.median():.0f}")
                report.append(f"    最高: {likes.max()}")

    report.append("\n" + "="*70)

    report_path = output_dir / 'sentiment_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    print(f"  ✅ 保存: {report_path}")

    print("\n" + "="*70)
    print("✅ 可视化完成")
    print("="*70)

    print(f"\n📂 生成的文件:")
    for file in output_dir.glob('*'):
        print(f"  - {file.name}")

    print(f"\n💡 下一步建议:")
    print(f"  1. 查看生成的图表: {output_dir}")
    print(f"  2. 运行主题建模: python scripts/run_topic_model.py --input {input_path}")
    print()

if __name__ == '__main__':
    main()
