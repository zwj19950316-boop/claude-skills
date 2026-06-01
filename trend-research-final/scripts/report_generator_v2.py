#!/usr/bin/env python3
"""
报告生成器 v2 — 新格式：话题+KOL提及+趋势+结合度+差异化方向
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_manager import load_config, ensure_dirs, REPORTS_DIR, CONFIG_DIR
from topic_analyzer import format_topic_summary, filter_relevant_videos
from enhanced_analytics import (
    generate_enhanced_analysis,
    format_full_analysis,
)


def extract_subscriber_number(subs_str):
    """提取订阅数数字"""
    if not subs_str:
        return 0
    import re
    match = re.search(r"([\d.]+)\s*([KMB]?)", str(subs_str))
    if match:
        num = float(match.group(1))
        suffix = match.group(2).upper()
        multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
        return int(num * multipliers.get(suffix, 1))
    return 0


def classify_topic_relevance(topic_name, topic_keywords=None):
    """判断话题与EaseUS产品的结合度
    支持动态话题：根据话题名 + 关键词综合判断
    """
    name_lower = topic_name.lower()
    keywords_lower = [k.lower() for k in (topic_keywords or [])]
    all_text = name_lower + " " + " ".join(keywords_lower)

    strong_keywords = ["data recovery", "partition", "disk full", "c drive", "backup", "clone", "migrate", "file recovery", "deleted", "recover", "format"]
    medium_keywords = ["blue screen", "bsod", "crash", "boot", "repair", "update", "system", "usb", "external drive", "storage", "ssd"]

    for kw in strong_keywords:
        if kw in all_text:
            return "strong", "EaseUS Data Recovery Wizard / Partition Master"

    for kw in medium_keywords:
        if kw in all_text:
            return "medium", "可软性植入产品作为解决方案"

    return "weak", "行业资讯类内容，扩大受众"


def get_content_directions(topic_name, topic_keywords, existing_videos):
    """基于现有内容给出差异化方向建议
    支持动态话题：根据话题名 + 关键词 + 视频标题综合判断
    """
    directions = []
    titles = [v["title"].lower() for v in existing_videos]
    all_text = (topic_name + " " + " ".join(topic_keywords or [])).lower()

    # 分析现有内容类型
    has_tutorial = any(t in title for title in titles for t in ["how to", "fix", "repair", "step by step"])
    has_comparison = any(t in title for title in titles for t in ["vs", "best", "top", "compare"])
    has_news = any(t in title for title in titles for t in ["new", "update", "latest", "microsoft"])
    has_review = any(t in title for title in titles for t in ["review", "test", "worth it"])

    if not has_tutorial:
        directions.append("教程实操类：'手把手教你解决XXX问题'")
    else:
        directions.append("进阶教程：'3种方法解决XXX，第2种最快'")

    if not has_comparison:
        directions.append("对比测评类：'5款工具对比，哪款最适合你？'")

    if not has_news:
        directions.append("新闻解读类：'微软又出问题了？深度解析影响'")

    if not has_review:
        directions.append("真实测评类：'实测XXX功能，结果出乎意料'")

    # 话题特定建议（基于关键词动态匹配）
    if any(k in all_text for k in ["data recovery", "recover", "deleted", "formatted", "recycle"]):
        directions.append("场景化内容：'我误删了 wedding 照片，24小时内找回'")
        directions.append("数据可视化：'恢复成功率对比图表'")

    if any(k in all_text for k in ["partition", "c drive", "disk full", "storage", "extend", "resize"]):
        directions.append("痛点共鸣：'C盘又满了？这个习惯正在毁掉你的电脑'")
        directions.append("Before/After：'一键扩容前后对比'")

    if any(k in all_text for k in ["update", "windows", "blue screen", "bsod", "crash", "boot"]):
        directions.append("避坑指南：'更新前必做的3件事，90%的人忽略了'")
        directions.append("合集类：'2026年Windows所有更新问题汇总'")

    if any(k in all_text for k in ["ssd", "hdd", "upgrade", "clone", "migrate", "nvme"]):
        directions.append("升级指南：'新旧硬盘无缝迁移，系统和数据一个不漏'")

    return directions[:5]


def generate_report(data_path, config, output_path=None):
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    topic_clusters = data.get("topic_clusters", {})
    google_counts = data.get("google_search_counts", {})
    trends_data = data.get("google_trends", {})
    total_videos = data.get("total_videos", 0)
    kol_channels = data.get("kol_channels", [])

    report_date = datetime.now().strftime("%Y年%m月%d日")

    report = f"""# EaseUS 热点话题调研报告（KOL内容聚类版）

