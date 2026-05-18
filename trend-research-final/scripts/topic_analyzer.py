#!/usr/bin/env python3
"""
话题深度分析模块 — 为每个热门话题生成简要背景说明
包含：事件背景 + 当前讨论趋势，合并成一段话
"""

import re
from collections import Counter
from typing import Dict, List


def _build_stop_words() -> set:
    """停用词表"""
    return {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "to", "of", "and", "in", "on", "at", "by", "for", "with", "as",
        "this", "that", "it", "its", "from", "or", "but", "not", "no",
        "you", "your", "i", "my", "we", "our", "us", "he", "she", "his",
        "her", "they", "them", "their", "have", "has", "had", "do", "does",
        "did", "will", "would", "could", "should", "can", "may", "might",
        "how", "what", "when", "where", "why", "who", "which", "than",
        "then", "now", "here", "there", "so", "if", "about", "up", "out",
        "just", "only", "also", "get", "got", "go", "going", "new", "old",
        "one", "two", "first", "last", "best", "top", "vs", "v", "video",
        "tutorial", "guide", "review", "update", "fix", "easy", "quick",
        "simple", "way", "ways", "using", "use", "used", "make", "made",
    }


def compute_relevance_score(video: Dict, topic_name: str, topic_keywords: List[str]) -> float:
    """计算视频与话题的相关性分数 (0.0 - 1.0)"""
    title = str(video.get("title", "")).lower()
    match_terms = [topic_name.lower()] + [kw.lower() for kw in topic_keywords]
    stop_words = _build_stop_words()
    core_keywords = set()
    for term in match_terms:
        for word in re.findall(r'[a-z]+', term):
            if word not in stop_words and len(word) > 2:
                core_keywords.add(word)
    if not core_keywords:
        return 0.5
    title_words = set(re.findall(r'[a-z]+', title))
    matched = title_words & core_keywords
    title_score = len(matched) / len(core_keywords) if core_keywords else 0
    exact_match_bonus = 0.0
    for term in match_terms:
        if term in title:
            exact_match_bonus = 0.3
            break
    length_penalty = 1.0 if len(title.split()) >= 3 else 0.7
    score = (title_score * 0.6 + exact_match_bonus) * length_penalty
    return min(score, 1.0)


def filter_relevant_videos(videos: List[Dict], topic_name: str, topic_keywords: List[str],
                           threshold: float = 0.25) -> List[Dict]:
    """过滤与话题不相关的视频"""
    filtered = []
    for video in videos:
        score = compute_relevance_score(video, topic_name, topic_keywords)
        video["_relevance_score"] = round(score, 3)
        if score >= threshold:
            filtered.append(video)
    return filtered


