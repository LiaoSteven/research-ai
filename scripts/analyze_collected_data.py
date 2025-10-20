#!/usr/bin/env python3
"""
分析采集的数据并生成可视化报告

生成内容：
1. AI占比演变趋势图
2. AI vs 非AI 互动指标对比
3. AI检测置信度分布
4. 评论长度对比
5. 综合研究报告
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from datetime import datetime
from pathlib import Path
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def load_data(data_file):
    """加载数据"""
    print(f"加载数据: {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        comments = json.load(f)
    return pd.DataFrame(comments)

def analyze_ai_ratio_evolution(df, output_dir):
    """分析AI占比演变"""
    print("\n1️⃣ 分析AI占比演变...")

    quarter_stats = df.groupby('quarter').agg({
        'video_type': lambda x: (x == 'ai_generated').sum(),
        'comment_id': 'count'
    }).rename(columns={'video_type': 'ai_count', 'comment_id': 'total'})

    quarter_stats['ai_ratio'] = (quarter_stats['ai_count'] / quarter_stats['total'] * 100).round(1)
    quarter_stats = quarter_stats.sort_index()

    # 绘图
    fig, ax = plt.subplots(figsize=(12, 6))

    quarters = quarter_stats.index.tolist()
    ai_ratios = quarter_stats['ai_ratio'].values

    ax.plot(quarters, ai_ratios, marker='o', linewidth=2, markersize=8,
            color='#FF6B6B', label='AI Content Ratio')
    ax.fill_between(range(len(quarters)), ai_ratios, alpha=0.3, color='#FF6B6B')

    ax.set_xlabel('Quarter', fontsize=12, fontweight='bold')
    ax.set_ylabel('AI Content Ratio (%)', fontsize=12, fontweight='bold')
    ax.set_title('AI Content Ratio Evolution (2022-2025)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()

    output_file = output_dir / 'ai_ratio_evolution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ 保存图表: {output_file}")
    plt.close()

    return quarter_stats

def analyze_interaction_comparison(df, output_dir):
    """分析AI vs 非AI互动对比"""
    print("\n2️⃣ 分析互动指标对比...")

    ai_comments = df[df['video_type'] == 'ai_generated']
    non_ai_comments = df[df['video_type'] == 'non_ai']

    # 创建对比图
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 点赞数对比
    data_likes = [
        ai_comments['like_count'].values,
        non_ai_comments['like_count'].values
    ]

    axes[0].boxplot(data_likes, labels=['AI Content', 'Non-AI Content'])
    axes[0].set_ylabel('Like Count', fontweight='bold')
    axes[0].set_title('Like Count Distribution', fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')

    # 评论长度对比
    ai_comments_copy = ai_comments.copy()
    non_ai_comments_copy = non_ai_comments.copy()
    ai_comments_copy['text_length'] = ai_comments_copy['text'].str.len()
    non_ai_comments_copy['text_length'] = non_ai_comments_copy['text'].str.len()

    data_length = [
        ai_comments_copy['text_length'].values,
        non_ai_comments_copy['text_length'].values
    ]

    axes[1].boxplot(data_length, labels=['AI Content', 'Non-AI Content'])
    axes[1].set_ylabel('Comment Length (characters)', fontweight='bold')
    axes[1].set_title('Comment Length Distribution', fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = output_dir / 'interaction_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ 保存图表: {output_file}")
    plt.close()

    stats = {
        'ai': {
            'avg_likes': ai_comments['like_count'].mean(),
            'median_likes': ai_comments['like_count'].median(),
            'avg_length': ai_comments_copy['text_length'].mean(),
            'median_length': ai_comments_copy['text_length'].median()
        },
        'non_ai': {
            'avg_likes': non_ai_comments['like_count'].mean(),
            'median_likes': non_ai_comments['like_count'].median(),
            'avg_length': non_ai_comments_copy['text_length'].mean(),
            'median_length': non_ai_comments_copy['text_length'].median()
        }
    }

    return stats

def analyze_ai_detection(df, output_dir):
    """分析AI检测置信度"""
    print("\n3️⃣ 分析AI检测置信度...")

    ai_comments = df[df['video_type'] == 'ai_generated']

    if len(ai_comments) == 0:
        print("   ⚠ 没有AI评论")
        return None

    # 提取置信度
    confidences = []
    all_keywords = []

    for _, row in ai_comments.iterrows():
        ai_det = row['ai_detection']
        confidences.append(ai_det['confidence'])
        all_keywords.extend(ai_det.get('matched_keywords', []))

    # 绘制置信度分布
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].hist(confidences, bins=20, color='#4ECDC4', edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('Confidence Score', fontweight='bold')
    axes[0].set_ylabel('Frequency', fontweight='bold')
    axes[0].set_title('AI Detection Confidence Distribution', fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')

    # 关键词频率
    keyword_counts = Counter(all_keywords)
    top_keywords = dict(keyword_counts.most_common(10))

    axes[1].barh(list(top_keywords.keys()), list(top_keywords.values()), color='#95E1D3')
    axes[1].set_xlabel('Frequency', fontweight='bold')
    axes[1].set_title('Top AI Keywords Detected', fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    output_file = output_dir / 'ai_detection_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   ✓ 保存图表: {output_file}")
    plt.close()

    return {
        'avg_confidence': sum(confidences) / len(confidences),
        'min_confidence': min(confidences),
        'max_confidence': max(confidences),
        'top_keywords': list(top_keywords.items())[:5]
    }

def generate_report(df, quarter_stats, interaction_stats, detection_stats, output_dir):
    """生成综合报告"""
    print("\n4️⃣ 生成综合报告...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f'analysis_report_{timestamp}.txt'

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(" YouTube Shorts AI Content Analysis Report\n")
        f.write("="*80 + "\n\n")

        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"分析评论数: {len(df):,}\n\n")

        # 基础统计
        f.write("="*80 + "\n")
        f.write("1. 数据概览\n")
        f.write("="*80 + "\n\n")

        f.write(f"时间范围: {df['published_at'].min()} ~ {df['published_at'].max()}\n")
        f.write(f"总评论数: {len(df):,}\n")
        f.write(f"视频数: {df['video_id'].nunique()}\n")
        f.write(f"作者数: {df['author'].nunique()}\n\n")

        # AI占比
        ai_count = len(df[df['video_type'] == 'ai_generated'])
        non_ai_count = len(df[df['video_type'] == 'non_ai'])
        ai_ratio = ai_count / len(df) * 100

        f.write(f"AI内容: {ai_count:,} ({ai_ratio:.1f}%)\n")
        f.write(f"非AI内容: {non_ai_count:,} ({100-ai_ratio:.1f}%)\n\n")

        # AI占比演变
        f.write("="*80 + "\n")
        f.write("2. AI占比时间演变\n")
        f.write("="*80 + "\n\n")

        f.write(f"{'季度':<12} {'AI评论':<10} {'总评论':<10} {'AI占比':<10}\n")
        f.write("-"*42 + "\n")
        for quarter, row in quarter_stats.iterrows():
            f.write(f"{quarter:<12} {int(row['ai_count']):<10} {int(row['total']):<10} {row['ai_ratio']:<10.1f}%\n")

        # 互动对比
        f.write("\n" + "="*80 + "\n")
        f.write("3. AI vs 非AI 互动对比\n")
        f.write("="*80 + "\n\n")

        f.write("AI内容:\n")
        f.write(f"  平均点赞: {interaction_stats['ai']['avg_likes']:.2f}\n")
        f.write(f"  中位数点赞: {interaction_stats['ai']['median_likes']:.0f}\n")
        f.write(f"  平均评论长度: {interaction_stats['ai']['avg_length']:.1f} 字符\n\n")

        f.write("非AI内容:\n")
        f.write(f"  平均点赞: {interaction_stats['non_ai']['avg_likes']:.2f}\n")
        f.write(f"  中位数点赞: {interaction_stats['non_ai']['median_likes']:.0f}\n")
        f.write(f"  平均评论长度: {interaction_stats['non_ai']['avg_length']:.1f} 字符\n\n")

        # AI检测
        if detection_stats:
            f.write("="*80 + "\n")
            f.write("4. AI检测统计\n")
            f.write("="*80 + "\n\n")

            f.write(f"平均置信度: {detection_stats['avg_confidence']:.3f}\n")
            f.write(f"置信度范围: {detection_stats['min_confidence']:.3f} ~ {detection_stats['max_confidence']:.3f}\n\n")

            f.write("最常见AI关键词:\n")
            for kw, count in detection_stats['top_keywords']:
                f.write(f"  • {kw}: {count}次\n")

        f.write("\n" + "="*80 + "\n")
        f.write("报告结束\n")
        f.write("="*80 + "\n")

    print(f"   ✓ 保存报告: {report_file}")

    return report_file

def main():
    if len(sys.argv) < 2:
        data_file = 'data/raw/comments_natural_distribution_20251020_200458.json'
        print(f"使用默认数据文件: {data_file}")
    else:
        data_file = sys.argv[1]

    # 创建输出目录
    output_dir = Path('output/analysis')
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print(" YouTube Shorts AI Content Analysis")
    print("="*80)

    # 加载数据
    df = load_data(data_file)
    print(f"✅ 加载 {len(df):,} 条评论\n")

    # 分析
    quarter_stats = analyze_ai_ratio_evolution(df, output_dir)
    interaction_stats = analyze_interaction_comparison(df, output_dir)
    detection_stats = analyze_ai_detection(df, output_dir)
    report_file = generate_report(df, quarter_stats, interaction_stats, detection_stats, output_dir)

    print("\n" + "="*80)
    print(" ✅ 分析完成!")
    print("="*80)
    print(f"\n📁 输出目录: {output_dir}")
    print(f"📊 图表: {list(output_dir.glob('*.png'))}")
    print(f"📄 报告: {report_file}\n")

if __name__ == '__main__':
    main()
