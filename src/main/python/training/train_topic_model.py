#!/usr/bin/env python3
"""
主题建模脚本 - 提取评论中的核心讨论话题

Usage:
    python scripts/run_topic_model.py --input data/processed/comments_sentiment.csv
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'main' / 'python'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from models.topic_model import TopicModel

def main():
    parser = argparse.ArgumentParser(description='运行主题建模')
    parser.add_argument('--input', required=True, help='输入CSV文件路径')
    parser.add_argument('--output', help='输出CSV文件路径（可选）')
    parser.add_argument('--n-topics', type=int, default=5, help='主题数量（默认5）')
    parser.add_argument('--backend', default='lda', choices=['lda', 'nmf'],
                        help='使用的算法（lda或nmf，默认lda）')
    parser.add_argument('--language', default='spanish', choices=['chinese', 'english', 'spanish', 'multilingual'],
                        help='文本语言（默认spanish）')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 输入文件不存在: {input_path}")
        sys.exit(1)

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_topics{input_path.suffix}"

    print("="*70)
    print(" 主题建模分析")
    print("="*70)
    print(f"\n📂 输入文件: {input_path}")
    print(f"📂 输出文件: {output_path}")
    print(f"🤖 算法: {args.backend.upper()}")
    print(f"🌍 语言: {args.language}")
    print(f"📊 主题数量: {args.n_topics}")

    # 读取数据
    print(f"\n📊 加载数据...")
    df = pd.read_csv(input_path)
    print(f"  - 评论数量: {len(df)}")

    # 选择文本列
    text_column = 'text_clean' if 'text_clean' in df.columns else 'text'
    texts = df[text_column].fillna('').tolist()

    # 过滤空文本和过短文本
    min_length = 10
    valid_indices = [i for i, text in enumerate(texts) if len(text.strip()) >= min_length]
    valid_texts = [texts[i] for i in valid_indices]

    print(f"  - 有效文本数: {len(valid_texts)} (过滤了 {len(texts) - len(valid_texts)} 条过短文本)")

    if len(valid_texts) < args.n_topics:
        print(f"❌ 有效文本数量 ({len(valid_texts)}) 少于主题数量 ({args.n_topics})")
        print(f"建议: 减少主题数量或使用更多数据")
        sys.exit(1)

    # 初始化主题模型
    print(f"\n🔧 初始化主题模型...")
    topic_model = TopicModel(
        n_topics=args.n_topics,
        backend=args.backend,
        language=args.language
    )

    # 训练模型
    print(f"\n🎯 训练主题模型...")
    print(f"  (这可能需要几分钟...)")

    try:
        topic_model.fit(valid_texts)
        print(f"  ✅ 模型训练完成")
    except Exception as e:
        print(f"  ❌ 训练失败: {e}")
        sys.exit(1)

    # 为所有文本分配主题
    print(f"\n📋 分配主题标签...")
    all_topics = []
    all_topic_probs = []

    for i, text in enumerate(texts):
        if i in valid_indices:
            # 有效文本，使用模型预测
            result = topic_model.transform([text])
            all_topics.append(result['topics'][0])
            all_topic_probs.append(result['probabilities'][0])
        else:
            # 无效文本，分配 -1
            all_topics.append(-1)
            all_topic_probs.append(0.0)

    # 添加结果到DataFrame
    df['topic'] = all_topics
    df['topic_probability'] = all_topic_probs
    df['topic_analyzed_at'] = datetime.now().isoformat()

    # 保存结果
    print(f"\n💾 保存结果到: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')

    # 显示主题
    print(f"\n" + "="*70)
    print(" 发现的主题 (Discovered Topics)")
    print("="*70)

    topics_info = topic_model.get_topics()

    for topic_id, words in topics_info.items():
        if topic_id == -1:
            continue

        # 统计这个主题的评论数
        topic_count = (df['topic'] == topic_id).sum()
        percentage = topic_count / len(df) * 100

        print(f"\n📌 主题 {topic_id} ({topic_count} 条评论, {percentage:.1f}%)")
        print(f"   关键词: {', '.join(words[:10])}")

    # 每个主题的代表性评论
    print(f"\n" + "="*70)
    print(" 主题代表性评论 (Representative Comments)")
    print("="*70)

    for topic_id in range(args.n_topics):
        topic_comments = df[df['topic'] == topic_id].nlargest(3, 'topic_probability')

        if len(topic_comments) == 0:
            continue

        print(f"\n📌 主题 {topic_id}:")
        for i, (idx, row) in enumerate(topic_comments.iterrows(), 1):
            text = row[text_column][:100] + "..." if len(row[text_column]) > 100 else row[text_column]
            prob = row['topic_probability']
            print(f"  {i}. (概率: {prob:.3f}) {text}")

    # 情感与主题的关系分析
    if 'sentiment' in df.columns:
        print(f"\n" + "="*70)
        print(" 情感-主题关系分析")
        print("="*70)

        for topic_id in range(args.n_topics):
            topic_df = df[df['topic'] == topic_id]
            if len(topic_df) == 0:
                continue

            sentiment_dist = topic_df['sentiment'].value_counts()
            print(f"\n📌 主题 {topic_id} 情感分布:")
            for sentiment, count in sentiment_dist.items():
                percentage = count / len(topic_df) * 100
                print(f"   {sentiment}: {count} ({percentage:.1f}%)")

    # 统计摘要
    print(f"\n" + "="*70)
    print(" 统计摘要")
    print("="*70)

    print(f"\n总评论数: {len(df)}")
    print(f"有效主题分配: {(df['topic'] >= 0).sum()}")
    print(f"无效文本: {(df['topic'] == -1).sum()}")

    topic_dist = df[df['topic'] >= 0]['topic'].value_counts().sort_index()
    print(f"\n主题分布:")
    for topic_id, count in topic_dist.items():
        percentage = count / len(df) * 100
        print(f"  主题 {topic_id}: {count} ({percentage:.1f}%)")

    print("\n" + "="*70)
    print("✅ 主题建模完成")
    print("="*70)

    print(f"\n💡 下一步建议:")
    print(f"  1. 可视化主题: python scripts/visualize_topics.py --input {output_path}")
    print(f"  2. 生成综合分析报告: python scripts/generate_report.py --input {output_path}")
    print(f"  3. 深入探索: 使用 Jupyter notebook 分析主题-情感-互动关系")
    print()

if __name__ == '__main__':
    main()
