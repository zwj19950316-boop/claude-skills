#!/usr/bin/env python3
"""
Dynamic Topic Extractor — Extract trending topics from YouTube video titles.

Approach: TF-IDF + KMeans clustering with keyword extraction.
- Lightweight: only requires scikit-learn (no GPU, no large models).
- Fast: < 30 seconds for ~100 titles.
- Works well on short text (10-20 words) by using character n-grams + word n-grams.
"""

import re
from collections import Counter, defaultdict
from typing import List, Dict

# Optional dependency: scikit-learn. Provide a clear error if missing.
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "scikit-learn is required. Install it with: pip install scikit-learn"
    ) from exc


def _preprocess(title: str) -> str:
    """Lowercase, strip, and normalize whitespace."""
    title = title.lower().strip()
    title = re.sub(r"\s+", " ", title)
    return title


def _build_stop_words() -> set:
    """Build a small domain-aware stop-word set for tech video titles."""
    generic = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "to", "of", "and", "in", "on", "at", "by", "for", "with", "as",
        "this", "that", "these", "those", "it", "its", "from", "or", "but",
        "not", "no", "yes", "you", "your", "i", "my", "we", "our", "us",
        "he", "she", "his", "her", "they", "them", "their", "have", "has",
        "had", "do", "does", "did", "will", "would", "could", "should",
        "can", "may", "might", "must", "shall", "how", "what", "when",
        "where", "why", "who", "which", "than", "then", "now", "here",
        "there", "so", "if", "about", "up", "out", "just", "only", "also",
        "get", "got", "go", "going", "went", "new", "old", "one", "two",
        "first", "last", "best", "top", "vs", "v", "episode", "video",
        "tutorial", "guide", "review", "update", "fix", "easy", "quick",
        "simple", "way", "ways", "using", "use", "used", "make", "made",
        # 动词 / 助动词 / 副词（避免进入话题名）
        "eventually", "showing", "explains", "reminds", "enters", "done",
        "making", "taking", "coming", "going", "being", "having",
        "really", "actually", "probably", "definitely", "maybe",
        "still", "already", "yet", "even", "ever", "never",
        "quite", "rather", "pretty", "fairly", "somewhat",
        "another", "every", "each", "much", "many", "more", "most",
        "some", "any", "all", "both", "either", "neither",
        "without", "within", "into", "onto", "upon", "over",
        "under", "between", "among", "during", "before", "after",
        "since", "until", "while", "although", "because", "though",
    }
    return generic


def _extract_top_terms_per_cluster(
    tfidf_matrix,
    vectorizer: TfidfVectorizer,
    labels: List[int],
    num_terms: int = 8,
) -> Dict[int, List[str]]:
    """Return the highest-TF-IDF terms for each cluster."""
    feature_names = vectorizer.get_feature_names_out()
    cluster_terms: Dict[int, List[str]] = {}

    # Group row indices by cluster label
    clusters = defaultdict(list)
    for idx, label in enumerate(labels):
        clusters[label].append(idx)

    for label, indices in clusters.items():
        # Sum TF-IDF scores across all documents in the cluster
        cluster_tfidf = tfidf_matrix[indices].sum(axis=0)
        if hasattr(cluster_tfidf, "A1"):
            scores = cluster_tfidf.A1
        else:
            scores = cluster_tfidf.flatten()

        # Get top terms
        top_indices = scores.argsort()[::-1][:num_terms]
        terms = [feature_names[i] for i in top_indices if scores[i] > 0]
        cluster_terms[label] = terms

    return cluster_terms


def _generate_topic_name(keywords: List[str], titles: List[str]) -> str:
    """基于聚类内视频标题生成可读的话题名称"""
    if not titles:
        return "Untitled Topic"

    # 从标题中提取 bigram，统计聚类内频率
    stop_words = _build_stop_words()
    bigram_counter = Counter()
    for title in titles:
        words = [_preprocess(t) for t in title.split()]
        words = [w for w in words if w not in stop_words and len(w) > 2]
        for i in range(len(words) - 1):
            bigram_counter[f"{words[i]} {words[i+1]}"] += 1

    # 取频率最高的 bigram（至少出现 2 次）
    if bigram_counter:
        top_bigram, count = bigram_counter.most_common(1)[0]
        if count >= 2:
            return top_bigram.title()

    # 回退：从 keywords 里挑一个多词关键词
    multi_word = [kw for kw in keywords if " " in kw]
    if multi_word:
        return multi_word[0].title()

    # 最终回退：用第一个有意义的关键词
    for kw in keywords:
        if kw.lower() not in stop_words:
            return kw.title()
    return "Misc Topic"


def _sum_views(videos: List[Dict]) -> int:
    """从 views 字符串中提取数字并求和"""
    total = 0
    for v in videos:
        views = str(v.get("views", "0")).replace(",", "").strip()
        match = re.match(r"([\d.]+)\s*([KMB]?)", views, re.IGNORECASE)
        if match:
            num = float(match.group(1))
            suffix = match.group(2).upper()
            multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
            total += int(num * multipliers.get(suffix, 1))
        else:
            nums = re.findall(r"\d+", views)
            if nums:
                total += int(nums[0])
    return total


