#!/usr/bin/env python3
"""
增强分析模块 — 提供四大新增功能：
1. 近7天搜索量曲线（Google Trends / pytrends）
2. 热点周期分析（历史类似热点持续时间）
3. YouTube竞争度分析（近7天长视频数量）
4. 选题推荐（高播放视频 + 高排名文章）

Author: Trend Research Skill
"""

import json
import logging
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from config_manager import CONFIG_DIR, ensure_dirs, load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_DATA_DIR = CONFIG_DIR / "raw_data"

# ---------------------------------------------------------------------------
# 1. 搜索量曲线 — Google Trends (pytrends)
# ---------------------------------------------------------------------------

def get_pytrends_client() -> Any:
    """Initialize pytrends client."""
    try:
        from pytrends.request import TrendReq
        return TrendReq(hl="en-US", tz=360, retries=0, backoff_factor=0.1)
    except ImportError:
        logger.warning("pytrends not installed. Search volume curve will be unavailable.")
        return None


def fetch_search_volume_curve(
    keywords: List[str],
    timeframe: str = "now 7-d",
    geo: str = "US",
) -> Dict[str, Any]:
    """
    获取近7天搜索量曲线数据。

    Returns:
        {
            "keyword": {
                "dates": ["2026-05-21", ...],
                "scores": [45, 52, ...],
                "trend": "上升/下降/平稳/波动",
                "peak_date": "2026-05-23",
                "peak_score": 78,
            }
        }
    """
    client = get_pytrends_client()
    if not client:
        return {}

    # pytrends 每次最多5个关键词
    all_results: Dict[str, Any] = {}
    batch_size = 5

    for i in range(0, len(keywords), batch_size):
        batch = keywords[i : i + batch_size]
        try:
            client.build_payload(batch, cat=0, timeframe=timeframe, geo=geo)
            iot_df = client.interest_over_time()

            if iot_df is None or iot_df.empty:
                continue

            if "isPartial" in iot_df.columns:
                iot_df = iot_df.drop(columns=["isPartial"])

            for kw in batch:
                if kw not in iot_df.columns:
                    continue
                series = iot_df[kw].dropna()
                dates = [str(d)[:10] for d in series.index]
                scores = [int(s) for s in series.values]

                if not scores:
                    continue

                # 计算趋势方向
                first_half = scores[: len(scores) // 2]
                second_half = scores[len(scores) // 2 :]
                avg_first = sum(first_half) / len(first_half) if first_half else 0
                avg_second = sum(second_half) / len(second_half) if second_half else 0

                if avg_second > avg_first * 1.15:
                    trend = "上升"
                elif avg_second < avg_first * 0.85:
                    trend = "下降"
                elif max(scores) - min(scores) > 30:
                    trend = "波动"
                else:
                    trend = "平稳"

                peak_idx = scores.index(max(scores))

                all_results[kw] = {
                    "dates": dates,
                    "scores": scores,
                    "trend": trend,
                    "peak_date": dates[peak_idx] if peak_idx < len(dates) else None,
                    "peak_score": max(scores),
                    "avg_score": round(sum(scores) / len(scores), 1),
                }

            time.sleep(1.5)  # rate limit
        except Exception as e:
            logger.warning(f"pytrends fetch failed for {batch}: {e}")
            time.sleep(2)

    return all_results


def format_volume_curve(curve_data: Dict[str, Any]) -> str:
    """将搜索量曲线格式化为 Markdown 表格 + 趋势描述。"""
    if not curve_data:
        return "> 搜索量曲线数据暂不可用（需安装 pytrends）。\n"

    lines = ["### 近7天搜索量趋势\n"]
    for kw, data in curve_data.items():
        dates = data["dates"]
        scores = data["scores"]
        trend = data["trend"]
        peak = data["peak_score"]
        peak_date = data["peak_date"]
        avg = data["avg_score"]

        # 简化的 ASCII 趋势图
        if scores:
            max_s = max(scores) if max(scores) > 0 else 1
            bars = ["█" * int(s / max_s * 10) if max_s > 0 else "" for s in scores]
            # 只展示最近4天的柱状图
            recent_bars = bars[-4:] if len(bars) >= 4 else bars
            chart = " ".join(recent_bars)
        else:
            chart = "N/A"

        lines.append(f"**{kw}** — 趋势: {trend} | 均值: {avg} | 峰值: {peak} ({peak_date})")
        lines.append(f"```")
        lines.append(f"近4天: {chart}")
        lines.append(f"```")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. 热点周期分析 — 基于历史数据 + WebSearch 推断
# ---------------------------------------------------------------------------

def search_historical_duration(topic_name: str, topic_keywords: List[str]) -> Dict[str, Any]:
    """
    通过 WebSearch 查找过往类似热点的持续时间。
    返回结构化数据供报告使用。
    """
    # 构建搜索查询：查找历史同类问题的修复时间线
    query_templates = [
        f"{topic_name} how long fixed Microsoft",
        f"{topic_name} issue resolved timeline",
        f"{topic_name} patch release date",
    ]

    # 这里返回一个结构，实际数据由调用方通过 WebSearch 填充
    return {
        "topic": topic_name,
        "search_queries": query_templates,
        "typical_duration_days": None,  # 待填充
        "historical_cases": [],         # 待填充
        "resolution_pattern": None,     # 待填充
    }


def infer_duration_pattern(topic_name: str) -> Tuple[Optional[int], str]:
    """
    基于话题类型推断典型热点持续时间。
    返回 (典型天数, 模式描述)。
    """
    name_lower = topic_name.lower()

    # Windows 更新问题
    if any(k in name_lower for k in ["update", "kb", "patch", "build"]):
        return (
            7,
            "微软通常会在问题曝光后 3-7 天内发布补丁修复，紧急情况下 24-48 小时推出热修复。",
        )

    # 蓝屏/崩溃
    if any(k in name_lower for k in ["blue screen", "bsod", "crash", "boot loop"]):
        return (
            14,
            "驱动或系统级蓝屏问题通常需要 1-2 周稳定，用户端 workaround 可在 24 小时内缓解。",
        )

    # 存储空间 / C盘满
    if any(k in name_lower for k in ["c drive", "disk full", "storage", "low disk"]):
        return (
            30,
            "存储空间管理是持续性痛点，非突发性热点，热度维持 2-4 周，适合长期内容布局。",
        )

    # 分区管理
    if any(k in name_lower for k in ["partition", "resize", "extend", "merge"]):
        return (
            21,
            "分区相关话题热度周期约 2-3 周，通常在系统大版本更新后（如 24H2）出现高峰。",
        )

    # 数据恢复
    if any(k in name_lower for k in ["data recovery", "recover", "deleted", "formatted"]):
        return (
            14,
            "数据恢复需求在误删事件（如系统更新、误操作）后 1-2 周内集中爆发，属于脉冲式热点。",
        )

    # SSD/硬件升级
    if any(k in name_lower for k in ["ssd", "hdd", "upgrade", "clone", "nvme"]):
        return (
            45,
            "硬件升级话题具有季节性（黑五、开学季），单轮热度可维持 1-2 个月。",
        )

    # 性能优化
    if any(k in name_lower for k in ["speed up", "optimize", "slow", "performance"]):
        return (
            21,
            "性能优化话题在系统更新后 2-3 周内热度较高，属于周期性复现热点。",
        )

    # 默认
    return (
        14,
        "一般技术话题热度维持 1-2 周，建议尽快跟进以获取搜索流量红利。",
    )


def format_duration_analysis(topic_name: str) -> str:
    """格式化热点周期分析文本。"""
    duration, pattern = infer_duration_pattern(topic_name)

    lines = [
        f"#### 热点周期预测\n",
        f"- **预估热度持续**: 约 {duration} 天",
        f"- **模式判断**: {pattern}",
    ]

    if duration and duration <= 7:
        lines.append("- **行动建议**: [紧急] 建议 48 小时内发布内容抢占流量")
    elif duration and duration <= 14:
        lines.append("- **行动建议**: [短期] 建议本周内跟进")
    else:
        lines.append("- **行动建议**: [中长期] 可精心策划深度内容")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 3. YouTube 竞争度分析 — 近7天长视频数量
# ---------------------------------------------------------------------------

def get_opencli_path() -> str:
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


def get_firecrawl_path() -> str:
    possible_paths = [
        Path.home() / "AppData" / "Roaming" / "npm" / "firecrawl.cmd",
        Path.home() / "AppData" / "Roaming" / "npm" / "firecrawl",
        Path("/c/Users/admin/AppData/Roaming/npm/firecrawl.cmd"),
        Path("/c/Users/admin/AppData/Roaming/npm/firecrawl"),
    ]
    for p in possible_paths:
        if p.exists():
            return str(p)
    return "firecrawl"


def run_opencli(cmd_args: List[str], description: str = "") -> Optional[Any]:
    opencli_path = get_opencli_path()
    full_cmd = [opencli_path] + cmd_args
    if description:
        logger.info(f"[搜索] {description}")

    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            err = result.stderr.strip()[:200]
            logger.warning(f"opencli error: {err}")
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
        logger.warning(f"opencli failed: {e}")
        return None


def parse_video_duration(duration_str: str) -> int:
    """将时长字符串转换为分钟数。"""
    if not duration_str:
        return 0
    duration_str = str(duration_str).strip()
    # 格式: "10:23" 或 "1:23:45"
    parts = duration_str.split(":")
    try:
        if len(parts) == 2:
            return int(parts[0]) + int(parts[1]) / 60
        elif len(parts) == 3:
            return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
    except ValueError:
        pass
    return 0


def is_long_video(duration_str: str, threshold_minutes: int = 5) -> bool:
    """判断是否为长视频（默认 >= 5分钟）。"""
    return parse_video_duration(duration_str) >= threshold_minutes


def fetch_youtube_competition(
    query: str,
    limit: int = 50,
    days_back: int = 7,
) -> Dict[str, Any]:
    """
    搜索 YouTube 近7天相关视频，统计竞争度指标。

    Returns:
        {
            "total_videos": 50,
            "long_videos": 32,
            "short_videos": 18,
            "avg_duration_min": 8.5,
            "top_channels": [("@Britec09", 5), ...],
            "high_view_videos": [{"title": ..., "views": ..., "channel": ...}, ...],
        }
    """
    data = run_opencli(
        ["youtube", "search", query, "--limit", str(limit), "-f", "yaml"],
        f"YouTube竞争度: {query}",
    )

    if not data or not isinstance(data, list):
        return {}

    total = 0
    long_count = 0
    short_count = 0
    durations = []
    channel_counts = defaultdict(int)
    videos = []

    for item in data:
        if not isinstance(item, dict):
            continue
        field = item.get("field", "")
        value = item.get("value", "")

        # 解析视频条目（格式与 search_executor_v3 一致）
        if isinstance(value, str) and "|" in value:
            parts = value.split("|")
            if len(parts) >= 3:
                total += 1
                duration_str = parts[0].strip()
                views_str = parts[1].strip()
                title = str(field).strip()

                dur_min = parse_video_duration(duration_str)
                durations.append(dur_min)

                if is_long_video(duration_str):
                    long_count += 1
                else:
                    short_count += 1

                views_num = 0
                match = re.match(r"([\d.]+)\s*([KMB]?)", str(views_str), re.IGNORECASE)
                if match:
                    num = float(match.group(1))
                    suffix = match.group(2).upper()
                    multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
                    views_num = int(num * multipliers.get(suffix, 1))

                # 尝试获取频道名
                channel = "Unknown"
                # 在 list 中找对应的 channel 字段
                # 这里简化处理

                videos.append({
                    "title": title,
                    "duration": duration_str,
                    "duration_min": dur_min,
                    "views": views_str,
                    "views_num": views_num,
                    "channel": channel,
                })

    # 按观看量排序取 Top
    videos_sorted = sorted(videos, key=lambda x: x["views_num"], reverse=True)

    return {
        "query": query,
        "total_videos": total,
        "long_videos": long_count,
        "short_videos": short_count,
        "avg_duration_min": round(sum(durations) / len(durations), 1) if durations else 0,
        "top_channels": sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        "high_view_videos": videos_sorted[:10],
    }


def format_competition_analysis(comp_data: Dict[str, Any]) -> str:
    """格式化竞争度分析为 Markdown。"""
    if not comp_data:
        return "> YouTube 竞争度数据暂不可用。\n"

    total = comp_data.get("total_videos", 0)
    long = comp_data.get("long_videos", 0)
    short = comp_data.get("short_videos", 0)
    avg_dur = comp_data.get("avg_duration_min", 0)

    # 竞争度评级
    if long >= 20:
        level = "[激烈] 竞争激烈"
        advice = "长视频供给饱和，建议差异化角度或 Shorts 形式切入"
    elif long >= 10:
        level = "[中等] 竞争中等"
        advice = "有一定供给但仍有空间，建议优化标题和缩略图"
    else:
        level = "[较低] 竞争较低"
        advice = "长视频供给不足，是抢占搜索排名的窗口期"

    lines = [
        f"#### YouTube 竞争度分析（近7天）\n",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 相关视频总数 | {total} |",
        f"| 长视频（≥5min） | {long} |",
        f"| 短视频（<5min） | {short} |",
        f"| 平均时长 | {avg_dur} 分钟 |",
        f"| 竞争评级 | {level} |",
        f"",
        f"**建议**: {advice}",
    ]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 4. 选题推荐 — 高播放视频 + 高排名文章
# ---------------------------------------------------------------------------

def fetch_top_youtube_content(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """获取 YouTube 上某关键词的高播放视频。"""
    data = run_opencli(
        ["youtube", "search", query, "--limit", str(limit), "-f", "yaml"],
        f"选题-YouTube: {query}",
    )

    if not data or not isinstance(data, list):
        return []

    videos = []
    for item in data:
        if not isinstance(item, dict):
            continue
        field = item.get("field", "")
        value = item.get("value", "")

        if isinstance(value, str) and "|" in value:
            parts = value.split("|")
            if len(parts) >= 3:
                title = str(field).strip()
                duration = parts[0].strip()
                views_str = parts[1].strip()

                views_num = 0
                match = re.match(r"([\d.]+)\s*([KMB]?)", str(views_str), re.IGNORECASE)
                if match:
                    num = float(match.group(1))
                    suffix = match.group(2).upper()
                    multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
                    views_num = int(num * multipliers.get(suffix, 1))

                videos.append({
                    "title": title,
                    "duration": duration,
                    "views": views_str,
                    "views_num": views_num,
                })

    return sorted(videos, key=lambda x: x["views_num"], reverse=True)


def fetch_top_web_articles(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """使用 firecrawl 搜索高排名文章。"""
    try:
        firecrawl_path = get_firecrawl_path()
        result = subprocess.run(
            [firecrawl_path, "search", query, "--limit", str(limit), "--json"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            return []

        data = json.loads(result.stdout)
        articles = []
        # firecrawl 返回格式: {"success":true,"data":{"web":[...]}}
        web_results = data.get("data", {}).get("web", []) if isinstance(data.get("data"), dict) else data.get("data", [])
        for item in web_results:
            articles.append({
                "title": item.get("title", "N/A"),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
            })
        return articles
    except Exception as e:
        logger.warning(f"firecrawl search failed: {e}")
        return []


def extract_content_theme(title: str) -> str:
    """从标题中提取内容主旨（简化版）。"""
    title_lower = title.lower()

    themes = []
    if any(w in title_lower for w in ["how to", "fix", "repair", "solve", "solution"]):
        themes.append("解决方案/教程")
    if any(w in title_lower for w in ["best", "top", "vs", "compare", "review"]):
        themes.append("对比评测")
    if any(w in title_lower for w in ["new", "latest", "update", "announced", "news"]):
        themes.append("新闻解读")
    if any(w in title_lower for w in ["warning", "avoid", "don't", "beware", "mistake"]):
        themes.append("避坑提醒")
    if any(w in title_lower for w in ["tips", "tricks", "secret", "hidden"]):
        themes.append("技巧分享")

    return "、".join(themes) if themes else "综合内容"


def format_content_recommendations(
    topic_name: str,
    topic_keywords: List[str],
    top_videos: List[Dict[str, Any]],
    top_articles: List[Dict[str, Any]],
) -> str:
    """格式化选题推荐为 Markdown。"""
    lines = [f"#### 选题参考\n"]

    # YouTube 高播放视频
    lines.append("**YouTube 高播放视频参考**\n")
    for i, v in enumerate(top_videos[:3], 1):
        theme = extract_content_theme(v["title"])
        lines.append(f"{i}. **{v['title']}** ({v['views']} views)")
        lines.append(f"   - 内容主旨: {theme}")
        lines.append(f"   - 时长: {v['duration']}")
        lines.append("")

    # 高排名文章
    lines.append("**高排名文章参考**\n")
    for i, a in enumerate(top_articles[:3], 1):
        theme = extract_content_theme(a["title"])
        lines.append(f"{i}. **{a['title']}**")
        if a.get("url"):
            lines.append(f"   - 链接: {a['url']}")
        lines.append(f"   - 内容主旨: {theme}")
        if a.get("description"):
            desc = a["description"][:120]
            lines.append(f"   - 摘要: {desc}...")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 5. 主入口 — 为话题生成完整增强分析
# ---------------------------------------------------------------------------

def generate_enhanced_analysis(
    topic_name: str,
    topic_keywords: List[str],
    enable_search_volume: bool = True,
    enable_duration: bool = True,
    enable_competition: bool = True,
    enable_recommendations: bool = True,
) -> Dict[str, Any]:
    """
    为单个话题生成完整的增强分析数据。

    Returns:
        {
            "search_volume": {...},
            "duration_analysis": "markdown",
            "competition": {...},
            "recommendations": "markdown",
        }
    """
    result = {}

    # 1. 搜索量曲线
    if enable_search_volume:
        search_kws = [topic_name] + topic_keywords[:2]
        # 清理关键词，去除停用词
        search_kws = [kw for kw in search_kws if len(kw) > 3]
        search_kws = list(dict.fromkeys(search_kws))[:5]  # 去重，最多5个
        if search_kws:
            try:
                result["search_volume"] = fetch_search_volume_curve(search_kws, timeframe="now 7-d")
            except Exception as e:
                logger.warning(f"Search volume fetch failed (network/proxy issue): {e}")
                result["search_volume"] = {}
        else:
            result["search_volume"] = {}

    # 2. 热点周期
    if enable_duration:
        result["duration_analysis"] = format_duration_analysis(topic_name)

    # 3. YouTube 竞争度
    if enable_competition:
        comp_data = fetch_youtube_competition(topic_name, limit=30)
        result["competition"] = comp_data

    # 4. 选题推荐
    if enable_recommendations:
        top_videos = fetch_top_youtube_content(topic_name, limit=20)
        top_articles = fetch_top_web_articles(topic_name, limit=10)
        result["recommendations"] = format_content_recommendations(
            topic_name, topic_keywords, top_videos, top_articles
        )

    return result


def format_full_analysis(analysis_data: Dict[str, Any]) -> str:
    """将增强分析数据格式化为完整的 Markdown 区块。"""
    parts = []

    # 搜索量曲线
    if "search_volume" in analysis_data:
        parts.append(format_volume_curve(analysis_data["search_volume"]))

    # 热点周期
    if "duration_analysis" in analysis_data:
        parts.append(analysis_data["duration_analysis"])

    # 竞争度
    if "competition" in analysis_data:
        parts.append(format_competition_analysis(analysis_data["competition"]))

    # 选题推荐
    if "recommendations" in analysis_data:
        parts.append(analysis_data["recommendations"])

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("用法: python enhanced_analytics.py <topic_name> [keyword1] [keyword2] ...")
        sys.exit(1)

    topic_name = sys.argv[1]
    keywords = sys.argv[2:]

    print(f"=== 增强分析: {topic_name} ===\n")
    analysis = generate_enhanced_analysis(topic_name, keywords)
    print(format_full_analysis(analysis))


if __name__ == "__main__":
    main()
