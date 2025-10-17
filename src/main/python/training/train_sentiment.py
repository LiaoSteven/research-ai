#!/usr/bin/env python3
"""
情感分析脚本 - 分析预处理后的评论情感

Usage:
    python scripts/run_sentiment.py --input data/processed/comments.csv
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'main' / 'python'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from models.sentiment_analyzer import SentimentAnalyzer

def main():
    parser = argparse.ArgumentParser(description='运行情感分析')
    parser.add_argument('--input', required=True, help='输入CSV文件路径')
    parser.add_argument('--output', help='输出CSV文件路径（可选，默认添加_sentiment后缀）')
    parser.add_argument('--backend', default='simple', choices=['simple', 'transformers'],
                        help='使用的后端（simple或transformers，默认simple）')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_path}")
        sys.exit(1)

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_sentiment{input_path.suffix}"

    print("="*70)
    print(" 情感分析")
    print("="*70)
    print(f"\n📂 输入文件: {input_path}")
    print(f"📂 输出文件: {output_path}")
    print(f"🤖 后端: {args.backend}")

    # 读取数据
    print(f"\n📊 加载数据...")
    df = pd.read_csv(input_path)
    print(f"  - 评论数量: {len(df)}")

    # 初始化情感分析器
    print(f"\n🔧 初始化情感分析器...")
    analyzer = SentimentAnalyzer(backend=args.backend)

    # 分析情感
    print(f"\n🎭 开始分析情感...")
    text_column = 'text_clean' if 'text_clean' in df.columns else 'text'

    results = []
    for idx, row in df.iterrows():
        text = row[text_column]
        result = analyzer.analyze(text)
        results.append(result)

        if (idx + 1) % 100 == 0:
            print(f"  进度: {idx + 1}/{len(df)} ({(idx+1)/len(df)*100:.1f}%)")

    # 添加结果到DataFrame
    df['sentiment'] = [r['sentiment'] for r in results]
    df['sentiment_confidence'] = [r['confidence'] for r in results]
    df['sentiment_analyzed_at'] = datetime.now().isoformat()

    # 保存结果
    print(f"\n💾 保存结果到: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')

    # 统计结果
    print(f"\n📈 情感分析结果统计:")
    sentiment_counts = df['sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        percentage = count / len(df) * 100
        print(f"  {sentiment}: {count} ({percentage:.1f}%)")

    print(f"\n📊 情感置信度统计:")
    print(f"  平均置信度: {df['sentiment_confidence'].mean():.3f}")
    print(f"  中位数: {df['sentiment_confidence'].median():.3f}")
    print(f"  最高: {df['sentiment_confidence'].max():.3f}")
    print(f"  最低: {df['sentiment_confidence'].min():.3f}")

    # 显示样本
    print(f"\n🔥 最积极的评论 (Top 3):")
    top_positive = df[df['sentiment'] == 'positive'].nlargest(3, 'sentiment_confidence')
    for i, (idx, row) in enumerate(top_positive.iterrows(), 1):
        print(f"\n  {i}. 置信度: {row['sentiment_confidence']:.3f} ({row['sentiment']})")
        text = row[text_column][:100] + "..." if len(row[text_column]) > 100 else row[text_column]
        print(f"     {text}")

    print(f"\n❄️  最消极的评论 (Top 3):")
    top_negative = df[df['sentiment'] == 'negative'].nlargest(3, 'sentiment_confidence')
    for i, (idx, row) in enumerate(top_negative.iterrows(), 1):
        print(f"\n  {i}. 置信度: {row['sentiment_confidence']:.3f} ({row['sentiment']})")
        text = row[text_column][:100] + "..." if len(row[text_column]) > 100 else row[text_column]
        print(f"     {text}")

    print("\n" + "="*70)
    print("✅ 情感分析完成")
    print("="*70)

    print(f"\n💡 下一步建议:")
    print(f"  1. 运行主题建模: python scripts/run_topic_model.py --input {output_path}")
    print(f"  2. 可视化结果: python scripts/visualize_sentiment.py --input {output_path}")
    print(f"  3. 深入分析: 使用 pandas 或 Jupyter notebook 探索数据")
    print()

if __name__ == '__main__':
    main()