def extract_topics(videos: List[Dict], num_topics: int = 8) -> List[Dict]:
    """
    从视频列表中动态提取话题聚类

    Args:
        videos: 视频 dict 列表，每个 dict 必须包含 "title" 和 "channel"
        num_topics: 期望的话题数量上限

    Returns:
        List[dict]，每个话题包含:
            - name: 话题名称
            - keywords: 代表性关键词列表
            - videos: 属于该话题的视频 dict 列表
            - video_count: 视频数量
            - kol_count: 涉及的 KOL 频道数
            - total_views: 总观看量
    """
    if not videos:
        return []

    video_titles = [v["title"] for v in videos]

    # Deduplicate while preserving order
    seen = set()
    unique_titles = []
    unique_indices = []
    for i, t in enumerate(video_titles):
        normalized = t.lower().strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_titles.append(t)
            unique_indices.append(i)

    n_clusters = min(num_topics, len(unique_titles))
    if n_clusters < 1:
        return []

    processed = [_preprocess(t) for t in unique_titles]
    stop_words = _build_stop_words()

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words=list(stop_words),
        ngram_range=(1, 2),
        max_df=0.85,
        min_df=1,
        max_features=500,
    )

    tfidf_matrix = vectorizer.fit_transform(processed)
    if tfidf_matrix.shape[1] == 0:
        return []

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10,
        max_iter=300,
    )
    labels = kmeans.fit_predict(tfidf_matrix)

    cluster_keywords = _extract_top_terms_per_cluster(
        tfidf_matrix, vectorizer, labels, num_terms=8
    )

    # Group original video dicts by cluster
    cluster_videos = defaultdict(list)
    for idx, label in zip(unique_indices, labels):
        cluster_videos[label].append(videos[idx])

    results = []
    for label in sorted(cluster_videos.keys()):
        topic_videos = cluster_videos[label]
        # 跳过纯噪音聚类（少于2个视频且无高观看量）
        if len(topic_videos) < 2 and _sum_views(topic_videos) < 50000:
            continue
        keywords = cluster_keywords.get(label, [])
        cluster_titles = [v["title"] for v in topic_videos]
        name = _generate_topic_name(keywords, cluster_titles)
        results.append({
            "name": name,
            "keywords": keywords,
            "videos": topic_videos,
            "video_count": len(topic_videos),
            "kol_count": len(set(v["channel"] for v in topic_videos)),
            "total_views": _sum_views(topic_videos),
        })

    results.sort(key=lambda x: (x["kol_count"], x["video_count"]), reverse=True)
    return results


def test_extract():
    """Run a quick self-test with sample tech video titles."""
    sample_titles = [
        # Windows update
        "Windows 11 24H2 Update Causing Major Problems - How to Fix",
        "Windows 11 KB5034441 Update Fails to Install - Fixed",
        "New Windows 11 Build 26120 Issues and Workarounds",
        "Windows 10 Update Stuck at 99% - Here is the Solution",
        "Windows 11 23H2 vs 24H2 - Should You Upgrade Now",
        "Fix Windows Update Error 0x800f081f in 2 Minutes",
        # BSOD / crash
        "Windows 11 Blue Screen of Death Fix 2026",
        "How to Fix BSOD CRITICAL PROCESS DIED Error",
        "Windows Keeps Crashing After Update - Fixed",
        "Fix Windows 11 Boot Loop and Startup Problems",
        "PC Freezes Randomly - 5 Fixes That Actually Work",
        # Storage / C drive
        "C Drive Full on Windows 11 - Free Up Space Fast",
        "How to Clean Up Disk Space on Windows 10/11",
        "Windows 11 Storage Sense Deep Clean Guide",
        "Low Disk Space Warning - Fix It Without Deleting Files",
        "Free Up 20GB on Your C Drive Right Now",
        # Partition
        "How to Extend C Drive Without Losing Data",
        "Resize Partition on Windows 11 - Full Tutorial",
        "Merge Partitions in Windows 11 Step by Step",
        "Unallocated Space to C Drive - Easy Method",
        # Data recovery
        "How to Recover Deleted Files on Windows 11 Free",
        "Best Free Data Recovery Software 2026 - Full Test",
        "Recover Files from Formatted Hard Drive",
        "Recycle Bin Recovery - Restore Deleted Files Easily",
        "SD Card Recovery - Get Your Photos Back",
        # SSD / upgrade
        "Clone HDD to SSD on Windows 11 - Complete Guide",
        "SSD Upgrade Guide 2026 - Which One to Buy",
        "Migrate Windows 11 to New NVMe SSD",
        "HDD vs SSD Speed Test - Real World Difference",
        # Performance
        "Speed Up Windows 11 in 2026 - 10 Easy Tips",
        "Windows 11 Slow Performance Fix After Update",
        "How to Optimize Windows 11 for Gaming and Work",
        "Fix Slow PC Boot Time in Under 5 Minutes",
        # Malware
        "Remove Malware from Windows 11 Completely",
        "Best Free Virus Removal Tools for Windows 2026",
        "How to Detect and Remove Ransomware",
        # Backup
        "Windows 11 Backup and Restore Full Tutorial",
        "Create a System Image Backup on Windows 11",
        "Best Free Backup Software for Windows 2026",
        # USB / external drive
        "USB Drive Not Recognized in Windows 11 - Fixed",
        "Fix Corrupted External Hard Drive Without Formatting",
        "External SSD Not Showing Up - 4 Quick Fixes",
    ]

    print(f"Testing extract_topics with {len(sample_titles)} sample titles...\n")
    topics = extract_topics(sample_titles, num_topics=8)

    print(f"Discovered {len(topics)} topics:\n")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic['name']}")
        print(f"   Keywords: {', '.join(topic['keywords'])}")
        print(f"   Videos ({len(topic['videos'])}):")
        for v in topic["videos"]:
            print(f"      - {v}")
        print()

    return topics


if __name__ == "__main__":
    test_extract()
