#!/usr/bin/env python3
"""
主题建模分析 - LDA Topic Modeling
对YouTube评论进行主题分析,识别讨论的主要话题
"""

import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re

def preprocess_text(text):
    """预处理文本"""
    if pd.isna(text):
        return ""
    # 转小写
    text = text.lower()
    # 移除URL
    text = re.sub(r'http\S+|www\S+', '', text)
    # 移除特殊字符,保留字母数字和空格
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # 移除多余空格
    text = ' '.join(text.split())
    return text

def get_top_words_per_topic(model, feature_names, n_top_words=10):
    """获取每个主题的top关键词"""
    topics = {}
    for topic_idx, topic in enumerate(model.components_):
        top_indices = topic.argsort()[-n_top_words:][::-1]
        top_words = [feature_names[i] for i in top_indices]
        topics[f"Topic {topic_idx}"] = top_words
    return topics

def generate_topic_labels(topics_words):
    """根据关键词生成主题标签"""
    labels = {}

    # 预定义的主题模式
    patterns = {
        'AI/Technology': ['ai', 'artificial', 'intelligence', 'machine', 'learning',
                         'chatgpt', 'gpt', 'model', 'neural', 'algorithm'],
        'Creative/Art': ['art', 'creative', 'design', 'drawing', 'painting',
                        'artist', 'artwork', 'create', 'style', 'image'],
        'Video Content': ['video', 'content', 'channel', 'watch', 'subscribe',
                         'shorts', 'youtube', 'creator', 'views'],
        'Tutorial/Education': ['tutorial', 'learn', 'how', 'make', 'easy',
                              'step', 'guide', 'tips', 'help', 'show'],
        'Animation': ['animation', 'animated', 'cartoon', 'character',
                     'motion', 'graphics', 'animate'],
        'Music/Sound': ['music', 'song', 'sound', 'audio', 'beat', 'track'],
        'Gaming': ['game', 'play', 'gaming', 'player', 'level'],
        'General Discussion': ['good', 'nice', 'cool', 'awesome', 'great',
                              'amazing', 'best', 'wow', 'like', 'love']
    }

    for topic_name, words in topics_words.items():
        # 检查每个预定义模式
        best_match = 'Unknown Topic'
        best_score = 0

        for pattern_name, pattern_words in patterns.items():
            # 计算匹配分数
            score = sum(1 for w in words if w in pattern_words)
            if score > best_score:
                best_score = score
                best_match = pattern_name

        # 如果没有好的匹配,使用前3个关键词
        if best_score < 2:
            best_match = f"{words[0]}/{words[1]}/{words[2]}"

        labels[topic_name] = best_match

    return labels

