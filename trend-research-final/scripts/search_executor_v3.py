#!/usr/bin/env python3
"""
热点发现引擎 v3 — 修复解析问题 + 1个月时间过滤 + Reddit社群
"""

import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_manager import load_config, ensure_dirs, CONFIG_DIR
from topic_extractor import extract_topics

RAW_DATA_DIR = CONFIG_DIR / "raw_data"
TIMEOUT_SECONDS = 120
MAX_AGE_DAYS = 7  # 只取最近7天的视频

# 话题定义：英文搜索关键词 + 分类
topics = {
    "Windows 11 update problems": {
        "patterns": ["update", "kb5", "patch", "24h2", "23h2", "upgrade", "build 26"],
        "exclude": ["nvidia", "amd driver", "gpu update"],
        "category": "windows",
        "search_keywords": ["Windows 11 update problems", "Windows 11 KB update issues", "Windows 11 24H2 problems"]
    },
    "Blue screen crash fix": {
        "patterns": ["blue screen", "bsod", "crash", "freeze", "stuck", "boot loop", "won't boot"],
        "exclude": [],
        "category": "windows",
        "search_keywords": ["Windows 11 blue screen fix", "BSOD crash fix 2026", "Windows boot loop repair"]
    },
    "C drive full cleanup": {
        "patterns": ["c drive", "disk full", "storage full", "low disk", "free up space", "clean up"],
        "exclude": [],
        "category": "storage",
        "search_keywords": ["C drive full Windows 11", "free up disk space", "Windows storage cleanup"]
    },
    "Partition resize extend": {
        "patterns": ["partition", "resize", "extend", "shrink", "merge partition", "unallocated"],
        "exclude": ["linux", "ubuntu"],
        "category": "storage",
        "search_keywords": ["extend C drive Windows", "resize partition without losing data", "partition manager Windows 11"]
    },
    "Data recovery deleted files": {
        "patterns": ["data recovery", "recover deleted", "file recovery", "formatted recovery", "recycle bin", "lost files"],
        "exclude": ["game save", "minecraft"],
        "category": "data-recovery",
        "search_keywords": ["recover deleted files free", "hard drive data recovery", "formatted drive recovery"]
    },
    "SSD HDD upgrade clone": {
        "patterns": ["ssd upgrade", "hdd to ssd", "clone disk", "migrate os", "nvme upgrade", "disk speed"],
        "exclude": ["ps5", "xbox"],
        "category": "storage",
        "search_keywords": ["SSD upgrade Windows 11", "clone HDD to SSD", "migrate Windows to new drive"]
    },
    "Windows speed up optimize": {
        "patterns": ["speed up", "optimize", "faster", "performance", "slow pc", "registry clean"],
        "exclude": ["game fps", "gaming performance"],
        "category": "windows",
        "search_keywords": ["speed up Windows 11", "Windows 11 performance fix", "optimize slow PC"]
    },
    "Malware virus removal": {
        "patterns": ["malware", "virus remove", "ransomware", "trojan", "remove malware"],
        "exclude": [],
        "category": "windows",
        "search_keywords": ["remove malware Windows 11", "ransomware recovery", "virus removal tool"]
    },
    "Backup restore files": {
        "patterns": ["backup", "restore", "undelete", "file history", "system image"],
        "exclude": [],
        "category": "data-recovery",
        "search_keywords": ["Windows 11 backup", "system image backup", "restore deleted files"]
    },
    "USB external drive fix": {
        "patterns": ["usb not working", "external drive", "flash drive", "sd card", "not recognized", "corrupted"],
        "exclude": [],
        "category": "storage",
        "search_keywords": ["USB drive not recognized", "external hard drive corrupted", "SD card recovery"]
    }
}

DEFAULT_REDDIT_COMMUNITIES = [
    "windows11", "computers", "MacOS", "mac", "apple",
    "techsupport", "DataRecovery", "technology"
]


def get_opencli_path():
    possible_paths = [
        Path.home() / "AppData" / "Roaming" / "npm" / "opencli.cmd",
        Path.home() / "AppData" / "Roaming" / "npm" / "opencli",
        Path("/c/Users/admin/AppData/Roaming/npm/opencli.cmd"),
        Path("/c/Users/admin/AppData/Roaming/npm/opencli"),
    ]
    for p in possible_paths:
        if p.exists():
            return str(p)
    return "opencli"


def run_opencli(cmd_args, description=""):
    opencli_path = get_opencli_path()
    full_cmd = [opencli_path] + cmd_args
    if description:
        print(f"  [搜索] {description}")

    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            encoding="utf-8",
            errors="replace"
        )
        if result.returncode != 0:
            err = result.stderr.strip()[:200]
            print(f"    [警告] {err}")
            return None
        output = result.stdout.strip()
        if not output:
            return None
        try:
            import yaml
            return yaml.safe_load(output)
        except Exception:
            return {"raw": output}
    except Exception as e:
        print(f"    [错误] {e}")
        return None


