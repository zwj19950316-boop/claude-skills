#!/usr/bin/env python3
"""
热点发现引擎 v2 — 从KOL内容聚类话题

核心逻辑改变：
- 不再用关键词搜索全网
- 改为抓取配置的YouTube频道内容
- 从KOL视频标题/内容中聚类热点话题
- 用Google搜索补充话题热度
"""

import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_manager import load_config, ensure_dirs, CONFIG_DIR

RAW_DATA_DIR = CONFIG_DIR / "raw_data"
TIMEOUT_SECONDS = 120

# 定义话题关键词映射（用于从视频标题中识别话题）
TOPIC_PATTERNS = {
    "Windows 11/10 更新问题": {
        "keywords": ["update", "kb5", "patch", "24h2", "23h2", "build", "version", "upgrade"],
        "exclude": ["nvidia", "amd", "gpu", "game"],
        "category": "windows"
    },
    "蓝屏/系统崩溃修复": {
        "keywords": ["blue screen", "bsod", "crash", "freeze", "stuck", "boot loop", "won't boot", "not booting"],
        "exclude": [],
        "category": "windows"
    },
    "C盘满/存储空间清理": {
        "keywords": ["c drive", "disk full", "storage full", "low disk", "free up space", "clean up", "clear space"],
        "exclude": [],
        "category": "storage"
    },
    "分区管理/扩容": {
        "keywords": ["partition", "resize", "extend", "shrink", "merge partition", "unallocated", "disk management"],
        "exclude": ["linux", "ubuntu"],
        "category": "storage"
    },
    "数据恢复": {
        "keywords": ["data recovery", "recover", "recover deleted", "file recovery", "formatted recovery", "recycle bin", "lost files"],
        "exclude": ["game", "minecraft"],
        "category": "data-recovery"
    },
    "硬盘/SSD相关": {
        "keywords": ["ssd", "hdd", "hard drive", "nvme", "sata", "disk speed", "clone disk", "migrate"],
        "exclude": ["ps5", "xbox", "console", "gaming"],
        "category": "storage"
    },
    "系统优化/加速": {
        "keywords": ["speed up", "optimize", "faster", "performance", "tweak", "registry"],
        "exclude": ["game", "fps", "gaming"],
        "category": "windows"
    },
    "病毒/恶意软件清除": {
        "keywords": ["malware", "virus", "ransomware", "trojan", "remove malware", "antivirus"],
        "exclude": [],
        "category": "windows"
    },
    "文件误删/备份": {
        "keywords": ["backup", "restore", "delete file", "accidentally deleted", "undelete", "file history"],
        "exclude": [],
        "category": "data-recovery"
    },
    "USB/外置设备问题": {
        "keywords": ["usb", "external drive", "flash drive", "sd card", "not recognized", "corrupted"],
        "exclude": [],
        "category": "storage"
    }
}


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
            print(f"    [警告] 命令失败: {err}")
            return None

        output = result.stdout.strip()
        if not output:
            return None

        try:
            import yaml
            return yaml.safe_load(output)
        except ImportError:
            return {"raw": output}
        except Exception:
            return {"raw": output}

    except subprocess.TimeoutExpired:
        print(f"    [警告] 命令超时 ({TIMEOUT_SECONDS}s)")
        return None
    except FileNotFoundError:
        print(f"    [错误] opencli 未找到")
        return None
    except Exception as e:
        print(f"    [错误] 执行异常: {e}")
        return None


def get_youtube_channel_videos(channel_handle, limit=10):
    """获取YouTube频道最新视频列表"""
    return run_opencli(
        ["youtube", "channel", channel_handle, "--limit", str(limit), "-f", "yaml"],
        f"频道: {channel_handle}"
    )


def parse_channel_videos(channel_handle, raw_data):
    """解析频道原始数据，提取视频列表"""
    videos = []
    if not isinstance(raw_data, dict):
        return videos

    channel_name = channel_handle
    subscribers = "Unknown"
    videos_started = False

    for key, value in raw_data.items():
        if key == "name":
            channel_name = value
        elif key == "subscribers":
            subscribers = value
        elif key == "--- Recent Videos ---":
            videos_started = True
        elif videos_started and isinstance(value, str) and "|" in value:
            parts = value.split("|")
            if len(parts) >= 3:
                videos.append({
                    "channel": channel_handle,
                    "channel_name": channel_name,
                    "subscribers": subscribers,
                    "title": key.strip(),
                    "duration": parts[0].strip() if len(parts) > 0 else "",
                    "views": parts[1].strip() if len(parts) > 1 else "",
                    "time": parts[2].strip() if len(parts) > 2 else "",
                    "url": parts[3].strip() if len(parts) > 3 else ""
                })

    return videos


def extract_number(text):
    """从文本中提取数字（如 '1.2K' -> 1200）"""
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


def parse_time_ago(time_str):
    """解析时间字符串为大致datetime"""
    if not time_str:
        return None
    time_str = str(time_str).lower().strip()
    now = datetime.now()

    match = re.match(r"(\d+)\s*(h|hour|hr|d|day|w|week|m|min|minute|mo|month)", time_str)
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
    return None


