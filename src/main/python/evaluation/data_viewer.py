#!/usr/bin/env python3
"""
快速查看采集的数据

Usage:
    python view_data.py data/raw/comments_20251017_184926.json
"""

import sys
import json
from pathlib import Path

if len(sys.argv) < 2:
    print("用法: python view_data.py <comments_file.json>")
    sys.exit(1)

file_path = sys.argv[1]

# 读取数据
with open(file_path, 'r', encoding='utf-8') as f:
    comments = json.load(f)

print("\n" + "="*70)
print(f" 数据概览：{Path(file_path).name}")
print("="*70)

print(f"\n📊 基本统计：")
print(f"  总评论数：{len(comments)}")

# 统计视频数
video_ids = set(c['video_id'] for c in comments)
print(f"  涉及视频：{len(video_ids)}")

# 统计作者数
authors = set(c['author'] for c in comments)
print(f"  独立作者：{len(authors)}")

# 统计回复
replies = sum(1 for c in comments if c.get('is_reply', False))
print(f"  回复数：{replies}")
print(f"  顶层评论：{len(comments) - replies}")

# 文本长度统计
lengths = [len(c['text']) for c in comments]
print(f"\n📝 文本统计：")
print(f"  平均长度：{sum(lengths)/len(lengths):.1f} 字符")
print(f"  最短：{min(lengths)} 字符")
print(f"  最长：{max(lengths)} 字符")

# 点赞统计
likes = [c.get('like_count', 0) for c in comments]
print(f"\n👍 点赞统计：")
print(f"  总点赞数：{sum(likes)}")
print(f"  平均点赞：{sum(likes)/len(likes):.1f}")
print(f"  最高点赞：{max(likes)}")

# 时间范围
dates = [c.get('published_at', '') for c in comments if c.get('published_at')]
if dates:
    print(f"\n📅 时间范围：")
    print(f"  最早：{min(dates)[:10]}")
    print(f"  最晚：{max(dates)[:10]}")

# 显示样本
print(f"\n📝 评论样本（前 5 条）：")
print("-" * 70)
for i, comment in enumerate(comments[:5], 1):
    text = comment['text'][:100] + "..." if len(comment['text']) > 100 else comment['text']
    print(f"\n{i}. @{comment['author']}")
    print(f"   {text}")
    print(f"   👍 {comment.get('like_count', 0)} | 📅 {comment.get('published_at', 'N/A')[:10]}")

print("\n" + "="*70)
print("✅ 数据已准备好进行预处理和分析")
print("="*70 + "\n")
