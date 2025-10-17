#!/usr/bin/env python3
"""
综合分析报告生成器 - 生成完整的研究分析报告

Usage:
    python scripts/generate_report.py --input data/processed/comments_sentiment_topics.csv
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def main():
    parser = argparse.ArgumentParser(description='生成综合分析报告')
    parser.add_argument('--input', required=True, help='输入CSV文件路径')
    parser.add_argument('--output-dir', default='output/reports', help='输出目录')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_path}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print(" 综合分析报告生成")
    print("="*70)
    print(f"\n📂 输入文件: {input_path}")
    print(f"📂 输出目录: {output_dir}")

    # 读取数据
    print(f"\n📊 加载数据...")
    df = pd.read_csv(input_path)
    print(f"  - 评论数量: {len(df)}")

    # 生成报告
    report = []

    # 标题和元信息
    report.append("="*70)
    report.append("YouTube Shorts 评论分析 - 综合研究报告")
    report.append("="*70)
    report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"数据文件: {input_path}")
    report.append(f"分析评论数: {len(df)}")
    report.append("")

    # 1. 数据概览
    report.append("="*70)
    report.append("1. 数据概览 (Data Overview)")
    report.append("="*70)
    report.append("")

    # 基本统计
    report.append("1.1 基本统计")
    report.append(f"  总评论数: {len(df)}")
    if 'video_id' in df.columns:
        report.append(f"  涉及视频: {df['video_id'].nunique()} 个")
    if 'author' in df.columns:
        report.append(f"  独立作者: {df['author'].nunique()} 人")
    if 'published_datetime' in df.columns:
        df['published_datetime'] = pd.to_datetime(df['published_datetime'])
        date_range = f"{df['published_datetime'].min().date()} 至 {df['published_datetime'].max().date()}"
        report.append(f"  时间跨度: {date_range}")
    report.append("")

    # 文本统计
    if 'text_length' in df.columns:
        report.append("1.2 文本统计")
        report.append(f"  平均长度: {df['text_length'].mean():.1f} 字符")
        report.append(f"  中位数: {df['text_length'].median():.0f} 字符")
        report.append(f"  最短: {df['text_length'].min()} 字符")
        report.append(f"  最长: {df['text_length'].max()} 字符")
        if 'word_count' in df.columns:
            report.append(f"  平均词数: {df['word_count'].mean():.1f}")
        report.append("")

    # 互动统计
    if 'like_count' in df.columns:
        report.append("1.3 互动统计")
        report.append(f"  总点赞数: {df['like_count'].sum()}")
        report.append(f"  平均点赞: {df['like_count'].mean():.2f}")
        report.append(f"  中位数: {df['like_count'].median():.0f}")
        report.append(f"  最高点赞: {df['like_count'].max()}")
        if 'reply_count' in df.columns:
            report.append(f"  总回复数: {df['reply_count'].sum()}")
        report.append("")

    # 2. 情感分析结果
    if 'sentiment' in df.columns:
        report.append("="*70)
        report.append("2. 情感分析结果 (Sentiment Analysis)")
        report.append("="*70)
        report.append("")

        sentiment_counts = df['sentiment'].value_counts()
        report.append("2.1 情感分布")
        for sentiment, count in sentiment_counts.items():
            percentage = count / len(df) * 100
            report.append(f"  {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
        report.append("")

        # 置信度统计
        if 'sentiment_confidence' in df.columns:
            report.append("2.2 情感置信度")
            report.append(f"  平均: {df['sentiment_confidence'].mean():.3f}")
            report.append(f"  中位数: {df['sentiment_confidence'].median():.3f}")
            report.append(f"  范围: {df['sentiment_confidence'].min():.3f} - {df['sentiment_confidence'].max():.3f}")
            report.append("")

        # 情感与点赞关系
        if 'like_count' in df.columns:
            report.append("2.3 情感与互动关系")
            for sentiment in ['positive', 'negative', 'neutral']:
                if sentiment in df['sentiment'].values:
                    subset = df[df['sentiment'] == sentiment]
                    report.append(f"  {sentiment.capitalize()} 评论:")
                    report.append(f"    平均点赞: {subset['like_count'].mean():.2f}")
                    report.append(f"    中位数: {subset['like_count'].median():.0f}")
                    report.append(f"    最高: {subset['like_count'].max()}")
            report.append("")

            # 关键发现
            pos_avg = df[df['sentiment'] == 'positive']['like_count'].mean() if 'positive' in df['sentiment'].values else 0
            neu_avg = df[df['sentiment'] == 'neutral']['like_count'].mean() if 'neutral' in df['sentiment'].values else 0
            if pos_avg > 0 and neu_avg > 0:
                ratio = pos_avg / neu_avg
                report.append(f"  ⭐ 关键发现: 积极评论获得的平均点赞是中性评论的 {ratio:.1f} 倍")
                report.append("")

    # 3. 主题建模结果
    if 'topic' in df.columns:
        report.append("="*70)
        report.append("3. 主题建模结果 (Topic Modeling)")
        report.append("="*70)
        report.append("")

        valid_topics = df[df['topic'] >= 0]
        report.append(f"3.1 主题分布 (有效主题分配: {len(valid_topics)})")
        topic_counts = valid_topics['topic'].value_counts().sort_index()
        for topic_id, count in topic_counts.items():
            percentage = count / len(df) * 100
            report.append(f"  主题 {topic_id}: {count} ({percentage:.1f}%)")
        report.append("")

        # 主题-情感交叉分析
        if 'sentiment' in df.columns:
            report.append("3.2 主题-情感交叉分析")
            for topic_id in sorted(valid_topics['topic'].unique()):
                topic_df = df[df['topic'] == topic_id]
                sentiment_dist = topic_df['sentiment'].value_counts()

                report.append(f"\n  主题 {topic_id} ({len(topic_df)} 条评论):")

                # 计算积极率
                pos_count = sentiment_dist.get('positive', 0)
                pos_ratio = pos_count / len(topic_df) * 100

                for sentiment, count in sentiment_dist.items():
                    percentage = count / len(topic_df) * 100
                    report.append(f"    {sentiment}: {count} ({percentage:.1f}%)")

                # 平均点赞
                if 'like_count' in df.columns:
                    avg_likes = topic_df['like_count'].mean()
                    report.append(f"    平均点赞: {avg_likes:.2f}")

            report.append("")

    # 4. 时间序列分析
    if 'published_datetime' in df.columns:
        report.append("="*70)
        report.append("4. 时间分析 (Temporal Analysis)")
        report.append("="*70)
        report.append("")

        df['published_date'] = df['published_datetime'].dt.date

        # 每日评论数
        report.append("4.1 每日评论分布")
        daily_counts = df['published_date'].value_counts().sort_index()
        for date, count in daily_counts.items():
            report.append(f"  {date}: {count} 条")
        report.append("")

        # 每日情感分布
        if 'sentiment' in df.columns:
            report.append("4.2 每日情感分布")
            daily_sentiment = df.groupby(['published_date', 'sentiment']).size().unstack(fill_value=0)
            for date in daily_sentiment.index:
                report.append(f"  {date}:")
                for sentiment in daily_sentiment.columns:
                    count = daily_sentiment.loc[date, sentiment]
                    if count > 0:
                        report.append(f"    {sentiment}: {count}")
            report.append("")

    # 5. 热门评论分析
    if 'like_count' in df.columns:
        report.append("="*70)
        report.append("5. 热门评论分析 (Popular Comments)")
        report.append("="*70)
        report.append("")

        text_column = 'text_clean' if 'text_clean' in df.columns else 'text'

        # Top 10 最热门评论
        report.append("5.1 最热门评论 (Top 10)")
        top_comments = df.nlargest(10, 'like_count')
        for i, (idx, row) in enumerate(top_comments.iterrows(), 1):
            text = row[text_column][:100] + "..." if len(row[text_column]) > 100 else row[text_column]
            report.append(f"\n  {i}. 👍 {row['like_count']} 赞")
            if 'sentiment' in df.columns:
                report.append(f"     情感: {row['sentiment']}")
            if 'topic' in df.columns and row['topic'] >= 0:
                report.append(f"     主题: {int(row['topic'])}")
            report.append(f"     内容: {text}")

        report.append("")

    # 6. 研究发现总结
    report.append("="*70)
    report.append("6. 研究发现总结 (Key Findings)")
    report.append("="*70)
    report.append("")

    findings = []

    # 情感发现
    if 'sentiment' in df.columns:
        sentiment_counts = df['sentiment'].value_counts()
        dominant_sentiment = sentiment_counts.idxmax()
        dominant_pct = sentiment_counts.max() / len(df) * 100
        findings.append(f"• 主导情感为 {dominant_sentiment} ({dominant_pct:.1f}%)")

        if 'like_count' in df.columns:
            pos_avg = df[df['sentiment'] == 'positive']['like_count'].mean() if 'positive' in df['sentiment'].values else 0
            neu_avg = df[df['sentiment'] == 'neutral']['like_count'].mean() if 'neutral' in df['sentiment'].values else 0
            neg_avg = df[df['sentiment'] == 'negative']['like_count'].mean() if 'negative' in df['sentiment'].values else 0

            if pos_avg > max(neu_avg, neg_avg):
                findings.append(f"• 积极评论获得更多互动 (平均 {pos_avg:.2f} 赞)")

    # 主题发现
    if 'topic' in df.columns:
        valid_topics = df[df['topic'] >= 0]
        if len(valid_topics) > 0:
            topic_counts = valid_topics['topic'].value_counts()
            largest_topic = topic_counts.idxmax()
            largest_pct = topic_counts.max() / len(df) * 100
            findings.append(f"• 最大主题群组为主题 {largest_topic} ({largest_pct:.1f}%)")

    # 互动发现
    if 'like_count' in df.columns:
        high_engagement = (df['like_count'] > df['like_count'].quantile(0.9)).sum()
        high_pct = high_engagement / len(df) * 100
        findings.append(f"• 高互动评论 (>90th percentile) 占 {high_pct:.1f}%")

    # 时间发现
    if 'published_datetime' in df.columns:
        df['hour'] = df['published_datetime'].dt.hour
        peak_hour = df['hour'].mode()[0] if len(df['hour'].mode()) > 0 else None
        if peak_hour is not None:
            findings.append(f"• 评论高峰时段为 {peak_hour}:00")

    report.append("\n".join(findings))
    report.append("")

    # 7. 方法论说明
    report.append("="*70)
    report.append("7. 方法论 (Methodology)")
    report.append("="*70)
    report.append("")
    report.append("7.1 数据采集")
    report.append("  - 平台: YouTube Shorts")
    report.append("  - API: YouTube Data API v3")
    report.append("  - 采集方式: 自动化热门视频采集")
    report.append("")
    report.append("7.2 数据预处理")
    report.append("  - 文本清洗和标准化")
    report.append("  - 垃圾评论过滤")
    report.append("  - 重复评论去除")
    report.append("  - 时间特征提取")
    report.append("")
    report.append("7.3 情感分析")
    report.append("  - 方法: 基于规则的多语言情感分析")
    report.append("  - 语言支持: 中文、英语、西班牙语")
    report.append("  - 分类: Positive, Negative, Neutral")
    report.append("")
    report.append("7.4 主题建模")
    report.append("  - 算法: LDA (Latent Dirichlet Allocation)")
    report.append("  - 预处理: Stop words removal, tokenization")
    report.append("  - 主题数量: 5")
    report.append("")

    # 8. 结论
    report.append("="*70)
    report.append("8. 结论与建议 (Conclusions)")
    report.append("="*70)
    report.append("")
    report.append("本研究通过分析 YouTube Shorts 评论，揭示了观众的情感倾向、讨论")
    report.append("主题和互动模式。主要发现包括：")
    report.append("")

    if 'sentiment' in df.columns and 'like_count' in df.columns:
        pos_avg = df[df['sentiment'] == 'positive']['like_count'].mean() if 'positive' in df['sentiment'].values else 0
        neu_avg = df[df['sentiment'] == 'neutral']['like_count'].mean() if 'neutral' in df['sentiment'].values else 0
        if pos_avg > neu_avg:
            report.append("1. 积极情感评论获得显著更多的用户互动，表明正面内容更容易引")
            report.append("   起观众共鸣和支持。")
            report.append("")

    if 'sentiment' in df.columns:
        sentiment_counts = df['sentiment'].value_counts()
        if 'neutral' in sentiment_counts.index and sentiment_counts['neutral'] > sentiment_counts.sum() * 0.5:
            report.append("2. 大多数评论呈现中性情感，说明观众主要发表客观评论而非强烈")
            report.append("   的情绪反应。")
            report.append("")

    if 'topic' in df.columns:
        report.append("3. 评论主题呈现多样化分布，反映了不同观众群体的兴趣和关注点。")
        report.append("")

    report.append("建议后续研究方向：")
    report.append("• 扩大数据集规模，采集更多视频类别的评论")
    report.append("• 进行 AI 生成内容 vs 非 AI 内容的对比分析")
    report.append("• 追踪长期时间序列数据 (2022-至今) 的情感演变")
    report.append("• 使用深度学习模型提升情感分析和主题建模精度")
    report.append("")

    report.append("="*70)
    report.append("报告生成完毕")
    report.append("="*70)

    # 保存报告
    report_path = output_dir / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"\n✅ 报告已保存到: {report_path}")

    # 同时输出到控制台
    print("\n" + "="*70)
    print("报告预览:")
    print("="*70)
    for line in report[:50]:  # 显示前50行
        print(line)
    print("\n... (完整报告请查看文件)")

    print(f"\n📊 报告统计:")
    print(f"  - 总行数: {len(report)}")
    print(f"  - 文件大小: {report_path.stat().st_size / 1024:.1f} KB")

    print("\n" + "="*70)
    print("✅ 综合分析报告生成完成")
    print("="*70)
    print()

if __name__ == '__main__':
    main()