def parse_time_ago(time_str):
    if not time_str:
        return None
    time_str = str(time_str).lower().strip()
    now = datetime.now()
    match = re.match(r"(\d+)\s*(hour|hr|h|day|d|week|w|month|mo|min|minute|m|year|y)", time_str)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if unit in ("h", "hour", "hr"):
            return now - timedelta(hours=num)
        elif unit in ("d", "day"):
            return now - timedelta(days=num)
        elif unit in ("w", "week"):
            return now - timedelta(weeks=num)
        elif unit in ("m", "min", "minute"):
            return now - timedelta(minutes=num)
        elif unit in ("mo", "month"):
            return now - timedelta(days=num * 30)
        elif unit in ("y", "year"):
            return now - timedelta(days=num * 365)
    return None


def parse_channel_videos(channel_handle, raw_data):
    videos = []
    if not raw_data:
        return videos

    # Handle list format from yaml.safe_load
    items = raw_data if isinstance(raw_data, list) else []

    channel_name = channel_handle
    subscribers = "Unknown"
    videos_started = False

    for item in items:
        if not isinstance(item, dict):
            continue
        field = item.get("field", "")
        value = item.get("value", "")

        if field == "name":
            channel_name = value
        elif field == "subscribers":
            subscribers = value
        elif field == "---":
            videos_started = True
        elif videos_started and isinstance(value, str) and "|" in value:
            parts = value.split("|")
            if len(parts) >= 3:
                # Parse time and filter by age
                time_str = parts[2].strip() if len(parts) > 2 else ""
                video_time = parse_time_ago(time_str)
                if video_time and (datetime.now() - video_time).days <= MAX_AGE_DAYS:
                    videos.append({
                        "channel": channel_handle,
                        "channel_name": channel_name,
                        "subscribers": subscribers,
                        "title": str(field).strip(),
                        "duration": parts[0].strip() if len(parts) > 0 else "",
                        "views": parts[1].strip() if len(parts) > 1 else "",
                        "time": time_str,
                        "url": parts[3].strip() if len(parts) > 3 else ""
                    })

    return videos


def extract_number(text):
    if not text:
        return 0
    text = str(text).replace(",", "").strip()
    match = re.match(r"([\d.]+)\s*([KMB]?)", text, re.IGNORECASE)
    if match:
        num = float(match.group(1))
        suffix = match.group(2).upper()
        multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
        return int(num * multipliers.get(suffix, 1))
    nums = re.findall(r"\d+", text)
    if nums:
        return int(nums[0])
    return 0


def generate_search_keywords(topic_name, topic_keywords):
    """基于话题名称和关键词生成 Google 搜索关键词"""
    # 取话题名本身 + 前 2 个关键词组合
    keywords = [topic_name.lower()]
    for kw in topic_keywords[:2]:
        keywords.append(f"{kw} 2026")
    return keywords[:3]


def get_youtube_channel_videos(channel_handle, limit=15):
    return run_opencli(
        ["youtube", "channel", channel_handle, "--limit", str(limit), "-f", "yaml"],
        f"频道: {channel_handle}"
    )


def discover_kol_channels(query, limit=5):
    """基于话题关键词智能搜索补充KOL频道"""
    data = run_opencli(
        ["youtube", "search", query, "--limit", str(limit * 2), "-f", "yaml"],
        f"发现KOL: {query}"
    )
    channels = []
    if not data or not isinstance(data, list):
        return channels

    for item in data:
        if not isinstance(item, dict):
            continue
        field = item.get("field", "")
        value = item.get("value", "")
        if field == "channel" and value and value.startswith("@"):
            channels.append(value)
        elif field == "url" and "youtube.com/@" in str(value):
            handle = str(value).split("youtube.com/@")[-1].split("/")[0]
            if handle:
                channels.append(f"@{handle}")

    # 去重并限制数量
    seen = set()
    unique = []
    for ch in channels:
        ch_lower = ch.lower()
        if ch_lower not in seen:
            seen.add(ch_lower)
            unique.append(ch)
    return unique[:limit]


def search_reddit(subreddit, limit=10):
    return run_opencli(
        ["reddit", "search", f"subreddit:{subreddit}", "--limit", str(limit), "-f", "yaml"],
        f"Reddit: r/{subreddit}"
    )