> **报告日期**: {report_date}
> **监测范围**: {len(kol_channels)} 个YouTube频道（含官方+竞品）
> **数据来源**: YouTube KOL内容 + Google搜索热度 + Google Trends
> **分析逻辑**: 从KOL近期内容中聚类话题 → 统计提及频次 → 评估趋势 → 分析结合度

---

## 执行摘要

- **抓取视频总数**: {total_videos} 个
- **聚类话题数**: {len(topic_clusters)} 个
- **高KOL提及话题** (≥3个频道): {sum(1 for t in topic_clusters.values() if t.get("kol_count", 0) >= 3)} 个
- **强产品结合话题**: {sum(1 for t, d in topic_clusters.items() if classify_topic_relevance(t, d.get('keywords', []))[0] == 'strong')} 个

---

## 一、Google Trends 热门话题

"""

    # Google Trends 板块（pytrends 数据，或由 WebSearch 补充）
    interest_over_time = trends_data.get("interest_over_time", {})
    related_queries = trends_data.get("related_queries", {})
    websearch_trends = data.get("websearch_trends", {})

    if websearch_trends:
        report += "### 行业趋势佐证（WebSearch 补充）\n\n"
        for topic, info in websearch_trends.items():
            indicator = info.get("trend_indicator", "")
            report += f"**{topic}** — 🔥 {indicator}\n"
            for ev in info.get("evidence", [])[:3]:
                report += f"  - {ev}\n"
            report += "\n"

    if interest_over_time:
        report += "### 关键词搜索热度趋势（过去7天）\n\n"
        for kw, data in interest_over_time.items():
            if not data:
                continue
            items = list(data.items())
            latest = items[-3:]
            report += f"**{kw}**: "
            report += " → ".join([f"{d[-2:]}:{s}" for d, s in latest])
            report += "\n"
        report += "\n"

    if related_queries:
        report += "### 相关上升搜索词\n\n"
        for kw, data in related_queries.items():
            rising = data.get("rising", [])
            if rising:
                report += f"**{kw}**:\n"
                for item in rising[:3]:
                    q = item.get("query", "")
                    v = item.get("value", "")
                    report += f"  - {q} (+{v}% 热度)\n"
                report += "\n"

    if not websearch_trends and not interest_over_time and not related_queries:
        report += "> 注：Google Trends 数据需通过 WebSearch 或 pytrends 补充。当前 opencli/google search 被反爬虫拦截。\n\n"

    # 话题排行部分
    report += "---\n\n## 二、KOL热议话题排行\n\n"
    report += "> 排序逻辑：KOL提及数 > 总观看量 > 内容时效性\n\n"

    # 按KOL提及数+总观看量排序
    sorted_topics = sorted(
        topic_clusters.items(),
        key=lambda x: (x[1].get("kol_count", 0), x[1].get("total_views", 0)),
        reverse=True
    )

    for i, (topic_name, topic_data) in enumerate(sorted_topics[:15], 1):
        videos = topic_data.get("videos", [])
        kol_count = topic_data.get("kol_count", 0)
        total_views = topic_data.get("total_views", 0)
        google_count = google_counts.get(topic_name, 0)

        topic_keywords = topic_data.get("keywords", [])
        relevance, relevance_desc = classify_topic_relevance(topic_name, topic_keywords)
        relevance_label = {
            "strong": "✅ 强结合",
            "medium": "⚠️ 中等结合",
            "weak": "📰 弱结合/资讯"
        }.get(relevance, "📰 一般")

        directions = get_content_directions(topic_name, topic_keywords, videos)

        # 生成话题简要说明
        topic_summary = format_topic_summary(topic_name, topic_keywords, videos)

        # 生成增强分析（搜索量曲线 + 周期 + 竞争度 + 选题）
        enhanced = generate_enhanced_analysis(topic_name, topic_keywords)
        enhanced_md = format_full_analysis(enhanced)

        report += f"""### TOP {i}: {topic_name}

