#!/usr/bin/env python3
"""
主题标签脚本 - 给主题赋予有意义的名称

根据关键词分析，给每个主题ID赋予描述性名称

Usage:
    python scripts/label_topics.py \
        --input data/processed/comments_sentiment_topics.csv \
        --output data/processed/comments_labeled_topics.csv
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
from collections import Counter
import json


# 主题标签映射（根据关键词分析得出）
TOPIC_LABELS = {
    0: {
        'name': 'Destiny Game Discussion',
        'name_zh': 'Destiny游戏讨论',
        'description': 'Comments about Destiny game, accounts, upgrades, and gameplay',
        'keywords': ['account', 'foltyn', 'destiny', 'upgrade', 'rising']
    },
    1: {
        'name': 'Gaming & Pokemon',
        'name_zh': '游戏与宝可梦',
        'description': 'General gaming discussion, Pokemon, zombies mode',
        'keywords': ['pokemon', 'game', 'zombies', 'better', 'play']
    },
    2: {
        'name': 'Cazzu Music & Culture',
        'name_zh': 'Cazzu音乐与文化',
        'description': 'Comments about Cazzu (artist), music, Spanish content',
        'keywords': ['cazzu', 'music', 'hermosa', 'mujer', 'song']
    },
    3: {
        'name': 'Gaming Technical',
        'name_zh': '游戏技术讨论',
        'description': 'Technical gaming discussion, timestamps, specific players',
        'keywords': ['josh', 'jandel', 'omega', 'owner', '11:34']
    },
    4: {
        'name': 'General Engagement',
        'name_zh': '通用互动讨论',
        'description': 'Mixed general discussion with high engagement',
        'keywords': ['this', 'like', 'game', 'looks', 'people', 'good']
    }
}


def analyze_topic_keywords(df: pd.DataFrame, topic_id: int, top_n: int = 20) -> list:
    """
    分析主题的关键词

    Args:
        df: 数据框
        topic_id: 主题ID
        top_n: 返回前N个关键词

    Returns:
        关键词列表
    """
    topic_texts = df[df['topic'] == topic_id]['text'].tolist()

    # 词频统计
    all_words = []
    for text in topic_texts:
        words = str(text).lower().split()
        all_words.extend([w for w in words if len(w) > 3])

    word_freq = Counter(all_words).most_common(top_n)
    return [word for word, count in word_freq]


def label_topics(input_file: str, output_file: str):
    """
    给主题添加标签

    Args:
        input_file: 输入文件
        output_file: 输出文件
    """
    print(f"\n📊 读取数据: {input_file}")
    df = pd.read_csv(input_file)

    print(f"  总评论数: {len(df)}")
    print(f"  有主题评论: {len(df[df['topic'] >= 0])}")

    # 添加主题标签列
    df['topic_name'] = df['topic'].map(lambda x: TOPIC_LABELS.get(x, {}).get('name', 'Unknown') if x >= 0 else 'No Topic')
    df['topic_name_zh'] = df['topic'].map(lambda x: TOPIC_LABELS.get(x, {}).get('name_zh', '未知') if x >= 0 else '无主题')
    df['topic_description'] = df['topic'].map(lambda x: TOPIC_LABELS.get(x, {}).get('description', '') if x >= 0 else '')

    # 保存
    print(f"\n💾 保存到: {output_file}")
    df.to_csv(output_file, index=False)

    # 打印统计
    print(f"\n📊 主题标签统计:")
    topic_counts = df[df['topic'] >= 0].groupby(['topic', 'topic_name_zh']).size().reset_index(name='count')
    topic_counts['percentage'] = (topic_counts['count'] / topic_counts['count'].sum() * 100).round(1)

    for _, row in topic_counts.iterrows():
        print(f"  Topic {int(row['topic'])}: {row['topic_name_zh']}")
        print(f"    评论数: {row['count']} ({row['percentage']}%)")
        print(f"    关键词: {', '.join(TOPIC_LABELS[int(row['topic'])]['keywords'][:5])}")
        print()

    return df


def generate_labeled_report(df: pd.DataFrame, output_dir: Path):
    """
    生成带标签的主题报告

    Args:
        df: 数据框
        output_dir: 输出目录
    """
    print(f"\n📝 生成带标签的主题报告...")

    df_topics = df[df['topic'] >= 0].copy()

    report = []

    report.append("=" * 80)
    report.append("主题建模分析报告（带标签）")
    report.append("YouTube Shorts Comments - Labeled Topic Analysis")
    report.append("=" * 80)
    report.append(f"\n生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"分析评论数: {len(df_topics):,}")
    report.append("")

    # 主题分布
    report.append("=" * 80)
    report.append("主题分布与解释")
    report.append("=" * 80)
    report.append("")

    for topic_id in sorted(df_topics['topic'].unique()):
        topic_df = df_topics[df_topics['topic'] == topic_id]
        topic_info = TOPIC_LABELS[topic_id]

        count = len(topic_df)
        pct = count / len(df_topics) * 100

        report.append(f"主题 {topic_id}: {topic_info['name_zh']} ({topic_info['name']})")
        report.append(f"{'='*80}")
        report.append(f"评论数: {count:,} ({pct:.1f}%)")
        report.append(f"描述: {topic_info['description']}")
        report.append(f"关键词: {', '.join(topic_info['keywords'])}")
        report.append("")

        # 情感分布
        if 'sentiment' in topic_df.columns:
            sentiment_counts = topic_df['sentiment'].value_counts()
            report.append("情感分布:")
            for sent, sent_count in sentiment_counts.items():
                sent_pct = sent_count / count * 100
                report.append(f"  {sent}: {sent_count} ({sent_pct:.1f}%)")

        # 互动数据
        if 'like_count' in topic_df.columns:
            report.append(f"\n互动数据:")
            report.append(f"  平均点赞: {topic_df['like_count'].mean():.2f}")
            report.append(f"  中位数: {topic_df['like_count'].median():.0f}")
            report.append(f"  最高点赞: {topic_df['like_count'].max()}")

        # 示例评论（最高点赞）
        if 'text' in topic_df.columns and 'like_count' in topic_df.columns:
            top_comment = topic_df.nlargest(1, 'like_count').iloc[0]
            report.append(f"\n最受欢迎评论（{int(top_comment['like_count'])} 赞）:")
            comment_text = str(top_comment['text'])[:150]
            if len(str(top_comment['text'])) > 150:
                comment_text += "..."
            report.append(f"  \"{comment_text}\"")

        report.append("")
        report.append("")

    # 主题对比
    report.append("=" * 80)
    report.append("主题对比分析")
    report.append("=" * 80)
    report.append("")

    # 最受欢迎主题
    if 'like_count' in df_topics.columns:
        avg_likes = df_topics.groupby(['topic', 'topic_name_zh'])['like_count'].mean().reset_index()
        avg_likes = avg_likes.sort_values('like_count', ascending=False)

        report.append("最受欢迎主题（按平均点赞）:")
        for _, row in avg_likes.iterrows():
            report.append(f"  {row['topic_name_zh']}: {row['like_count']:.2f} 平均点赞")
        report.append("")

    # 最积极主题
    if 'sentiment' in df_topics.columns:
        positive_counts = df_topics[df_topics['sentiment'] == 'positive'].groupby(['topic', 'topic_name_zh']).size()
        total_counts = df_topics.groupby(['topic', 'topic_name_zh']).size()
        positive_ratio = (positive_counts / total_counts * 100).reset_index(name='positive_pct')
        positive_ratio = positive_ratio.sort_values('positive_pct', ascending=False)

        report.append("最积极主题（按积极情感比例）:")
        for _, row in positive_ratio.iterrows():
            report.append(f"  {row['topic_name_zh']}: {row['positive_pct']:.1f}% 积极")
        report.append("")

    report.append("=" * 80)
    report.append("报告结束")
    report.append("=" * 80)

    # 保存报告
    report_text = '\n'.join(report)
    report_file = output_dir / 'topic_analysis_labeled_report.txt'

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"  ✓ 保存: {report_file}")

    return report_text


def main():
    parser = argparse.ArgumentParser(description='主题标签工具')
    parser.add_argument('--input', required=True, help='输入 CSV 文件')
    parser.add_argument('--output', required=True, help='输出 CSV 文件')

    args = parser.parse_args()

    print("=" * 80)
    print(" 主题标签工具")
    print("=" * 80)

    # 添加标签
    df = label_topics(args.input, args.output)

    # 生成报告
    output_dir = Path(args.output).parent.parent / 'output' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_labeled_report(df, output_dir)

    # 保存主题标签配置
    config_file = output_dir / 'topic_labels_config.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(TOPIC_LABELS, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 主题标签完成！")
    print(f"\n📊 输出文件:")
    print(f"  - 带标签数据: {args.output}")
    print(f"  - 带标签报告: {output_dir / 'topic_analysis_labeled_report.txt'}")
    print(f"  - 标签配置: {config_file}")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
