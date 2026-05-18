#!/usr/bin/env python3
"""
生成近一周热点趋势报告
基于 firecrawl 搜索结果
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from topic_analyzer import generate_topic_summary


def load_firecrawl_results(filepath):
    """加载 firecrawl 搜索结果"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("data", {}).get("web", [])


def analyze_topic_from_results(topic_name, results, category):
    """从搜索结果分析话题"""
    videos = []
    articles = []

    for item in results:
        title = item.get("title", "")
        url = item.get("url", "")
        desc = item.get("description", "")

        if "youtube.com" in url or "youtu.be" in url:
            videos.append({
                "title": title,
                "url": url,
                "channel": "YouTube",
                "views": "N/A",
                "time": "近期"
            })
        else:
            articles.append({
                "title": title,
                "url": url,
                "description": desc,
                "source": url.split("/")[2] if "/" in url else "Unknown"
            })

    # 生成话题摘要
    summary = generate_topic_summary(topic_name, [], videos + articles)

    return {
        "name": topic_name,
        "category": category,
        "video_count": len(videos),
        "article_count": len(articles),
        "sources": list(set(a["source"] for a in articles))[:5],
        "summary": summary,
        "videos": videos[:3],
        "articles": articles[:3]
    }


def classify_priority(topic):
    """分类优先级"""
    name = topic["name"].lower()

    # P0: 强产品关联 + 高热度
    strong_keywords = ["data recovery", "partition", "disk full", "c drive", "backup", "clone", "migrate"]
    if any(kw in name for kw in strong_keywords) and topic["article_count"] >= 5:
        return "P0"

    # P1: 中等关联
    medium_keywords = ["blue screen", "bsod", "crash", "boot", "repair", "update", "system", "usb", "external drive", "storage", "ssd"]
    if any(kw in name for kw in medium_keywords) and topic["article_count"] >= 3:
        return "P1"

    return "P2"


def generate_report(topics):
    """生成 Markdown 报告"""
    report_date = datetime.now().strftime("%Y年%m月%d日")

    report = f"""# EaseUS 热点话题调研报告 — 近一周趋势

> **报告日期**: {report_date}
> **监测范围**: Windows系统 / 数据恢复 / 存储设备
> **数据来源**: Firecrawl 网页搜索（Google/Reddit/新闻）
> **品牌**: EaseUS

---

## 执行摘要

- **热点话题总数**: {len(topics)} 个
- **P0级选题（立即跟进）**: {sum(1 for t in topics if classify_priority(t) == 'P0')} 个
- **P1级选题（本周跟进）**: {sum(1 for t in topics if classify_priority(t) == 'P1')} 个
- **P2级选题（储备观察）**: {sum(1 for t in topics if classify_priority(t) == 'P2')} 个

---

## 一、热点话题排行

"""

    # 按优先级排序
    sorted_topics = sorted(topics, key=lambda x: classify_priority(x))

    for i, topic in enumerate(sorted_topics, 1):
        priority = classify_priority(topic)
        priority_label = {"P0": "🔴 P0-立即跟进", "P1": "🟡 P1-本周跟进", "P2": "🟢 P2-储备观察"}.get(priority, "🟢 P2")

        report += f"""### TOP {i}: {topic['name']}

| 维度 | 数据 |
|-----|------|
| **优先级** | {priority_label} |
| **所属领域** | {topic['category']} |
| **相关文章** | {topic['article_count']} 篇 |
| **相关视频** | {topic['video_count']} 个 |
| **主要来源** | {', '.join(topic['sources'])} |

**话题解读**：{topic['summary']}

**参考链接**：
"""

        for v in topic['videos']:
            report += f"- [视频] {v['title']}]({v['url']})\n"
        for a in topic['articles']:
            report += f"- [文章] {a['title']}]({a['url']})\n"

        report += "\n---\n\n"

    # 建议选题角度
    report += """## 二、建议选题角度

"""

    p0_topics = [t for t in topics if classify_priority(t) == "P0"]
    p1_topics = [t for t in topics if classify_priority(t) == "P1"]

    report += "### 🔴 P0 — 立即跟进（48小时内）\n\n"
    if p0_topics:
        for t in p0_topics[:3]:
            report += f"1. **{t['name']}**\n"
            report += f"   - EaseUS产品结合点：{get_product_recommendation(t['name'])}\n"
            report += f"   - 内容形式：教程 / 测评 / 短平快tips\n"
            report += f"   - 目标平台：YouTube + TikTok同步\n\n"
    else:
        report += "暂无P0级选题\n\n"

    report += "### 🟡 P1 — 本周跟进\n\n"
    if p1_topics:
        for t in p1_topics[:3]:
            report += f"1. **{t['name']}**\n"
            report += f"   - EaseUS产品结合点：{get_product_recommendation(t['name'])}\n"
            report += f"   - 内容形式：教程 / 新闻解读\n\n"
    else:
        report += "暂无P1级选题\n\n"

    # 数据附录
    report += f"""---

## 三、数据附录

### 本次搜索关键词
- Windows 11 update problems May 2026
- data recovery software 2026
- C drive full Windows 11
- Windows 11 blue screen BSOD May 2026
- SSD upgrade clone Windows 2026

### 数据来源时间戳
- 报告生成时间: {datetime.now().isoformat()}

---

*本报告由 EaseUS TrendBot 自动生成，基于 Firecrawl 网页搜索数据。*
"""

    return report


def get_product_recommendation(topic_name):
    """根据话题推荐产品"""
    name = topic_name.lower()
    if any(k in name for k in ["data recovery", "recover", "deleted", "formatted", "lost"]):
        return "EaseUS Data Recovery Wizard"
    elif any(k in name for k in ["partition", "c drive", "disk full", "storage", "extend", "resize", "merge"]):
        return "EaseUS Partition Master"
    elif any(k in name for k in ["clone", "migrate", "ssd", "hdd", "upgrade", "backup"]):
        return "EaseUS Disk Copy / Todo Backup"
    elif any(k in name for k in ["blue screen", "bsod", "crash", "boot", "update", "system"]):
        return "可软性植入 Partition Master（系统修复场景）"
    else:
        return "行业资讯类内容，扩大受众"


def main():
    base_dir = Path(r"C:\Users\admin\.claude\skills\.firecrawl")

    # 加载所有搜索结果
    topics_data = []

    topic_configs = [
        ("Windows 11 更新问题", "win_update.json", "windows-system"),
        ("数据恢复软件", "data_recovery.json", "data-recovery"),
        ("C盘空间不足", "c_drive.json", "storage-device"),
        ("Windows 11 蓝屏故障", "bsod.json", "windows-system"),
        ("SSD升级与克隆", "ssd.json", "storage-device"),
    ]

    for name, filename, category in topic_configs:
        filepath = base_dir / filename
        if filepath.exists():
            results = load_firecrawl_results(filepath)
            if results:
                topic = analyze_topic_from_results(name, results, category)
                topics_data.append(topic)
                print(f"[完成] {name}: {topic['article_count']} 篇文章, {topic['video_count']} 个视频")

    if not topics_data:
        print("[错误] 没有找到搜索数据")
        sys.exit(1)

    # 生成报告
    report = generate_report(topics_data)

    # 保存报告
    reports_dir = Path.home() / ".config" / "trend-reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    report_path = reports_dir / f"{timestamp}_weekly_report.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n[成功] 报告已生成: {report_path}")
    return report_path


if __name__ == "__main__":
    main()
