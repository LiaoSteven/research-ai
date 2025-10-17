#!/usr/bin/env python3
"""
基础数据分析 - 查看预处理后的数据

Usage:
    python analyze_basic.py data/processed/comments.csv
"""

import sys
import pandas as pd
from pathlib import Path

if len(sys.argv) < 2:
    print("用法: python analyze_basic.py <comments.csv>")
    sys.exit(1)

file_path = sys.argv[1]

# 读取数据
print("📂 加载数据...")
df = pd.read_csv(file_path)

print("\n" + "="*70)
print(f" 数据分析：{Path(file_path).name}")
print("="*70)

# 基本信息
print(f"\n📊 数据维度：")
print(f"  行数：{len(df)}")
print(f"  列数：{len(df.columns)}")

print(f"\n📋 列名：")
for col in df.columns:
    print(f"  - {col}")

# 统计信息
print(f"\n📈 文本统计：")
if 'text_length' in df.columns:
    print(f"  平均文本长度：{df['text_length'].mean():.1f} 字符")
    print(f"  中位数：{df['text_length'].median():.0f} 字符")
    print(f"  最短：{df['text_length'].min()}")
    print(f"  最长：{df['text_length'].max()}")

if 'word_count' in df.columns:
    print(f"\n  平均词数：{df['word_count'].mean():.1f}")
    print(f"  中位数：{df['word_count'].median():.0f}")

# 互动统计
print(f"\n👍 互动统计：")
if 'like_count' in df.columns:
    print(f"  总点赞数：{df['like_count'].sum()}")
    print(f"  平均点赞：{df['like_count'].mean():.1f}")
    print(f"  最高点赞：{df['like_count'].max()}")

    # 热门评论
    top_comments = df.nlargest(3, 'like_count')
    print(f"\n🔥 最热门评论（Top 3）：")
    for i, (idx, row) in enumerate(top_comments.iterrows(), 1):
        text = row['text_clean'][:80] if pd.notna(row.get('text_clean')) else row['text'][:80]
        print(f"\n  {i}. 👍 {row['like_count']} 赞")
        print(f"     {text}...")

# 时间分布
if 'published_datetime' in df.columns:
    print(f"\n📅 时间分布：")
    df['published_datetime'] = pd.to_datetime(df['published_datetime'])
    print(f"  时间跨度：{df['published_datetime'].min()} 到 {df['published_datetime'].max()}")

    if 'published_date' in df.columns:
        date_counts = df['published_date'].value_counts().head(5)
        print(f"\n  发布最多的日期：")
        for date, count in date_counts.items():
            print(f"    {date}: {count} 条评论")

# 作者分析
if 'author' in df.columns:
    print(f"\n👥 作者分析：")
    print(f"  独立作者：{df['author'].nunique()}")

    top_authors = df['author'].value_counts().head(5)
    print(f"\n  最活跃作者：")
    for author, count in top_authors.items():
        print(f"    {author}: {count} 条评论")

# 视频分布
if 'video_id' in df.columns:
    print(f"\n🎬 视频分析：")
    print(f"  涉及视频：{df['video_id'].nunique()}")

    video_counts = df['video_id'].value_counts().head(5)
    print(f"\n  评论最多的视频：")
    for video_id, count in video_counts.items():
        print(f"    {video_id}: {count} 条评论")

# 保存快速统计
summary = {
    'total_comments': len(df),
    'unique_authors': df['author'].nunique() if 'author' in df.columns else 0,
    'unique_videos': df['video_id'].nunique() if 'video_id' in df.columns else 0,
    'avg_text_length': df['text_length'].mean() if 'text_length' in df.columns else 0,
    'avg_word_count': df['word_count'].mean() if 'word_count' in df.columns else 0,
    'total_likes': df['like_count'].sum() if 'like_count' in df.columns else 0,
}

print("\n" + "="*70)
print("✅ 数据分析完成")
print("="*70)

print(f"\n💡 下一步建议：")
print(f"  1. 运行情感分析识别正面/负面评论")
print(f"  2. 进行主题建模发现讨论话题")
print(f"  3. 使用 pandas/Excel 深入探索数据")
print()
