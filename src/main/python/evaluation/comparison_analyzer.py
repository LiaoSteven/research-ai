#!/usr/bin/env python3
"""
AI vs 非AI 内容对比分析

对比 AI 生成内容和非 AI 内容在情感、主题、互动等方面的差异

Usage:
    python scripts/compare_ai_nonai.py \
        --ai data/processed/comments_ai_sentiment_topics.csv \
        --non-ai data/processed/comments_non_ai_sentiment_topics.csv
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats

def calculate_statistics(df_ai, df_non_ai):
    """计算统计数据"""

    results = {
        'sample_sizes': {
            'ai': len(df_ai),
            'non_ai': len(df_non_ai)
        }
    }

    # 1. 情感分布对比
    ai_sentiment = df_ai['sentiment'].value_counts(normalize=True)
    non_ai_sentiment = df_non_ai['sentiment'].value_counts(normalize=True)

    results['sentiment_distribution'] = {
        'ai': ai_sentiment.to_dict(),
        'non_ai': non_ai_sentiment.to_dict()
    }

    # 卡方检验 - 情感分布差异
    if 'sentiment' in df_ai.columns and 'sentiment' in df_non_ai.columns:
        contingency_table = pd.crosstab(
            pd.concat([df_ai, df_non_ai])['sentiment'],
            pd.concat([
                pd.Series(['AI']*len(df_ai)),
                pd.Series(['Non-AI']*len(df_non_ai))
            ])
        )
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        results['sentiment_chi2_test'] = {
            'chi2': float(chi2),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }

    # 2. 情感置信度对比
    if 'sentiment_confidence' in df_ai.columns and 'sentiment_confidence' in df_non_ai.columns:
        results['sentiment_confidence'] = {
            'ai': {
                'mean': float(df_ai['sentiment_confidence'].mean()),
                'median': float(df_ai['sentiment_confidence'].median()),
                'std': float(df_ai['sentiment_confidence'].std())
            },
            'non_ai': {
                'mean': float(df_non_ai['sentiment_confidence'].mean()),
                'median': float(df_non_ai['sentiment_confidence'].median()),
                'std': float(df_non_ai['sentiment_confidence'].std())
            }
        }

        # T检验 - 置信度差异
        t_stat, p_value = stats.ttest_ind(
            df_ai['sentiment_confidence'].dropna(),
            df_non_ai['sentiment_confidence'].dropna()
        )
        results['confidence_ttest'] = {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }

    # 3. 互动数据对比
    if 'like_count' in df_ai.columns and 'like_count' in df_non_ai.columns:
        results['engagement'] = {
            'ai': {
                'total_likes': int(df_ai['like_count'].sum()),
                'mean_likes': float(df_ai['like_count'].mean()),
                'median_likes': float(df_ai['like_count'].median()),
                'max_likes': int(df_ai['like_count'].max())
            },
            'non_ai': {
                'total_likes': int(df_non_ai['like_count'].sum()),
                'mean_likes': float(df_non_ai['like_count'].mean()),
                'median_likes': float(df_non_ai['like_count'].median()),
                'max_likes': int(df_non_ai['like_count'].max())
            }
        }

        # Mann-Whitney U 检验 - 点赞数差异（非参数检验）
        u_stat, p_value = stats.mannwhitneyu(
            df_ai['like_count'].dropna(),
            df_non_ai['like_count'].dropna(),
            alternative='two-sided'
        )
        results['likes_mannwhitney'] = {
            'u_statistic': float(u_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }

    # 4. 主题分布对比
    if 'topic' in df_ai.columns and 'topic' in df_non_ai.columns:
        ai_topics = df_ai[df_ai['topic'] >= 0]['topic'].value_counts(normalize=True)
        non_ai_topics = df_non_ai[df_non_ai['topic'] >= 0]['topic'].value_counts(normalize=True)

        results['topic_distribution'] = {
            'ai': ai_topics.to_dict(),
            'non_ai': non_ai_topics.to_dict()
        }

    # 5. 文本长度对比
    if 'text_length' in df_ai.columns and 'text_length' in df_non_ai.columns:
        results['text_length'] = {
            'ai': {
                'mean': float(df_ai['text_length'].mean()),
                'median': float(df_ai['text_length'].median()),
                'std': float(df_ai['text_length'].std())
            },
            'non_ai': {
                'mean': float(df_non_ai['text_length'].mean()),
                'median': float(df_non_ai['text_length'].median()),
                'std': float(df_non_ai['text_length'].std())
            }
        }

        # T检验 - 文本长度差异
        t_stat, p_value = stats.ttest_ind(
            df_ai['text_length'].dropna(),
            df_non_ai['text_length'].dropna()
        )
        results['length_ttest'] = {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }

    # 6. 情感-主题交叉分析
    if 'sentiment' in df_ai.columns and 'topic' in df_ai.columns:
        # AI 内容的情感-主题分布
        ai_cross = pd.crosstab(
            df_ai[df_ai['topic'] >= 0]['topic'],
            df_ai[df_ai['topic'] >= 0]['sentiment'],
            normalize='index'
        )

        # 非AI 内容的情感-主题分布
        non_ai_cross = pd.crosstab(
            df_non_ai[df_non_ai['topic'] >= 0]['topic'],
            df_non_ai[df_non_ai['topic'] >= 0]['sentiment'],
            normalize='index'
        )

        results['sentiment_topic_cross'] = {
            'ai': ai_cross.to_dict(),
            'non_ai': non_ai_cross.to_dict()
        }

    return results


def generate_report(results, df_ai, df_non_ai):
    """生成对比分析报告"""

    report = []

    report.append("="*70)
    report.append("AI vs 非AI 内容对比分析报告")
    report.append("="*70)
    report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # 1. 样本信息
    report.append("="*70)
    report.append("1. 样本信息")
    report.append("="*70)
    report.append(f"\nAI 内容评论数: {results['sample_sizes']['ai']}")
    report.append(f"非 AI 内容评论数: {results['sample_sizes']['non_ai']}")
    report.append(f"总计: {results['sample_sizes']['ai'] + results['sample_sizes']['non_ai']}")
    report.append("")

    # 2. 情感分布对比
    report.append("="*70)
    report.append("2. 情感分布对比")
    report.append("="*70)
    report.append("")

    report.append("AI 内容情感分布:")
    for sentiment, ratio in results['sentiment_distribution']['ai'].items():
        report.append(f"  {sentiment}: {ratio*100:.1f}%")

    report.append("\n非 AI 内容情感分布:")
    for sentiment, ratio in results['sentiment_distribution']['non_ai'].items():
        report.append(f"  {sentiment}: {ratio*100:.1f}%")

    # 情感分布显著性检验
    if 'sentiment_chi2_test' in results:
        report.append(f"\n卡方检验结果:")
        report.append(f"  χ² = {results['sentiment_chi2_test']['chi2']:.4f}")
        report.append(f"  p-value = {results['sentiment_chi2_test']['p_value']:.4f}")
        if results['sentiment_chi2_test']['significant']:
            report.append(f"  ⭐ 结论: 情感分布存在显著差异 (p < 0.05)")
        else:
            report.append(f"  结论: 情感分布无显著差异 (p >= 0.05)")
    report.append("")

    # 3. 情感置信度对比
    if 'sentiment_confidence' in results:
        report.append("="*70)
        report.append("3. 情感置信度对比")
        report.append("="*70)
        report.append("")

        report.append("AI 内容:")
        report.append(f"  平均置信度: {results['sentiment_confidence']['ai']['mean']:.3f}")
        report.append(f"  中位数: {results['sentiment_confidence']['ai']['median']:.3f}")
        report.append(f"  标准差: {results['sentiment_confidence']['ai']['std']:.3f}")

        report.append("\n非 AI 内容:")
        report.append(f"  平均置信度: {results['sentiment_confidence']['non_ai']['mean']:.3f}")
        report.append(f"  中位数: {results['sentiment_confidence']['non_ai']['median']:.3f}")
        report.append(f"  标准差: {results['sentiment_confidence']['non_ai']['std']:.3f}")

        if 'confidence_ttest' in results:
            report.append(f"\nT检验结果:")
            report.append(f"  t = {results['confidence_ttest']['t_statistic']:.4f}")
            report.append(f"  p-value = {results['confidence_ttest']['p_value']:.4f}")
            if results['confidence_ttest']['significant']:
                report.append(f"  ⭐ 结论: 置信度存在显著差异 (p < 0.05)")
            else:
                report.append(f"  结论: 置信度无显著差异 (p >= 0.05)")
        report.append("")

    # 4. 互动数据对比
    if 'engagement' in results:
        report.append("="*70)
        report.append("4. 互动数据对比")
        report.append("="*70)
        report.append("")

        report.append("AI 内容:")
        report.append(f"  总点赞数: {results['engagement']['ai']['total_likes']}")
        report.append(f"  平均点赞: {results['engagement']['ai']['mean_likes']:.2f}")
        report.append(f"  中位数: {results['engagement']['ai']['median_likes']:.0f}")
        report.append(f"  最高点赞: {results['engagement']['ai']['max_likes']}")

        report.append("\n非 AI 内容:")
        report.append(f"  总点赞数: {results['engagement']['non_ai']['total_likes']}")
        report.append(f"  平均点赞: {results['engagement']['non_ai']['mean_likes']:.2f}")
        report.append(f"  中位数: {results['engagement']['non_ai']['median_likes']:.0f}")
        report.append(f"  最高点赞: {results['engagement']['non_ai']['max_likes']}")

        # 计算比率
        ai_avg = results['engagement']['ai']['mean_likes']
        non_ai_avg = results['engagement']['non_ai']['mean_likes']
        if non_ai_avg > 0:
            ratio = ai_avg / non_ai_avg
            report.append(f"\n⭐ AI 内容平均点赞是非 AI 的 {ratio:.2f} 倍")

        if 'likes_mannwhitney' in results:
            report.append(f"\nMann-Whitney U 检验结果:")
            report.append(f"  U = {results['likes_mannwhitney']['u_statistic']:.2f}")
            report.append(f"  p-value = {results['likes_mannwhitney']['p_value']:.4f}")
            if results['likes_mannwhitney']['significant']:
                report.append(f"  ⭐ 结论: 点赞数存在显著差异 (p < 0.05)")
            else:
                report.append(f"  结论: 点赞数无显著差异 (p >= 0.05)")
        report.append("")

    # 5. 主题分布对比
    if 'topic_distribution' in results:
        report.append("="*70)
        report.append("5. 主题分布对比")
        report.append("="*70)
        report.append("")

        report.append("AI 内容主题分布:")
        for topic, ratio in sorted(results['topic_distribution']['ai'].items()):
            report.append(f"  主题 {int(topic)}: {ratio*100:.1f}%")

        report.append("\n非 AI 内容主题分布:")
        for topic, ratio in sorted(results['topic_distribution']['non_ai'].items()):
            report.append(f"  主题 {int(topic)}: {ratio*100:.1f}%")
        report.append("")

    # 6. 文本长度对比
    if 'text_length' in results:
        report.append("="*70)
        report.append("6. 文本长度对比")
        report.append("="*70)
        report.append("")

        report.append("AI 内容:")
        report.append(f"  平均长度: {results['text_length']['ai']['mean']:.1f} 字符")
        report.append(f"  中位数: {results['text_length']['ai']['median']:.0f} 字符")

        report.append("\n非 AI 内容:")
        report.append(f"  平均长度: {results['text_length']['non_ai']['mean']:.1f} 字符")
        report.append(f"  中位数: {results['text_length']['non_ai']['median']:.0f} 字符")

        if 'length_ttest' in results:
            report.append(f"\nT检验结果:")
            report.append(f"  t = {results['length_ttest']['t_statistic']:.4f}")
            report.append(f"  p-value = {results['length_ttest']['p_value']:.4f}")
            if results['length_ttest']['significant']:
                report.append(f"  ⭐ 结论: 文本长度存在显著差异 (p < 0.05)")
            else:
                report.append(f"  结论: 文本长度无显著差异 (p >= 0.05)")
        report.append("")

    # 7. 关键发现总结
    report.append("="*70)
    report.append("7. 关键发现总结")
    report.append("="*70)
    report.append("")

    findings = []

    # 情感差异
    if 'sentiment_chi2_test' in results and results['sentiment_chi2_test']['significant']:
        ai_pos = results['sentiment_distribution']['ai'].get('positive', 0)
        non_ai_pos = results['sentiment_distribution']['non_ai'].get('positive', 0)
        if ai_pos > non_ai_pos:
            findings.append(f"• AI 内容的积极情感比例更高 ({ai_pos*100:.1f}% vs {non_ai_pos*100:.1f}%)")
        else:
            findings.append(f"• 非 AI 内容的积极情感比例更高 ({non_ai_pos*100:.1f}% vs {ai_pos*100:.1f}%)")

    # 互动差异
    if 'likes_mannwhitney' in results and results['likes_mannwhitney']['significant']:
        ai_avg = results['engagement']['ai']['mean_likes']
        non_ai_avg = results['engagement']['non_ai']['mean_likes']
        if ai_avg > non_ai_avg:
            findings.append(f"• AI 内容获得更多互动（平均 {ai_avg:.2f} vs {non_ai_avg:.2f} 赞）")
        else:
            findings.append(f"• 非 AI 内容获得更多互动（平均 {non_ai_avg:.2f} vs {ai_avg:.2f} 赞）")

    # 文本长度差异
    if 'length_ttest' in results and results['length_ttest']['significant']:
        ai_len = results['text_length']['ai']['mean']
        non_ai_len = results['text_length']['non_ai']['mean']
        if ai_len > non_ai_len:
            findings.append(f"• AI 内容评论更长（平均 {ai_len:.1f} vs {non_ai_len:.1f} 字符）")
        else:
            findings.append(f"• 非 AI 内容评论更长（平均 {non_ai_len:.1f} vs {ai_len:.1f} 字符）")

    if findings:
        report.extend(findings)
    else:
        report.append("• 未发现统计学上显著的差异")

    report.append("")
    report.append("="*70)
    report.append("报告结束")
    report.append("="*70)

    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='AI vs 非AI 内容对比分析')
    parser.add_argument('--ai', required=True, help='AI 内容数据文件')
    parser.add_argument('--non-ai', required=True, help='非 AI 内容数据文件')
    parser.add_argument('--output', default='output/reports', help='输出目录')

    args = parser.parse_args()

    print("="*70)
    print(" AI vs 非AI 内容对比分析")
    print("="*70)

    # 读取数据
    print(f"\n📊 加载数据...")
    try:
        df_ai = pd.read_csv(args.ai)
        print(f"  AI 内容: {len(df_ai)} 条评论")
    except FileNotFoundError:
        print(f"❌ 找不到 AI 内容文件: {args.ai}")
        return 1

    try:
        df_non_ai = pd.read_csv(args.non_ai)
        print(f"  非 AI 内容: {len(df_non_ai)} 条评论")
    except FileNotFoundError:
        print(f"❌ 找不到非 AI 内容文件: {args.non_ai}")
        return 1

    # 计算统计数据
    print(f"\n🔬 进行统计分析...")
    results = calculate_statistics(df_ai, df_non_ai)

    # 生成报告
    print(f"\n📝 生成对比报告...")
    report_text = generate_report(results, df_ai, df_non_ai)

    # 保存报告
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"ai_vs_nonai_comparison_{timestamp}.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)

    # 保存统计数据（JSON）
    import json
    stats_path = output_dir / f"ai_vs_nonai_stats_{timestamp}.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 分析完成！")
    print(f"\n📄 报告已保存:")
    print(f"  文本报告: {report_path}")
    print(f"  统计数据: {stats_path}")

    # 显示报告预览
    print("\n" + "="*70)
    print("报告预览:")
    print("="*70)
    print(report_text)

    return 0


if __name__ == '__main__':
    sys.exit(main())