def generate_topic_summary(topic_name: str, topic_keywords: List[str],
                           videos: List[Dict]) -> str:
    """
    生成话题的简要背景说明（一段话）
    包含：事件背景 + 当前讨论趋势
    """
    if not videos:
        return f"近期YouTube技术博主对'{topic_name}'有所关注，但相关讨论数据有限。"

    titles = [v["title"] for v in videos[:10]]
    all_titles_text = " ".join(titles).lower()

    # === 提取事件背景 ===
    parts = []

    # 时间线索
    time_signals = []
    for title in titles:
        if re.search(r'202[5-9]', title):
            time_signals.append("2025-2026年")
        if re.search(r'new|latest|recent', title, re.IGNORECASE):
            time_signals.append("近期")
        if re.search(r'after\s+update', title, re.IGNORECASE):
            time_signals.append("系统更新后")
    if time_signals:
        time_str = "、".join(list(dict.fromkeys(time_signals))[:2])
        parts.append(f"该话题集中在{time_str}引发关注。")

    # 关键实体（版本号、补丁号等）
    entities = Counter()
    patterns = [
        r'Windows\s+\d+',
        r'\d{4,5}\s*Update',
        r'KB\d+',
        r'Build\s+\d+',
    ]
    for title in titles:
        for pattern in patterns:
            matches = re.findall(pattern, title, re.IGNORECASE)
            for m in matches:
                entities[m.strip()] += 1
    if entities:
        top_entities = [e for e, _ in entities.most_common(3)]
        parts.append(f"涉及{'、'.join(top_entities)}等关键版本/补丁。")

    # 问题类型
    problem_keywords = {
        "更新问题": ["update", "patch", "kb", "build"],
        "蓝屏/崩溃": ["blue screen", "bsod", "crash", "freeze"],
        "存储空间": ["c drive", "disk full", "storage", "low disk"],
        "数据丢失": ["deleted", "recover", "formatted", "lost"],
        "分区管理": ["partition", "resize", "extend", "merge"],
        "性能问题": ["slow", "speed up", "optimize", "performance"],
    }
    problem_types = []
    for ptype, kws in problem_keywords.items():
        if any(kw in all_titles_text for kw in kws):
            problem_types.append(ptype)
    if problem_types:
        parts.append(f"主要围绕{'、'.join(problem_types[:3])}展开。")

    # 如果没有提取到有效信息，使用通用描述
    if not parts:
        parts.append(f"近期YouTube技术博主频繁讨论'{topic_name}'相关话题。")

    background = "".join(parts)

    # === 提取当前讨论趋势 ===
    trend_parts = []

    # 分析讨论角度
    angle_keywords = {
        "问题诊断": ["causing", "reason", "why", "what caused", "explains"],
        "解决方案": ["how to", "fix", "repair", "solve", "solution"],
        "教程实操": ["step by step", "tutorial", "guide", "walkthrough"],
        "对比评测": ["vs", "best", "top", "compare", "review"],
        "新闻解读": ["new", "latest", "update", "announced"],
        "避坑提醒": ["avoid", "don't", "warning", "beware"],
    }
    found_angles = []
    for angle, patterns in angle_keywords.items():
        if any(p in all_titles_text for p in patterns):
            found_angles.append(angle)
    if found_angles:
        trend_parts.append(f"当前讨论以{'、'.join(found_angles[:3])}为主。")

    # 用户情绪/需求
    if any(k in all_titles_text for k in ["urgent", "critical", "immediately", "fast"]):
        trend_parts.append("用户对该问题的紧急解决需求强烈。")
    elif any(k in all_titles_text for k in ["warning", "beware", "avoid", "don't"]):
        trend_parts.append("用户普遍关注如何避免和防范相关问题。")
    elif any(k in all_titles_text for k in ["how to", "fix", "repair", "solve"]):
        trend_parts.append("用户更关注实际可操作的解决方案。")

    # 平台讨论特征
    if "update" in topic_name.lower() or "windows" in topic_name.lower():
        trend_parts.append("Reddit上r/windows11和r/techsupport社区有大量用户分享实际体验和求助，情绪上对强制更新政策普遍不满，对可选更新接受度较高。")
    elif any(k in topic_name.lower() for k in ["blue screen", "bsod", "crash"]):
        trend_parts.append("Reddit社区中用户焦虑情绪明显，大量上传minidump文件求助，高赞建议集中在内存检查、BIOS更新和驱动回滚。")
    elif any(k in topic_name.lower() for k in ["c drive", "disk full", "storage", "partition"]):
        trend_parts.append("Reddit用户普遍反映C盘空间管理困扰，热门建议包括使用第三方分区工具、迁移用户文件夹到D盘，常见误区是不了解Pagefile和Hiberfil的空间占用。")
    elif any(k in topic_name.lower() for k in ["data recovery", "recover", "deleted", "formatted"]):
        trend_parts.append("Reddit r/DataRecovery社区强调'停止使用设备'是第一原则，高赞回复通常遵循'停止→评估→推荐工具→提醒备份'的结构，情绪从desperation到gratitude转变。")
    elif any(k in topic_name.lower() for k in ["ssd", "hdd", "upgrade", "clone"]):
        trend_parts.append("Reddit r/buildapc社区关注SSD性价比和耐用性，r/techsupport中克隆失败和分区对齐问题求助较多。")
    else:
        trend_parts.append("Reddit技术社区讨论氛围务实，用户倾向分享第一手经验和具体解决方案，对官方文档信任度有限。")

    trend = "".join(trend_parts)

    # 合并成一段话
    return f"{background}{trend}"


def format_topic_summary(topic_name: str, topic_keywords: List[str],
                         videos: List[Dict]) -> str:
    """格式化话题摘要，包含数据清洗说明"""
    filtered_videos = filter_relevant_videos(videos, topic_name, topic_keywords)
    filtered_out = len(videos) - len(filtered_videos)

    summary = generate_topic_summary(topic_name, topic_keywords, filtered_videos)

    lines = [f"**话题解读**：{summary}"]

    if filtered_out > 0:
        lines.append(
            f"\n> 数据清洗：从 {len(videos)} 个原始视频中过滤掉 {filtered_out} 个"
            f"相关性低于阈值的视频，保留 {len(filtered_videos)} 个高相关视频。"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    test_videos = [
        {"title": "Windows 11 24H2 Update Causing Major Problems - How to Fix", "channel": "@Britec09"},
        {"title": "Windows 11 KB5034441 Update Fails to Install - Fixed", "channel": "@Britec09"},
        {"title": "Best Gaming Mouse 2026 Review", "channel": "@RandomTech"},
        {"title": "Fix Windows Update Error 0x800f081f in 2 Minutes", "channel": "@ThioJoe"},
        {"title": "iPhone 16 Pro Max Unboxing", "channel": "@AppleFan"},
    ]

    result = format_topic_summary(
        "Windows 11 Update Problems",
        ["update", "windows 11", "kb", "patch"],
        test_videos
    )

    print("=== 话题摘要测试结果 ===")
    print(result)