def plot_topic_distribution(lda_output, output_path):
    """绘制主题分布图"""
    # 计算每个主题在所有文档中的平均权重
    topic_weights = lda_output.mean(axis=0)

    fig, ax = plt.subplots(figsize=(12, 6))
    topics = [f"Topic {i}" for i in range(len(topic_weights))]

    bars = ax.bar(topics, topic_weights, color='steelblue', alpha=0.7)

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}',
                ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('Topics', fontsize=12)
    ax.set_ylabel('Average Topic Weight', fontsize=12)
    ax.set_title('Topic Distribution Across All Comments', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ 保存图表: {output_path}")

def plot_top_words(topics_words, output_path):
    """绘制每个主题的top关键词"""
    n_topics = len(topics_words)
    fig, axes = plt.subplots(n_topics, 1, figsize=(12, 3*n_topics))

    if n_topics == 1:
        axes = [axes]

    for idx, (topic_name, words) in enumerate(topics_words.items()):
        ax = axes[idx]
        y_pos = np.arange(len(words))

        ax.barh(y_pos, range(len(words), 0, -1), color='coral', alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(words)
        ax.invert_yaxis()
        ax.set_xlabel('Importance Rank', fontsize=10)
        ax.set_title(f'{topic_name} - Top Keywords', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ 保存图表: {output_path}")

def analyze_topics_by_category(df, lda_output, output_path):
    """分析AI vs 非AI内容的主题分布差异"""
    # 为每个文档分配主题权重
    df_with_topics = df.copy()
    for i in range(lda_output.shape[1]):
        df_with_topics[f'topic_{i}'] = lda_output[:, i]

    # 按video_type分组统计
    topic_cols = [col for col in df_with_topics.columns if col.startswith('topic_')]

    ai_topics = df_with_topics[df_with_topics['video_type'] == 'ai_generated'][topic_cols].mean()
    non_ai_topics = df_with_topics[df_with_topics['video_type'] == 'non_ai'][topic_cols].mean()

    # 绘制对比图
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(topic_cols))
    width = 0.35

    bars1 = ax.bar(x - width/2, ai_topics, width, label='AI Content', color='lightcoral', alpha=0.8)
    bars2 = ax.bar(x + width/2, non_ai_topics, width, label='Non-AI Content', color='lightblue', alpha=0.8)

    ax.set_xlabel('Topics', fontsize=12)
    ax.set_ylabel('Average Topic Weight', fontsize=12)
    ax.set_title('Topic Distribution: AI vs Non-AI Content', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'Topic {i}' for i in range(len(topic_cols))], rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ 保存图表: {output_path}")

    return ai_topics, non_ai_topics

def main():
    if len(sys.argv) < 2:
        print("用法: python topic_modeling_analysis.py <评论数据文件.json> [输出目录]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('output/topics')
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print(" YouTube Shorts Topic Modeling Analysis")
    print("="*80)
    print(f"加载数据: {input_file}")

    # 加载数据
    with open(input_file, 'r', encoding='utf-8') as f:
        comments = json.load(f)

    df = pd.DataFrame(comments)
    print(f"✅ 加载 {len(df)} 条评论\n")

    # 预处理文本
    print("1️⃣ 预处理评论文本...")
    df['text_clean'] = df['text'].apply(preprocess_text)

    # 移除空文本
    df_clean = df[df['text_clean'].str.len() > 10].copy()
    print(f"   ✓ 保留 {len(df_clean)} 条有效评论\n")

    # LDA主题建模
    print("2️⃣ 执行LDA主题建模...")
    n_topics = 5  # 提取5个主题
    n_top_words = 10

    # 使用CountVectorizer
    vectorizer = CountVectorizer(
        max_df=0.8,  # 忽略出现在80%以上文档中的词
        min_df=5,     # 至少出现在5个文档中
        max_features=1000,
        stop_words='english'
    )

    doc_term_matrix = vectorizer.fit_transform(df_clean['text_clean'])
    print(f"   ✓ 文档-词项矩阵: {doc_term_matrix.shape}")

    # LDA模型
    lda_model = LatentDirichletAllocation(
        n_components=n_topics,
        max_iter=50,
        learning_method='online',
        random_state=42,
        n_jobs=-1
    )

    lda_output = lda_model.fit_transform(doc_term_matrix)
    print(f"   ✓ LDA主题数: {n_topics}\n")

    # 提取主题关键词
    print("3️⃣ 提取主题关键词...")
    feature_names = vectorizer.get_feature_names_out()
    topics_words = get_top_words_per_topic(lda_model, feature_names, n_top_words)

    # 生成主题标签
    topic_labels = generate_topic_labels(topics_words)

    for topic_name, words in topics_words.items():
        label = topic_labels[topic_name]
        print(f"   {topic_name} ({label}):")
        print(f"      {', '.join(words[:5])}\n")

    # 可视化
    print("4️⃣ 生成可视化...")
    plot_topic_distribution(lda_output, output_dir / 'topic_distribution.png')
    plot_top_words(topics_words, output_dir / 'topic_keywords.png')

    # AI vs 非AI 主题对比
    if 'video_type' in df_clean.columns:
        print("\n5️⃣ 分析AI vs 非AI主题差异...")
        ai_topics, non_ai_topics = analyze_topics_by_category(
            df_clean, lda_output, output_dir / 'topic_comparison_ai_vs_nonai.png'
        )

    # 生成报告
    print("\n6️⃣ 生成主题分析报告...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""================================================================================
 Topic Modeling Analysis Report
================================================================================

生成时间: {timestamp}
分析评论数: {len(df_clean)}
提取主题数: {n_topics}

================================================================================
主题概览
================================================================================

"""

    for topic_name, words in topics_words.items():
        label = topic_labels[topic_name]
        report += f"{topic_name}: {label}\n"
        report += f"  关键词: {', '.join(words)}\n\n"

    report += """================================================================================
主题分布统计
================================================================================

"""

    topic_weights = lda_output.mean(axis=0)
    for i, weight in enumerate(topic_weights):
        label = topic_labels[f"Topic {i}"]
        report += f"Topic {i} ({label}): {weight:.3f} ({weight*100:.1f}%)\n"

    if 'video_type' in df_clean.columns:
        report += f"""
================================================================================
AI vs 非AI 主题对比
================================================================================

AI内容主题分布:
"""
        for i, weight in enumerate(ai_topics):
            label = topic_labels[f"Topic {i}"]
            report += f"  Topic {i} ({label}): {weight:.3f}\n"

        report += "\n非AI内容主题分布:\n"
        for i, weight in enumerate(non_ai_topics):
            label = topic_labels[f"Topic {i}"]
            report += f"  Topic {i} ({label}): {weight:.3f}\n"

    report += f"""
================================================================================
报告结束
================================================================================
"""

    # 保存报告
    report_file = output_dir / f'topic_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"   ✓ 保存报告: {report_file}")

    # 保存主题数据为JSON
    topic_data = {
        'topics': {
            topic_name: {
                'label': topic_labels[topic_name],
                'keywords': words,
                'weight': float(topic_weights[int(topic_name.split()[1])])
            }
            for topic_name, words in topics_words.items()
        },
        'metadata': {
            'n_topics': n_topics,
            'n_documents': len(df_clean),
            'timestamp': timestamp
        }
    }

    json_file = output_dir / 'topics.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(topic_data, f, indent=2, ensure_ascii=False)
    print(f"   ✓ 保存JSON: {json_file}")

    print("\n" + "="*80)
    print(" ✅ 主题建模分析完成!")
    print("="*80)
    print(f"\n📁 输出目录: {output_dir}")
    print(f"📊 图表: topic_distribution.png, topic_keywords.png")
    if 'video_type' in df_clean.columns:
        print(f"      topic_comparison_ai_vs_nonai.png")
    print(f"📄 报告: {report_file.name}")
    print(f"📋 数据: topics.json\n")

if __name__ == '__main__':
    main()
