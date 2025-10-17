#!/usr/bin/env python3
"""
AI vs 非AI 对比可视化脚本

生成全面的对比可视化图表

Usage:
    python scripts/visualize_comparison.py \
        --ai data/processed/comments_ai_sentiment_topics.csv \
        --non-ai data/processed/comments_non_ai_sentiment_topics.csv \
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

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style('whitegrid')


def load_data(ai_file: str, non_ai_file: str) -> tuple:
    """
    加载 AI 和非AI 数据

    Args:
        ai_file: AI 内容数据文件
        non_ai_file: 非AI 内容数据文件

    Returns:
        (df_ai, df_non_ai) 元组
    """
    print(f"\n📊 加载数据...")
    print(f"  AI 数据: {ai_file}")
    print(f"  非AI 数据: {non_ai_file}")

    df_ai = pd.read_csv(ai_file)
    df_non_ai = pd.read_csv(non_ai_file)

    print(f"\n  AI 评论: {len(df_ai):,}")
    print(f"  非AI 评论: {len(df_non_ai):,}")

    return df_ai, df_non_ai


def visualize_sentiment_comparison(df_ai: pd.DataFrame, df_non_ai: pd.DataFrame, output_dir: Path):
    """
    情感分布对比可视化

    Args:
        df_ai: AI 数据
        df_non_ai: 非AI 数据
        output_dir: 输出目录
    """
    print(f"\n📈 生成情感对比图...")

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 1. 饼图对比
    sentiment_ai = df_ai['sentiment'].value_counts()
    sentiment_non_ai = df_non_ai['sentiment'].value_counts()

    colors = {'positive': '#4caf50', 'neutral': '#9e9e9e', 'negative': '#f44336'}
    color_list = [colors.get(s, '#cccccc') for s in sentiment_ai.index]

    axes[0].pie(sentiment_ai.values, labels=sentiment_ai.index, autopct='%1.1f%%',
                colors=color_list, startangle=90)
    axes[0].set_title('AI 内容情感分布', fontsize=14, fontweight='bold')

    color_list = [colors.get(s, '#cccccc') for s in sentiment_non_ai.index]
    axes[1].pie(sentiment_non_ai.values, labels=sentiment_non_ai.index, autopct='%1.1f%%',
                colors=color_list, startangle=90)
    axes[1].set_title('非AI 内容情感分布', fontsize=14, fontweight='bold')

    # 2. 对比柱状图
    sentiment_comparison = pd.DataFrame({
        'AI': df_ai['sentiment'].value_counts(normalize=True) * 100,
        '非AI': df_non_ai['sentiment'].value_counts(normalize=True) * 100
    })

    sentiment_comparison.plot(kind='bar', ax=axes[2], color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
    axes[2].set_title('情感分布对比', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('情感类型', fontsize=12)
    axes[2].set_ylabel('百分比 (%)', fontsize=12)
    axes[2].legend(title='内容类型', loc='upper right')
    axes[2].tick_params(axis='x', rotation=0)
    axes[2].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = output_dir / 'sentiment_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")


def visualize_engagement_comparison(df_ai: pd.DataFrame, df_non_ai: pd.DataFrame, output_dir: Path):
    """
    互动数据对比可视化

    Args:
        df_ai: AI 数据
        df_non_ai: 非AI 数据
        output_dir: 输出目录
    """
    print(f"\n💬 生成互动对比图...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. 平均点赞对比
    engagement_data = pd.DataFrame({
        '内容类型': ['AI 内容', '非AI 内容'],
        '平均点赞': [df_ai['like_count'].mean(), df_non_ai['like_count'].mean()],
        '中位数点赞': [df_ai['like_count'].median(), df_non_ai['like_count'].median()]
    })

    x = np.arange(len(engagement_data))
    width = 0.35

    axes[0, 0].bar(x - width/2, engagement_data['平均点赞'], width,
                   label='平均点赞', color='#2196f3', alpha=0.8)
    axes[0, 0].bar(x + width/2, engagement_data['中位数点赞'], width,
                   label='中位数点赞', color='#ff9800', alpha=0.8)
    axes[0, 0].set_title('点赞数对比（平均 vs 中位数）', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('点赞数', fontsize=10)
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(engagement_data['内容类型'])
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    # 2. 点赞数分布箱线图
    like_data = [df_ai['like_count'], df_non_ai['like_count']]
    bp = axes[0, 1].boxplot(like_data, labels=['AI 内容', '非AI 内容'],
                            patch_artist=True, showmeans=True)
    for patch, color in zip(bp['boxes'], ['#ff6b6b', '#4ecdc4']):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    axes[0, 1].set_title('点赞数分布（箱线图）', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylabel('点赞数', fontsize=10)
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    # 3. 点赞数分布直方图（对数尺度）
    axes[1, 0].hist([df_ai['like_count'], df_non_ai['like_count']],
                    bins=50, label=['AI 内容', '非AI 内容'],
                    color=['#ff6b6b', '#4ecdc4'], alpha=0.6, edgecolor='black')
    axes[1, 0].set_title('点赞数分布（直方图）', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('点赞数', fontsize=10)
    axes[1, 0].set_ylabel('频数', fontsize=10)
    axes[1, 0].set_yscale('log')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 4. 评论长度对比
    if 'text_length' in df_ai.columns and 'text_length' in df_non_ai.columns:
        length_data = pd.DataFrame({
            '内容类型': ['AI 内容', '非AI 内容'],
            '平均长度': [df_ai['text_length'].mean(), df_non_ai['text_length'].mean()],
            '中位数长度': [df_ai['text_length'].median(), df_non_ai['text_length'].median()]
        })

        x = np.arange(len(length_data))
        axes[1, 1].bar(x - width/2, length_data['平均长度'], width,
                       label='平均长度', color='#9c27b0', alpha=0.8)
        axes[1, 1].bar(x + width/2, length_data['中位数长度'], width,
                       label='中位数长度', color='#ff5722', alpha=0.8)
        axes[1, 1].set_title('评论长度对比', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('字符数', fontsize=10)
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(length_data['内容类型'])
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = output_dir / 'engagement_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")


def visualize_topic_comparison(df_ai: pd.DataFrame, df_non_ai: pd.DataFrame, output_dir: Path):
    """
    主题分布对比可视化

    Args:
        df_ai: AI 数据
        df_non_ai: 非AI 数据
        output_dir: 输出目录
    """
    print(f"\n🏷️  生成主题对比图...")

    if 'topic' not in df_ai.columns or 'topic' not in df_non_ai.columns:
        print("  ⚠️  未找到主题字段，跳过主题对比")
        return

    # 过滤有效主题
    df_ai_topics = df_ai[df_ai['topic'] >= 0]
    df_non_ai_topics = df_non_ai[df_non_ai['topic'] >= 0]

    if len(df_ai_topics) == 0 or len(df_non_ai_topics) == 0:
        print("  ⚠️  没有有效的主题数据")
        return

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 1. 主题分布对比（柱状图）
    topic_ai = df_ai_topics['topic'].value_counts(normalize=True).sort_index() * 100
    topic_non_ai = df_non_ai_topics['topic'].value_counts(normalize=True).sort_index() * 100

    topic_comparison = pd.DataFrame({
        'AI 内容': topic_ai,
        '非AI 内容': topic_non_ai
    }).fillna(0)

    topic_comparison.plot(kind='bar', ax=axes[0], color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
    axes[0].set_title('主题分布对比', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('主题 ID', fontsize=12)
    axes[0].set_ylabel('百分比 (%)', fontsize=12)
    axes[0].legend(title='内容类型', loc='upper right')
    axes[0].tick_params(axis='x', rotation=0)
    axes[0].grid(True, alpha=0.3, axis='y')

    # 2. 主题-情感交叉分析
    if 'sentiment' in df_ai.columns:
        ai_cross = pd.crosstab(df_ai_topics['topic'], df_ai_topics['sentiment'], normalize='index') * 100
        non_ai_cross = pd.crosstab(df_non_ai_topics['topic'], df_non_ai_topics['sentiment'], normalize='index') * 100

        # 选择最大的主题进行对比
        top_topics = topic_comparison['AI 内容'].nlargest(3).index

        x = np.arange(len(top_topics))
        width = 0.35

        ai_positive = [ai_cross.loc[t, 'positive'] if t in ai_cross.index and 'positive' in ai_cross.columns else 0
                       for t in top_topics]
        non_ai_positive = [non_ai_cross.loc[t, 'positive'] if t in non_ai_cross.index and 'positive' in non_ai_cross.columns else 0
                           for t in top_topics]

        axes[1].bar(x - width/2, ai_positive, width, label='AI 内容', color='#ff6b6b', alpha=0.8)
        axes[1].bar(x + width/2, non_ai_positive, width, label='非AI 内容', color='#4ecdc4', alpha=0.8)
        axes[1].set_title('主要主题的积极情感比例', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('主题 ID', fontsize=12)
        axes[1].set_ylabel('积极情感比例 (%)', fontsize=12)
        axes[1].set_xticks(x)
        axes[1].set_xticklabels([f'Topic {t}' for t in top_topics])
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = output_dir / 'topic_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")


def visualize_comprehensive_dashboard(df_ai: pd.DataFrame, df_non_ai: pd.DataFrame, output_dir: Path):
    """
    生成综合对比仪表板

    Args:
        df_ai: AI 数据
        df_non_ai: 非AI 数据
        output_dir: 输出目录
    """
    print(f"\n📊 生成综合对比仪表板...")

    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 1. 数据量对比
    ax1 = fig.add_subplot(gs[0, 0])
    counts = [len(df_ai), len(df_non_ai)]
    ax1.bar(['AI 内容', '非AI 内容'], counts, color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
    ax1.set_title('数据量对比', fontsize=12, fontweight='bold')
    ax1.set_ylabel('评论数', fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(counts):
        ax1.text(i, v, f'{v:,}', ha='center', va='bottom', fontsize=10)

    # 2. 情感对比（堆叠柱状图）
    ax2 = fig.add_subplot(gs[0, 1])
    sentiment_ai_pct = df_ai['sentiment'].value_counts(normalize=True) * 100
    sentiment_non_ai_pct = df_non_ai['sentiment'].value_counts(normalize=True) * 100

    sentiments = ['positive', 'neutral', 'negative']
    ai_values = [sentiment_ai_pct.get(s, 0) for s in sentiments]
    non_ai_values = [sentiment_non_ai_pct.get(s, 0) for s in sentiments]

    x = np.arange(2)
    colors = ['#4caf50', '#9e9e9e', '#f44336']

    bottom_ai = 0
    bottom_non_ai = 0
    for i, sentiment in enumerate(sentiments):
        ax2.bar(0, ai_values[i], bottom=bottom_ai, color=colors[i], alpha=0.8, label=sentiment if i == 0 else "")
        ax2.bar(1, non_ai_values[i], bottom=bottom_non_ai, color=colors[i], alpha=0.8)
        bottom_ai += ai_values[i]
        bottom_non_ai += non_ai_values[i]

    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(['AI 内容', '非AI 内容'])
    ax2.set_title('情感分布对比', fontsize=12, fontweight='bold')
    ax2.set_ylabel('百分比 (%)', fontsize=10)
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3, axis='y')

    # 3. 平均点赞对比
    ax3 = fig.add_subplot(gs[0, 2])
    avg_likes = [df_ai['like_count'].mean(), df_non_ai['like_count'].mean()]
    ax3.bar(['AI 内容', '非AI 内容'], avg_likes, color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
    ax3.set_title('平均点赞数对比', fontsize=12, fontweight='bold')
    ax3.set_ylabel('平均点赞', fontsize=10)
    ax3.grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(avg_likes):
        ax3.text(i, v, f'{v:.1f}', ha='center', va='bottom', fontsize=10)

    # 4. 点赞数分布（小提琴图）
    ax4 = fig.add_subplot(gs[1, :])
    data_to_plot = [df_ai['like_count'], df_non_ai['like_count']]
    parts = ax4.violinplot(data_to_plot, positions=[0, 1], showmeans=True, showmedians=True)
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(['#ff6b6b', '#4ecdc4'][i])
        pc.set_alpha(0.6)
    ax4.set_xticks([0, 1])
    ax4.set_xticklabels(['AI 内容', '非AI 内容'])
    ax4.set_title('点赞数分布（小提琴图）', fontsize=12, fontweight='bold')
    ax4.set_ylabel('点赞数', fontsize=10)
    ax4.grid(True, alpha=0.3, axis='y')

    # 5. 评论长度分布
    if 'text_length' in df_ai.columns and 'text_length' in df_non_ai.columns:
        ax5 = fig.add_subplot(gs[2, 0])
        ax5.hist([df_ai['text_length'], df_non_ai['text_length']],
                 bins=50, label=['AI 内容', '非AI 内容'],
                 color=['#ff6b6b', '#4ecdc4'], alpha=0.6, edgecolor='black')
        ax5.set_title('评论长度分布', fontsize=12, fontweight='bold')
        ax5.set_xlabel('字符数', fontsize=10)
        ax5.set_ylabel('频数', fontsize=10)
        ax5.legend()
        ax5.grid(True, alpha=0.3)

    # 6. 主题分布对比
    if 'topic' in df_ai.columns and 'topic' in df_non_ai.columns:
        ax6 = fig.add_subplot(gs[2, 1:])
        df_ai_topics = df_ai[df_ai['topic'] >= 0]
        df_non_ai_topics = df_non_ai[df_non_ai['topic'] >= 0]

        if len(df_ai_topics) > 0 and len(df_non_ai_topics) > 0:
            topic_ai = df_ai_topics['topic'].value_counts(normalize=True).sort_index() * 100
            topic_non_ai = df_non_ai_topics['topic'].value_counts(normalize=True).sort_index() * 100

            topic_comparison = pd.DataFrame({
                'AI 内容': topic_ai,
                '非AI 内容': topic_non_ai
            }).fillna(0)

            topic_comparison.plot(kind='bar', ax=ax6, color=['#ff6b6b', '#4ecdc4'], alpha=0.8)
            ax6.set_title('主题分布对比', fontsize=12, fontweight='bold')
            ax6.set_xlabel('主题 ID', fontsize=10)
            ax6.set_ylabel('百分比 (%)', fontsize=10)
            ax6.legend(title='内容类型')
            ax6.tick_params(axis='x', rotation=0)
            ax6.grid(True, alpha=0.3, axis='y')

    plt.suptitle('AI vs 非AI 内容综合对比仪表板', fontsize=16, fontweight='bold', y=0.995)
    output_file = output_dir / 'comprehensive_dashboard.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='AI vs 非AI 对比可视化')
    parser.add_argument('--ai', required=True, help='AI 内容数据文件')
    parser.add_argument('--non-ai', required=True, help='非AI 内容数据文件')
    parser.add_argument('--output', default='output/figures', help='输出目录')

    args = parser.parse_args()

    print("=" * 80)
    print(" AI vs 非AI 对比可视化工具")
    print("=" * 80)

    # 加载数据
    df_ai, df_non_ai = load_data(args.ai, args.non_ai)

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成各类对比图
    visualize_sentiment_comparison(df_ai, df_non_ai, output_dir)
    visualize_engagement_comparison(df_ai, df_non_ai, output_dir)
    visualize_topic_comparison(df_ai, df_non_ai, output_dir)
    visualize_comprehensive_dashboard(df_ai, df_non_ai, output_dir)

    print(f"\n✅ 对比可视化完成！")
    print(f"\n📊 生成的文件:")
    print(f"  - sentiment_comparison.png")
    print(f"  - engagement_comparison.png")
    print(f"  - topic_comparison.png")
    print(f"  - comprehensive_dashboard.png")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