def classify_video_topic(title):
    """根据标题分类话题"""
    title_lower = title.lower()
    matched_topics = []

    for topic_name, topic_info in TOPIC_PATTERNS.items():
        keywords = topic_info.get("keywords", [])
        exclude = topic_info.get("exclude", [])

        # 检查排除词
        if any(ex in title_lower for ex in exclude):
            continue

        # 检查关键词
        if any(kw in title_lower for kw in keywords):
            matched_topics.append(topic_name)

    return matched_topics


def get_google_search_volume(keyword):
    """用Google搜索获取话题热度指标"""
    data = run_opencli(
        ["google", "search", keyword, "--limit", "10", "--lang", "en", "-f", "yaml"],
        f"Google热度: {keyword}"
    )
    if isinstance(data, dict) and "raw" in data:
        raw = data["raw"]
        result_count = raw.count("title:")
        return result_count
    elif isinstance(data, list):
        return len(data)
    return 0


def get_google_trends():
    """获取Google Trends热门搜索（科技/Windows相关）"""
    trends_data = {
        "us_tech": [],
        "us_daily": [],
        "related_to_windows": []
    }

    # 尝试获取美国地区每日趋势 RSS
    print("\n  [Trends] 获取 Google Trends US...")
    data = run_opencli(
        ["web", "read", "--url", "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US", "-f", "yaml"],
        "Google Trends US"
    )
    if data and isinstance(data, dict) and "raw" in data:
        raw = data["raw"]
        # 简单解析RSS中的title
        titles = re.findall(r'<title>(.+?)</title>', raw)
        trends_data["us_daily"] = [t for t in titles if t != "Daily Search Trends"][:20]

    # 尝试获取科技相关趋势
    print("  [Trends] 获取科技相关趋势...")
    tech_keywords = ["Windows 11", "Windows 10", "data recovery", "SSD", "backup software"]
    for kw in tech_keywords:
        data = run_opencli(
            ["google", "search", kw, "--limit", "5", "--lang", "en", "-f", "yaml"],
            f"Trends相关: {kw}"
        )
        if data:
            if isinstance(data, dict) and "raw" in data:
                raw = data["raw"]
                titles = re.findall(r'title:\s*(.+)', raw)
                trends_data["us_tech"].extend([{"keyword": kw, "titles": titles[:5]}])
            elif isinstance(data, list):
                titles = [item.get("title", "") for item in data if isinstance(item, dict)]
                trends_data["us_tech"].append({"keyword": kw, "titles": titles[:5]})
        time.sleep(1)

    return trends_data


def analyze_kol_content(config):
    """核心分析：抓取KOL内容并聚类话题"""
    all_videos = []
    kol_channels = config.get("competitors", {}).get("youtube", [])
    brand_channel = config.get("brand", {}).get("youtube", "")

    # 添加品牌官方频道
    if brand_channel:
        kol_channels = [brand_channel] + kol_channels

    print(f"\n=== 开始抓取 {len(kol_channels)} 个频道内容 ===")

    for i, channel in enumerate(kol_channels, 1):
        print(f"\n[{i}/{len(kol_channels)}] 抓取 {channel}...")
        raw_data = get_youtube_channel_videos(channel, limit=15)

        if raw_data:
            videos = parse_channel_videos(channel, raw_data)
            all_videos.extend(videos)
            print(f"  成功获取 {len(videos)} 个视频")
        else:
            print(f"  [跳过] 无法获取 {channel}")

        time.sleep(2)

    print(f"\n=== 共获取 {len(all_videos)} 个视频 ===")

    # 话题聚类
    topic_videos = defaultdict(list)
    uncategorized = []

    for video in all_videos:
        topics = classify_video_topic(video["title"])
        if topics:
            for topic in topics:
                topic_videos[topic].append(video)
        else:
            uncategorized.append(video)

    print(f"\n=== 话题聚类结果 ===")
    for topic, videos in sorted(topic_videos.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {topic}: {len(videos)} 个视频")

    # 补充Google搜索热度
    print(f"\n=== 补充Google搜索热度 ===")
    topic_google_data = {}
    for topic in list(topic_videos.keys())[:10]:
        count = get_google_search_volume(topic)
        topic_google_data[topic] = count
        print(f"  {topic}: Google约 {count} 条结果")
        time.sleep(1)

    # 获取Google Trends
    print(f"\n=== 获取Google Trends数据 ===")
    trends_data = get_google_trends()

    return {
        "timestamp": datetime.now().isoformat(),
        "total_videos": len(all_videos),
        "topic_clusters": {
            topic: {
                "videos": videos,
                "kol_count": len(set(v["channel"] for v in videos)),
                "total_views": sum(extract_number(v["views"]) for v in videos),
                "latest_time": min((parse_time_ago(v["time"]) for v in videos if parse_time_ago(v["time"])), default=None),
            }
            for topic, videos in topic_videos.items()
        },
        "uncategorized": uncategorized[:20],
        "google_search_counts": topic_google_data,
        "google_trends": trends_data,
        "kol_channels": kol_channels
    }


def save_data(data, suffix=""):
    ensure_dirs()
    RAW_DATA_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = RAW_DATA_DIR / f"kol_analysis_{timestamp}{suffix}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n[保存] 分析数据已保存: {filepath}")
    return filepath


def main():
    config = load_config()
    if not config:
        print("[错误] 配置文件不存在")
        sys.exit(1)

    results = analyze_kol_content(config)
    save_data(results, "_v2")


if __name__ == "__main__":
    main()