def get_google_trends_data():
    """获取Google搜索热度（返回搜索结果数量作为热度代理指标）
    注意：opencli google search 返回的是搜索结果列表，不是Google Trends趋势曲线"""
    trends = {}
    keywords = ["Windows 11 update", "data recovery", "partition manager", "C drive full", "SSD upgrade"]
    for kw in keywords:
        data = run_opencli(
            ["google", "search", kw, "--limit", "10", "--lang", "en", "-f", "yaml"],
            f"Google: {kw}"
        )
        if data:
            if isinstance(data, list):
                # 计算实际返回的搜索结果条目数
                trends[kw] = len(data)
            elif isinstance(data, dict):
                trends[kw] = len(data)
            else:
                trends[kw] = 0
        else:
            trends[kw] = 0
        time.sleep(1)
    return trends


def analyze_content(config):
    # 1. 基础频道列表
    base_channels = config.get("competitors", {}).get("youtube", [])
    brand = config.get("brand", {}).get("youtube", "")
    kol_channels = list(dict.fromkeys([brand] + base_channels)) if brand else list(base_channels)

    # 2. 智能发现新KOL频道
    print("\n=== 智能发现新KOL频道 ===")
    discovery_queries = [
        "Windows 11 update fix tutorial",
        "data recovery software review 2026",
        "partition manager Windows tutorial"
    ]
    discovered = []
    for q in discovery_queries:
        new_chs = discover_kol_channels(q, limit=5)
        for ch in new_chs:
            if ch.lower() not in {c.lower() for c in kol_channels}:
                discovered.append(ch)
        time.sleep(2)

    # 去重并限制补充数量
    seen = set(c.lower() for c in kol_channels)
    extra = []
    for ch in discovered:
        if ch.lower() not in seen:
            seen.add(ch.lower())
            extra.append(ch)
    extra = extra[:5]

    if extra:
        print(f"  发现新频道: {extra}")
        kol_channels.extend(extra)
    else:
        print("  未发现新频道（或已达上限）")

    # 3. 抓取所有频道
    all_videos = []
    print(f"\n=== 抓取 {len(kol_channels)} 个频道（最近{MAX_AGE_DAYS}天）===")

    for i, ch in enumerate(kol_channels, 1):
        print(f"\n[{i}/{len(kol_channels)}] {ch}...")
        raw = get_youtube_channel_videos(ch, limit=20)
        if raw:
            videos = parse_channel_videos(ch, raw)
            all_videos.extend(videos)
            print(f"  成功: {len(videos)} 个视频（最近{MAX_AGE_DAYS}天）")
        else:
            print(f"  [跳过] 无法获取")
        time.sleep(2)

    print(f"\n=== 共获取 {len(all_videos)} 个视频 ===")

    # 4. 动态话题聚类
    dynamic_topics = extract_topics(all_videos, num_topics=8)

    print(f"\n=== 动态话题聚类 ===")
    for t in dynamic_topics:
        print(f"  {t['name']}: {t['video_count']} 个视频")

    # 5. Reddit数据（从配置读取）
    reddit_communities = config.get("reddit", {}).get("communities", DEFAULT_REDDIT_COMMUNITIES)
    print(f"\n=== Reddit社群搜索 ===")
    reddit_data = {}
    for sub in reddit_communities[:5]:
        data = search_reddit(sub, limit=10)
        reddit_data[sub] = data
        time.sleep(2)

    # 6. Google热度
    print(f"\n=== Google搜索热度 ===")
    google_trends = get_google_trends_data()

    # 构建动态话题数据结构
    topic_clusters = {}
    for t in dynamic_topics:
        topic_clusters[t["name"]] = {
            "videos": t["videos"],
            "kol_count": t["kol_count"],
            "total_views": t["total_views"],
            "search_keywords": generate_search_keywords(t["name"], t["keywords"])
        }

    # 将关键词搜索计数汇总到动态话题维度
    google_search_counts = {}
    for t in dynamic_topics:
        topic_name = t["name"]
        search_kws = generate_search_keywords(topic_name, t["keywords"])
        total = sum(google_trends.get(kw, 0) for kw in search_kws)
        google_search_counts[topic_name] = total

    return {
        "timestamp": datetime.now().isoformat(),
        "total_videos": len(all_videos),
        "topic_clusters": topic_clusters,
        "google_trends": google_trends,
        "google_search_counts": google_search_counts,
        "reddit_data": reddit_data,
        "kol_channels": kol_channels,
        "discovered_channels": extra
    }


def save_data(data, suffix=""):
    ensure_dirs()
    RAW_DATA_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = RAW_DATA_DIR / f"kol_analysis_{timestamp}{suffix}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n[保存] {filepath}")
    return filepath


def main():
    config = load_config()
    if not config:
        print("[错误] 配置不存在")
        sys.exit(1)
    results = analyze_content(config)
    save_data(results, "_v3")


if __name__ == "__main__":
    main()
