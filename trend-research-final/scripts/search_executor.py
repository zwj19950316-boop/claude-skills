#!/usr/bin/env python3
"""搜索执行脚本 — 调用opencli执行跨平台热点搜索"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加同级目录到路径，以便导入config_manager
sys.path.insert(0, str(Path(__file__).parent))
from config_manager import load_config, ensure_dirs, CONFIG_DIR

RAW_DATA_DIR = CONFIG_DIR / "raw_data"
TIMEOUT_SECONDS = 120  # 每个opencli命令超时时间


def get_opencli_path():
    """获取opencli可执行文件的完整路径"""
    # 尝试常见安装路径
    possible_paths = [
        Path.home() / "AppData" / "Roaming" / "npm" / "opencli.cmd",
        Path.home() / "AppData" / "Roaming" / "npm" / "opencli",
        Path("/c/Users/admin/AppData/Roaming/npm/opencli.cmd"),
        Path("/c/Users/admin/AppData/Roaming/npm/opencli"),
    ]
    for p in possible_paths:
        if p.exists():
            return str(p)
    # 回退到PATH查找
    return "opencli"


def run_opencli(cmd_args, description=""):
    """执行opencli命令，返回解析后的数据"""
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

        # 尝试解析YAML输出
        try:
            import yaml
            return yaml.safe_load(output)
        except ImportError:
            # 如果没有pyyaml，尝试简单解析或返回原始文本
            return {"raw": output}
        except Exception as e:
            print(f"    [警告] YAML解析失败: {e}")
            return {"raw": output}

    except subprocess.TimeoutExpired:
        print(f"    [警告] 命令超时 ({TIMEOUT_SECONDS}s)")
        return None
    except FileNotFoundError:
        print(f"    [错误] opencli 未找到，请确认已安装并添加到PATH")
        return None
    except Exception as e:
        print(f"    [错误] 执行异常: {e}")
        return None


def search_google(keyword, limit=10, lang="en"):
    """Google搜索"""
    return run_opencli(
        ["google", "search", keyword, "--limit", str(limit), "--lang", lang, "-f", "yaml"],
        f"Google: {keyword}"
    )


def search_google_news(keyword, limit=10, lang="en"):
    """Google News搜索"""
    return run_opencli(
        ["google", "news", keyword, "--limit", str(limit), "--lang", lang, "-f", "yaml"],
        f"Google News: {keyword}"
    )


def search_youtube(keyword, limit=20):
    """YouTube搜索"""
    return run_opencli(
        ["youtube", "search", keyword, "--limit", str(limit), "-f", "yaml"],
        f"YouTube: {keyword}"
    )


def search_twitter(keyword, limit=15):
    """Twitter/X搜索"""
    return run_opencli(
        ["twitter", "search", keyword, "--filter", "top", "--limit", str(limit), "-f", "yaml"],
        f"Twitter: {keyword}"
    )


def search_facebook(keyword, limit=10):
    """Facebook搜索"""
    return run_opencli(
        ["facebook", "search", keyword, "--limit", str(limit), "-f", "yaml"],
        f"Facebook: {keyword}"
    )


def get_youtube_channel(channel_handle, limit=5):
    """获取YouTube频道最新视频"""
    return run_opencli(
        ["youtube", "channel", channel_handle, "--limit", str(limit), "-f", "yaml"],
        f"YouTube频道: {channel_handle}"
    )


def get_twitter_profile(username):
    """获取Twitter/X用户资料"""
    return run_opencli(
        ["twitter", "profile", username, "-f", "yaml"],
        f"Twitter资料: @{username}"
    )


def get_twitter_user_tweets(username, limit=15):
    """获取Twitter用户最近推文"""
    return run_opencli(
        ["twitter", "search", f"from:{username}", "--filter", "top", "--limit", str(limit), "-f", "yaml"],
        f"Twitter推文: @{username}"
    )


def search_all_domains(config):
    """搜索所有配置领域的关键词"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "google": [],
        "google_news": [],
        "youtube": [],
        "twitter": [],
        "facebook": []
    }

    domains = config.get("domains", {})
    all_keywords = []
    for domain_name, domain_config in domains.items():
        all_keywords.extend(domain_config.get("keywords", []))

    # 去重并限制数量，避免请求过多
    unique_keywords = list(dict.fromkeys(all_keywords))[:15]

    print(f"\n=== 开始跨平台搜索 ({len(unique_keywords)}个关键词) ===")

    for keyword in unique_keywords:
        print(f"\n关键词: {keyword}")

        # Google搜索
        data = search_google(keyword)
        if data:
            results["google"].append({"keyword": keyword, "data": data})
        time.sleep(1)

        # Google News
        data = search_google_news(keyword)
        if data:
            results["google_news"].append({"keyword": keyword, "data": data})
        time.sleep(1)

        # YouTube
        data = search_youtube(keyword)
        if data:
            results["youtube"].append({"keyword": keyword, "data": data})
        time.sleep(1)

        # Twitter
        data = search_twitter(keyword)
        if data:
            results["twitter"].append({"keyword": keyword, "data": data})
        time.sleep(1)

        # Facebook (失败率较高，作为补充)
        data = search_facebook(keyword)
        if data:
            results["facebook"].append({"keyword": keyword, "data": data})
        time.sleep(1)

    return results


