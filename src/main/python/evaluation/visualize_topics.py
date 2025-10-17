#!/usr/bin/env python3
"""
主题建模可视化脚本

生成主题建模的详细可视化图表

Usage:
    python scripts/visualize_topics.py \
        --input data/processed/comments_sentiment_topics.csv \
        --output output/figures
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# 设置中文字体（如果可用）
try:
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass


def load_data(input_file: str) -> pd.DataFrame:
    """加载数据"""
    print(f"\n📊 加载数据: {input_file}")
    df = pd.read_csv(input_file)
    print(f"  总评论数: {len(df)}")

    if 'topic' in df.columns:
        valid_topics = df[df['topic'] >= 0]
        print(f"  有效主题: {len(valid_topics)}")

    return df


def visualize_topic_distribution(df: pd.DataFrame, output_dir: Path):
    """主题分布可视化"""
    print(f"\n📊 生成主题分布图...")

    if 'topic' not in df.columns:
        print("  ⚠️  未找到主题字段")
        return

    # 过滤有效主题
    df_topics = df[df['topic'] >= 0].copy()

    if len(df_topics) == 0:
        print("  ⚠️  没有有效的主题数据")
        return

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. 主题分布饼图
    topic_counts = df_topics['topic'].value_counts().sort_index()
    colors = plt.cm.Set3(range(len(topic_counts)))

    axes[0, 0].pie(topic_counts.values, labels=[f'Topic {i}' for i in topic_counts.index],
                   autopct='%1.1f%%', colors=colors, startangle=90)
    axes[0, 0].set_title('Topic Distribution', fontsize=14, fontweight='bold')

    # 2. 主题分布柱状图
    axes[0, 1].bar(topic_counts.index, topic_counts.values, color=colors, alpha=0.8)
    axes[0, 1].set_xlabel('Topic ID', fontsize=12)
    axes[0, 1].set_ylabel('Number of Comments', fontsize=12)
    axes[0, 1].set_title('Topic Distribution (Bar Chart)', fontsize=14, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    # 3. 主题-情感关系
    if 'sentiment' in df_topics.columns:
        sentiment_by_topic = pd.crosstab(df_topics['topic'], df_topics['sentiment'], normalize='index') * 100

        sentiment_by_topic.plot(kind='bar', stacked=True, ax=axes[1, 0],
                                color=['#f44336', '#9e9e9e', '#4caf50'], alpha=0.8)
        axes[1, 0].set_xlabel('Topic ID', fontsize=12)
        axes[1, 0].set_ylabel('Percentage (%)', fontsize=12)
        axes[1, 0].set_title('Sentiment Distribution by Topic', fontsize=14, fontweight='bold')
        axes[1, 0].legend(title='Sentiment', labels=['Negative', 'Neutral', 'Positive'])
        axes[1, 0].set_xticklabels(axes[1, 0].get_xticklabels(), rotation=0)
        axes[1, 0].grid(True, alpha=0.3, axis='y')

    # 4. 主题平均点赞数
    if 'like_count' in df_topics.columns:
        avg_likes_by_topic = df_topics.groupby('topic')['like_count'].mean()

        axes[1, 1].bar(avg_likes_by_topic.index, avg_likes_by_topic.values,
                       color=colors, alpha=0.8)
        axes[1, 1].set_xlabel('Topic ID', fontsize=12)
        axes[1, 1].set_ylabel('Average Likes', fontsize=12)
        axes[1, 1].set_title('Average Likes by Topic', fontsize=14, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = output_dir / 'topic_analysis_comprehensive.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")


def visualize_topic_wordclouds(df: pd.DataFrame, output_dir: Path):
    """主题词云（如果有文本数据）"""
    print(f"\n☁️  生成主题关键词分析...")

    if 'topic' not in df.columns or 'text' not in df.columns:
        print("  ⚠️  缺少必要字段")
        return

    # 过滤有效主题
    df_topics = df[df['topic'] >= 0].copy()

    if len(df_topics) == 0:
        print("  ⚠️  没有有效的主题数据")
        return

    # 分析每个主题的常见词（简化版）
    topics = sorted(df_topics['topic'].unique())

    fig, axes = plt.subplots(len(topics), 1, figsize=(14, 4 * len(topics)))
    if len(topics) == 1:
        axes = [axes]

    for idx, topic_id in enumerate(topics):
        topic_texts = df_topics[df_topics['topic'] == topic_id]['text'].tolist()

        # 简单的词频统计（分割并计数）
        all_words = []
        for text in topic_texts:
            words = str(text).lower().split()
            all_words.extend([w for w in words if len(w) > 3])  # 过滤短词

        word_freq = Counter(all_words).most_common(15)

        if word_freq:
            words, counts = zip(*word_freq)
            axes[idx].barh(range(len(words)), counts, color=plt.cm.Set3(idx), alpha=0.8)
            axes[idx].set_yticks(range(len(words)))
            axes[idx].set_yticklabels(words)
            axes[idx].set_xlabel('Frequency', fontsize=11)
            axes[idx].set_title(f'Topic {topic_id} - Top 15 Words', fontsize=12, fontweight='bold')
            axes[idx].invert_yaxis()
            axes[idx].grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    output_file = output_dir / 'topic_keywords.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")


def visualize_topic_engagement(df: pd.DataFrame, output_dir: Path):
    """主题互动分析"""
    print(f"\n💬 生成主题互动分析图...")

    if 'topic' not in df.columns or 'like_count' not in df.columns:
        print("  ⚠️  缺少必要字段")
        return

    # 过滤有效主题
    df_topics = df[df['topic'] >= 0].copy()

    if len(df_topics) == 0:
        print("  ⚠️  没有有效的主题数据")
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 1. 主题点赞箱线图
    topics = sorted(df_topics['topic'].unique())
    like_data = [df_topics[df_topics['topic'] == t]['like_count'].values for t in topics]

    bp = axes[0].boxplot(like_data, labels=[f'Topic {t}' for t in topics],
                         patch_artist=True, showmeans=True)

    colors = plt.cm.Set3(range(len(topics)))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    axes[0].set_xlabel('Topic', fontsize=12)
    axes[0].set_ylabel('Likes', fontsize=12)
    axes[0].set_title('Likes Distribution by Topic (Box Plot)', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')

    # 2. 主题评论长度对比
    if 'text_length' in df_topics.columns:
        avg_length_by_topic = df_topics.groupby('topic')['text_length'].mean()

        axes[1].bar(avg_length_by_topic.index, avg_length_by_topic.values,
                    color=colors, alpha=0.8)
        axes[1].set_xlabel('Topic ID', fontsize=12)
        axes[1].set_ylabel('Average Comment Length (chars)', fontsize=12)
        axes[1].set_title('Average Comment Length by Topic', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = output_dir / 'topic_engagement.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")


def generate_topic_report(df: pd.DataFrame, output_dir: Path):
    """生成主题分析报告"""
    print(f"\n📝 生成主题分析报告...")

    if 'topic' not in df.columns:
        print("  ⚠️  未找到主题字段")
        return

    df_topics = df[df['topic'] >= 0].copy()

    if len(df_topics) == 0:
        print("  ⚠️  没有有效的主题数据")
        return

    report = []

    report.append("=" * 70)
    report.append("主题建模分析报告")
    report.append("YouTube Shorts Comments Topic Analysis")
    report.append("=" * 70)
    report.append(f"\n生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"分析评论数: {len(df_topics):,}")
    report.append("")

    # 1. 主题分布
    report.append("=" * 70)
    report.append("1. 主题分布 (Topic Distribution)")
    report.append("=" * 70)
    report.append("")

    topic_counts = df_topics['topic'].value_counts().sort_index()

    for topic_id, count in topic_counts.items():
        pct = count / len(df_topics) * 100
        report.append(f"Topic {topic_id}:")
        report.append(f"  评论数: {count:,} ({pct:.1f}%)")

        # 情感分布
        if 'sentiment' in df_topics.columns:
            topic_sentiments = df_topics[df_topics['topic'] == topic_id]['sentiment'].value_counts()
            for sent, sent_count in topic_sentiments.items():
                sent_pct = sent_count / count * 100
                report.append(f"    {sent}: {sent_count} ({sent_pct:.1f}%)")

        # 互动数据
        if 'like_count' in df_topics.columns:
            topic_likes = df_topics[df_topics['topic'] == topic_id]['like_count']
            report.append(f"  平均点赞: {topic_likes.mean():.2f}")
            report.append(f"  中位数: {topic_likes.median():.0f}")

        report.append("")

    # 2. 主题关键特征
    report.append("=" * 70)
    report.append("2. 主题关键特征 (Topic Characteristics)")
    report.append("=" * 70)
    report.append("")

    # 最受欢迎主题（平均点赞最高）
    if 'like_count' in df_topics.columns:
        avg_likes = df_topics.groupby('topic')['like_count'].mean().sort_values(ascending=False)
        report.append("最受欢迎主题（按平均点赞）:")
        for topic_id, likes in avg_likes.head(3).items():
            report.append(f"  Topic {topic_id}: {likes:.2f} 平均点赞")
        report.append("")

    # 最积极主题
    if 'sentiment' in df_topics.columns:
        positive_ratio = df_topics[df_topics['sentiment'] == 'positive'].groupby('topic').size() / df_topics.groupby('topic').size()
        positive_ratio = positive_ratio.sort_values(ascending=False)
        report.append("最积极主题（按积极情感比例）:")
        for topic_id, ratio in positive_ratio.head(3).items():
            report.append(f"  Topic {topic_id}: {ratio*100:.1f}% 积极")
        report.append("")

    # 最长评论主题
    if 'text_length' in df_topics.columns:
        avg_length = df_topics.groupby('topic')['text_length'].mean().sort_values(ascending=False)
        report.append("评论最长主题（按平均长度）:")
        for topic_id, length in avg_length.head(3).items():
            report.append(f"  Topic {topic_id}: {length:.0f} 字符")
        report.append("")

    report.append("=" * 70)
    report.append("报告结束")
    report.append("=" * 70)

    # 保存报告
    report_text = '\n'.join(report)
    report_file = output_dir / 'topic_analysis_report.txt'

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"  ✓ 保存: {report_file}")

    return report_text


def main():
    parser = argparse.ArgumentParser(description='主题建模可视化')
    parser.add_argument('--input', required=True, help='输入 CSV 文件')
    parser.add_argument('--output', default='output/figures', help='输出目录')

    args = parser.parse_args()

    print("=" * 70)
    print(" 主题建模可视化工具")
    print("=" * 70)

    # 加载数据
    df = load_data(args.input)

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成各类可视化
    visualize_topic_distribution(df, output_dir)
    visualize_topic_wordclouds(df, output_dir)
    visualize_topic_engagement(df, output_dir)
    generate_topic_report(df, output_dir)

    print(f"\n✅ 主题可视化完成！")
    print(f"\n📊 生成的文件:")
    print(f"  - topic_analysis_comprehensive.png (4子图)")
    print(f"  - topic_keywords.png (关键词分析)")
    print(f"  - topic_engagement.png (互动分析)")
    print(f"  - topic_analysis_report.txt (详细报告)")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