| 维度 | 数据 |
|-----|------|
| **KOL提及** | {kol_count} 个频道提及 |
| **相关视频** | {len(videos)} 个 |
| **总观看量** | {total_views:,} |
| **Google搜索** | 约 {google_count} 条结果 |
| **产品结合度** | {relevance_label} |
| **结合说明** | {relevance_desc} |

{topic_summary}

{enhanced_md}

**提及该话题的KOL**:

"""
        # 按频道分组展示
        channel_videos = defaultdict(list)
        for v in videos:
            channel_videos[v["channel"]].append(v)

        for ch, ch_videos in sorted(channel_videos.items(),
                                     key=lambda x: extract_subscriber_number(x[1][0].get("subscribers", "")),
                                     reverse=True)[:6]:
            subs = ch_videos[0].get("subscribers", "Unknown")
            report += f"- **{ch}** ({subs})\n"
            for v in ch_videos[:2]:
                report += f"  - [{v['title']}]({v['url']}) | {v['views']} | {v['time']}\n"

        report += f"\n**差异化内容方向建议**:\n\n"
        for d in directions:
            report += f"- {d}\n"

        report += "\n---\n\n"

    # 产品结合度汇总
    report += "## 三、话题与产品结合度总览\n\n"

    strong_topics = [(t, d) for t, d in sorted_topics if classify_topic_relevance(t, d.get("keywords", []))[0] == "strong"]
    medium_topics = [(t, d) for t, d in sorted_topics if classify_topic_relevance(t, d.get("keywords", []))[0] == "medium"]
    weak_topics = [(t, d) for t, d in sorted_topics if classify_topic_relevance(t, d.get("keywords", []))[0] == "weak"]

    report += f"""### ✅ 强结合话题（{len(strong_topics)}个）— 可直接植入产品

"""
    for topic, data in strong_topics[:5]:
        report += f"- **{topic}** — {data.get('kol_count', 0)}个KOL提及，{data.get('total_views', 0):,}观看\n"

    report += f"""
### ⚠️ 中等结合话题（{len(medium_topics)}个）— 可软性植入

"""
    for topic, data in medium_topics[:5]:
        report += f"- **{topic}** — {data.get('kol_count', 0)}个KOL提及，{data.get('total_views', 0):,}观看\n"

    report += f"""
### 📰 弱结合/资讯话题（{len(weak_topics)}个）— 扩大受众

"""
    for topic, data in weak_topics[:5]:
        report += f"- **{topic}** — {data.get('kol_count', 0)}个KOL提及，{data.get('total_views', 0):,}观看\n"

    # 数据附录
    report += f"""
---

## 四、数据附录

### 监测频道列表
"""
    for ch in kol_channels:
        report += f"- {ch}\n"

    report += f"""
### 数据采集时间
- 抓取视频数: {total_videos}
- 聚类话题数: {len(topic_clusters)}
- 报告生成时间: {datetime.now().isoformat()}

---

*本报告由 EaseUS TrendBot 自动生成，基于KOL内容聚类分析。*
"""

    if not output_path:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        output_path = REPORTS_DIR / f"{timestamp}_report_v2.md"

    ensure_dirs()
    REPORTS_DIR.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[成功] 报告已生成: {output_path}")
    return output_path


def main():
    config = load_config()
    if not config:
        print("[错误] 配置文件不存在")
        sys.exit(1)

    args = sys.argv[1:]

    data_files = sorted(Path(CONFIG_DIR / "raw_data").glob("kol_analysis_*.json"), reverse=True)
    if not data_files:
        print("[错误] 未找到KOL分析数据，请先运行 search_executor_v2.py")
        sys.exit(1)

    input_file = data_files[0]
    output_file = None

    if "--input" in args:
        idx = args.index("--input")
        input_file = Path(args[idx + 1]) if idx + 1 < len(args) else input_file

    if "--output" in args:
        idx = args.index("--output")
        output_file = Path(args[idx + 1]) if idx + 1 < len(args) else None

    print(f"[信息] 使用数据文件: {input_file}")
    report_path = generate_report(input_file, config, output_file)

    if "--email" in args:
        print("[信息] 准备发送邮件...")
        import os
        os.system(f'python "{Path(__file__).parent / "email_sender.py"}" --report "{report_path}"')


if __name__ == "__main__":
    main()