def search_competitors(config):
    """追踪竞争对手最新内容"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "youtube_channels": [],
        "twitter_profiles": []
    }

    competitors = config.get("competitors", {})

    print("\n=== 追踪竞争对手 ===")

    # YouTube频道
    youtube_channels = competitors.get("youtube", [])
    print(f"\nYouTube竞品频道: {len(youtube_channels)}个")
    for channel in youtube_channels[:10]:  # 限制数量避免超时
        data = get_youtube_channel(channel, limit=5)
        if data:
            results["youtube_channels"].append({
                "channel": channel,
                "data": data
            })
        time.sleep(2)

    # Twitter账号
    twitter_accounts = competitors.get("twitter", [])
    print(f"\nTwitter竞品账号: {len(twitter_accounts)}个")
    for account in twitter_accounts:
        # 尝试获取资料
        profile = get_twitter_profile(account)
        tweets = get_twitter_user_tweets(account)
        results["twitter_profiles"].append({
            "account": account,
            "profile": profile,
            "tweets": tweets
        })
        time.sleep(2)

    return results


def save_raw_data(data, suffix=""):
    """保存原始搜索数据"""
    ensure_dirs()
    RAW_DATA_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_{timestamp}{suffix}.json"
    filepath = RAW_DATA_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n[保存] 原始数据已保存: {filepath}")
    return filepath


def main():
    config = load_config()
    if not config:
        print("[错误] 配置文件不存在，请先运行: python config_manager.py init")
        sys.exit(1)

    args = sys.argv[1:]

    if "--competitors" in args:
        # 仅搜索竞争对手
        results = search_competitors(config)
        save_raw_data(results, "_competitors")
    elif "--domain" in args:
        # 指定领域搜索
        idx = args.index("--domain")
        domain = args[idx + 1] if idx + 1 < len(args) else None
        if not domain or domain not in config.get("domains", {}):
            print(f"[错误] 未知领域: {domain}")
            print(f"可用领域: {list(config.get('domains', {}).keys())}")
            sys.exit(1)

        domain_config = config["domains"][domain]
        keywords = domain_config.get("keywords", [])[:8]

        results = {
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "google": [],
            "youtube": [],
            "twitter": []
        }

        print(f"\n=== 搜索领域: {domain} ({len(keywords)}个关键词) ===")
        for keyword in keywords:
            print(f"\n关键词: {keyword}")
            data = search_google(keyword)
            if data:
                results["google"].append({"keyword": keyword, "data": data})
            time.sleep(1)

            data = search_youtube(keyword)
            if data:
                results["youtube"].append({"keyword": keyword, "data": data})
            time.sleep(1)

            data = search_twitter(keyword)
            if data:
                results["twitter"].append({"keyword": keyword, "data": data})
            time.sleep(1)

        save_raw_data(results, f"_{domain}")

    elif "--keyword" in args:
        # 指定单个关键词搜索
        idx = args.index("--keyword")
        keyword = args[idx + 1] if idx + 1 < len(args) else None
        if not keyword:
            print("[错误] 请提供关键词")
            sys.exit(1)

        results = {
            "timestamp": datetime.now().isoformat(),
            "keyword": keyword,
            "google": search_google(keyword),
            "google_news": search_google_news(keyword),
            "youtube": search_youtube(keyword),
            "twitter": search_twitter(keyword),
            "facebook": search_facebook(keyword)
        }
        save_raw_data(results, f"_{keyword.replace(' ', '_')}")

    else:
        # 默认：搜索所有领域 + 竞争对手
        print("=== 执行完整搜索 ===")
        domain_results = search_all_domains(config)
        competitor_results = search_competitors(config)

        combined = {
            "timestamp": datetime.now().isoformat(),
            "domain_search": domain_results,
            "competitor_tracking": competitor_results
        }
        save_raw_data(combined, "_full")


if __name__ == "__main__":
    main()
