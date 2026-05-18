#!/usr/bin/env python3
"""报告生成脚本 — 分析搜索数据，生成结构化热点报告"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config_manager import load_config, ensure_dirs, REPORTS_DIR, CONFIG_DIR


def parse_time_ago(time_str):
    """解析'2h ago', '3 days ago'等时间字符串为大致的datetime"""
    if not time_str:
        return None
    time_str = str(time_str).lower().strip()
    now = datetime.now()

    # 匹配数字+单位
    match = re.match(r'(\d+)\s*(h|hour|hr|d|day|w|week|m|min|minute|s|sec)', time_str)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if unit in ('h', 'hour', 'hr'):
            return now - timedelta(hours=num)
        elif unit in ('d', 'day'):
            return now - timedelta(days=num)
        elif unit in ('w', 'week'):
            return now - timedelta(weeks=num)
        elif unit in ('m', 'min', 'minute'):
            return now - timedelta(minutes=num)
        elif unit in ('s', 'sec'):
            return now - timedelta(seconds=num)

    # 尝试直接解析日期格式
    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%d %b %Y"):
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue

    return None


def calculate_timeliness_score(time_str):
    """计算时效性得分：24h内+3, 3天内+2, 7天内+1"""
    dt = parse_time_ago(time_str)
    if not dt:
        return 0

    age = datetime.now() - dt
    if age <= timedelta(hours=24):
        return 3
    elif age <= timedelta(days=3):
        return 2
    elif age <= timedelta(days=7):
        return 1
    return 0


def extract_number(text):
    """从文本中提取数字（如 '1.2K' -> 1200, '1.5M' -> 1500000）"""
    if not text:
        return 0
    text = str(text).replace(',', '').strip()

    # 匹配 K/M/B
    match = re.match(r'([\d.]+)\s*([KMB]?)', text, re.IGNORECASE)
    if match:
        num = float(match.group(1))
        suffix = match.group(2).upper()
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        return int(num * multipliers.get(suffix, 1))

    # 直接匹配数字
    nums = re.findall(r'\d+', text)
    if nums:
        return int(nums[0])

    return 0


def normalize_data(data):
    """将opencli返回的各种格式统一为列表"""
    if not data:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # 如果data里有列表，提取列表
        for key in ['results', 'items', 'data', 'tweets', 'videos', 'posts']:
            if key in data and isinstance(data[key], list):
                return data[key]
        # 否则返回单元素列表
        return [data]
    return []


def analyze_search_data(raw_data):
    """分析原始搜索数据，提取热点话题"""
    topics = defaultdict(lambda: {
        'title': '',
        'sources': [],
        'platforms': set(),
        'urls': [],
        'interactions': [],
        'timestamps': [],
        'google_count': 0,
        'youtube_count': 0,
        'twitter_count': 0,
        'news_count': 0
    })

    # 分析Google搜索
    for item in raw_data.get('google', []):
        keyword = item.get('keyword', '')
        results = normalize_data(item.get('data'))
        for result in results[:5]:
            title = result.get('title', '') if isinstance(result, dict) else str(result)
            if not title:
                continue
            key = title.lower()[:60]
            topics[key]['title'] = title
            topics[key]['platforms'].add('Google')
            topics[key]['google_count'] += 1
            topics[key]['sources'].append(f"Google搜索: {keyword}")
            if isinstance(result, dict) and result.get('url'):
                topics[key]['urls'].append(result['url'])

    # 分析Google News
    for item in raw_data.get('google_news', []):
        keyword = item.get('keyword', '')
        results = normalize_data(item.get('data'))
        for result in results[:5]:
            title = result.get('title', '') if isinstance(result, dict) else str(result)
            if not title:
                continue
            key = title.lower()[:60]
            topics[key]['title'] = title
            topics[key]['platforms'].add('Google News')
            topics[key]['news_count'] += 1
            topics[key]['sources'].append(f"Google News: {keyword}")
            if isinstance(result, dict) and result.get('url'):
                topics[key]['urls'].append(result['url'])

    # 分析YouTube
    for item in raw_data.get('youtube', []):
        keyword = item.get('keyword', '')
        results = normalize_data(item.get('data'))
        for result in results[:10]:
            if not isinstance(result, dict):
                continue
            title = result.get('title', '')
            if not title:
                continue
            key = title.lower()[:60]
            topics[key]['title'] = title
            topics[key]['platforms'].add('YouTube')
            topics[key]['youtube_count'] += 1
            topics[key]['sources'].append(f"YouTube: {keyword}")

            views = extract_number(result.get('views', '0'))
            if views:
                topics[key]['interactions'].append(views)

            ts = result.get('published', '')
            if ts:
                topics[key]['timestamps'].append(ts)

            url = result.get('url', '')
            if url:
                topics[key]['urls'].append(url)

    # 分析Twitter
    for item in raw_data.get('twitter', []):
        keyword = item.get('keyword', '')
        results = normalize_data(item.get('data'))
        for result in results[:10]:
            if not isinstance(result, dict):
                continue
            text = result.get('text', '')
            if not text:
                continue
            key = text.lower()[:60]
            topics[key]['title'] = text[:100]
            topics[key]['platforms'].add('Twitter')
            topics[key]['twitter_count'] += 1
            topics[key]['sources'].append(f"Twitter: {keyword}")

            likes = extract_number(result.get('likes', '0'))
            views = extract_number(result.get('views', '0'))
            if likes or views:
                topics[key]['interactions'].append(max(likes, views))

            ts = result.get('created_at', '')
            if ts:
                topics[key]['timestamps'].append(ts)

            url = result.get('url', '')
            if url:
                topics[key]['urls'].append(url)

    return topics


def calculate_hot_score(topic_data):
    """计算热度评分（1-10分）"""
    score = 0

    # 基础分（0-3分）：出现次数
    total_mentions = (topic_data['google_count'] + topic_data['youtube_count'] +
                      topic_data['twitter_count'])
    score += min(total_mentions * 0.5, 3)

    # 互动分（0-2分）
    if topic_data['interactions']:
        avg_interaction = sum(topic_data['interactions']) / len(topic_data['interactions'])
        if avg_interaction > 100000:
            score += 2
        elif avg_interaction > 10000:
            score += 1.5
        elif avg_interaction > 1000:
            score += 1
        elif avg_interaction > 100:
            score += 0.5

    # 时效分（0-3分）
    max_timeliness = 0
    for ts in topic_data['timestamps']:
        t = calculate_timeliness_score(ts)
        max_timeliness = max(max_timeliness, t)
    score += max_timeliness

    # 新闻分（0-1分）
    if topic_data['news_count'] > 0:
        score += 1

    # 跨平台分：覆盖>=3平台额外+1
    if len(topic_data['platforms']) >= 3:
        score += 1

    return round(min(score, 10), 1)


def get_easeus_relevance(title):
    """判断话题与EaseUS产品的关联度"""
    title_lower = title.lower()

    # 强关联关键词
    strong = ['data recovery', 'recover', 'deleted', 'formatted', 'partition',
              'disk full', 'c drive', 'storage full', 'extend', 'resize',
              'hard drive', 'ssd', 'backup', 'clone', 'migrate']
    # 中关联关键词
    medium = ['windows update', 'blue screen', 'bsod', 'boot', 'system repair',
              'not working', 'error', 'fix', 'usb', 'sd card', 'external drive']
    # 弱关联关键词
    weak = ['windows 11', 'windows 10', 'pc', 'computer', 'tech', 'tutorial']

    for kw in strong:
        if kw in title_lower:
            return 'strong'
    for kw in medium:
        if kw in title_lower:
            return 'medium'
    for kw in weak:
        if kw in title_lower:
            return 'weak'
    return 'none'


def get_priority(score, relevance):
    """根据得分和关联度确定优先级"""
    if score >= 7 and relevance in ('strong', 'medium'):
        return 'P0'
    elif score >= 6 or (score >= 5 and relevance == 'strong'):
        return 'P1'
    elif score >= 4:
        return 'P2'
    return None


def analyze_competitors(competitor_data):
    """分析竞争对手数据"""
    competitors = []

    # 分析YouTube频道
    for ch_data in competitor_data.get('youtube_channels', []):
        channel = ch_data.get('channel', '')
        data = ch_data.get('data', {})

        if not isinstance(data, dict):
            continue

        info = {
            'channel': channel,
            'platform': 'YouTube',
            'name': '',
            'subscribers': '',
            'recent_videos': []
        }

        # 解析频道信息
        videos_started = False
        for key, value in data.items():
            if key == 'field':
                continue
            if isinstance(value, str):
                if 'subscriber' in key.lower() or key == 'subscribers':
                    info['subscribers'] = value
                elif key == 'name':
                    info['name'] = value
                elif key == '--- Recent Videos ---':
                    videos_started = True
                elif videos_started and value and '|' in value:
                    # 解析视频信息: title | views | time | url
                    parts = value.split('|')
                    if len(parts) >= 3:
                        info['recent_videos'].append({
                            'title': key,
                            'duration': parts[0].strip() if len(parts) > 0 else '',
                            'views': parts[1].strip() if len(parts) > 1 else '',
                            'time': parts[2].strip() if len(parts) > 2 else '',
                            'url': parts[3].strip() if len(parts) > 3 else ''
                        })

        if info['recent_videos']:
            competitors.append(info)

    # 分析Twitter账号
    for tw_data in competitor_data.get('twitter_profiles', []):
        account = tw_data.get('account', '')
        profile = tw_data.get('profile', {})
        tweets = tw_data.get('tweets', {})

        info = {
            'account': account,
            'platform': 'Twitter',
            'followers': '',
            'recent_tweets': []
        }

        if isinstance(profile, dict):
            info['followers'] = str(profile.get('followers', ''))

        tweet_list = normalize_data(tweets)
        for tweet in tweet_list[:5]:
            if isinstance(tweet, dict):
                info['recent_tweets'].append({
                    'text': tweet.get('text', '')[:150],
                    'likes': tweet.get('likes', ''),
                    'time': tweet.get('created_at', ''),
                    'url': tweet.get('url', '')
                })

        if info['recent_tweets']:
            competitors.append(info)

    return competitors


def generate_report(raw_data_path, config, output_path=None):
    """生成完整的热点报告"""

    # 读取原始数据
    with open(raw_data_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    domain_search = raw_data.get('domain_search', raw_data)
    competitor_data = raw_data.get('competitor_tracking', {})

    # 分析热点话题
    topics = analyze_search_data(domain_search)

    # 计算评分和排序
    topic_list = []
    for key, data in topics.items():
        if not data['title']:
            continue
        score = calculate_hot_score(data)
        relevance = get_easeus_relevance(data['title'])
        priority = get_priority(score, relevance)

        topic_list.append({
            'title': data['title'][:120],
            'score': score,
            'relevance': relevance,
            'priority': priority,
            'platforms': list(data['platforms']),
            'urls': list(set(data['urls']))[:5],
            'sources': list(set(data['sources']))[:5],
            'google_count': data['google_count'],
            'youtube_count': data['youtube_count'],
            'twitter_count': data['twitter_count'],
            'news_count': data['news_count'],
            'max_interaction': max(data['interactions']) if data['interactions'] else 0,
            'latest_time': data['timestamps'][0] if data['timestamps'] else ''
        })

    # 按热度排序
    topic_list.sort(key=lambda x: x['score'], reverse=True)

    # 过滤低质量
    topic_list = [t for t in topic_list if t['score'] >= 3]

    # 限制数量
    max_topics = config.get('report', {}).get('max_hot_topics', 15)
    top_topics = topic_list[:max_topics]

    # 分析竞争对手
    competitors = analyze_competitors(competitor_data)

    # 分类选题
    p0_topics = [t for t in top_topics if t['priority'] == 'P0']
    p1_topics = [t for t in top_topics if t['priority'] == 'P1']
    p2_topics = [t for t in top_topics if t['priority'] == 'P2']

    # 生成报告Markdown
    report_date = datetime.now().strftime("%Y年%m月%d日")
    report = f"""# 热点话题调研报告 — EaseUS社媒选题参考

> **报告日期**: {report_date}
> **监测领域**: Windows系统 / 数据恢复 / 存储设备
> **数据来源**: Google / YouTube / X(Twitter) / Facebook
> **品牌**: EaseUS (Data Recovery Wizard / Partition Master)

## 执行摘要

- **热点话题总数**: {len(top_topics)}个
- **P0级选题** (立即跟进): {len(p0_topics)}个
- **P1级选题** (本周跟进): {len(p1_topics)}个
- **P2级选题** (储备观察): {len(p2_topics)}个
- **竞品动态**: {len(competitors)}个账号有新内容

---

## 一、热点话题排行

"""

    for i, topic in enumerate(top_topics, 1):
        priority_label = topic['priority'] if topic['priority'] else 'P2'
        relevance_label = {
            'strong': '强关联',
            'medium': '中关联',
            'weak': '弱关联',
            'none': '一般'
        }.get(topic['relevance'], '一般')

        platforms_str = ' / '.join(topic['platforms'])

        report += f"""### TOP {i}: {topic['title']}
- **热度评分**: {topic['score']}/10
- **优先级**: {priority_label}
- **产品关联**: {relevance_label}
- **来源平台**: {platforms_str}
"""

        if topic['urls']:
            report += "- **相关链接**:\n"
            for url in topic['urls'][:3]:
                report += f"  - {url}\n"

        report += f"""- **热度指标**:
  - Google搜索提及: {topic['google_count']}次
  - YouTube相关视频: {topic['youtube_count']}个
  - Twitter讨论: {topic['twitter_count']}条
"""
        if topic['news_count']:
            report += f"  - Google News报道: {topic['news_count']}篇\n"
        if topic['max_interaction']:
            report += f"  - 最高互动量: {topic['max_interaction']:,}\n"
        if topic['latest_time']:
            report += f"  - 最新内容: {topic['latest_time']}\n"

        # EaseUS结合建议
        report += "- **EaseUS结合建议**:\n"
        if topic['relevance'] == 'strong':
            report += "  - 可直接结合EaseUS产品做教程/测评内容\n"
        elif topic['relevance'] == 'medium':
            report += "  - 可软性植入EaseUS产品作为解决方案\n"
        else:
            report += "  - 可作为行业动态/资讯类内容，扩大受众\n"

        # 选题角度建议
        title_lower = topic['title'].lower()
        if 'recovery' in title_lower or 'recover' in title_lower or 'deleted' in title_lower:
            report += "  - 选题角度: '如何恢复误删的XXX — EaseUS Data Recovery实测'\n"
        elif 'partition' in title_lower or 'drive' in title_lower or 'disk' in title_lower:
            report += "  - 选题角度: 'C盘满了怎么办？EaseUS Partition Master一键扩容'\n"
        elif 'update' in title_lower or 'windows 11' in title_lower:
            report += "  - 选题角度: 'Win11更新后XXX问题解决'（可关联系统备份/数据保护）\n"
        elif 'full' in title_lower or 'storage' in title_lower:
            report += "  - 选题角度: '存储空间告急？三步清理+分区扩容指南'\n"
        else:
            report += "  - 选题角度: 结合热点做技术解读或产品场景化展示\n"

        report += "\n"

    # 竞争对手部分
    report += "---\n\n## 二、竞争对手内容追踪\n\n"

    if not competitors:
        report += "*暂无竞品数据（可能由于平台限制或配置问题）*\n\n"
    else:
        for comp in competitors:
            if comp.get('platform') == 'YouTube':
                report += f"""### {comp.get('name', comp.get('channel', 'Unknown'))} ({comp.get('subscribers', 'Unknown')})
- **平台**: YouTube
- **频道**: {comp.get('channel', '')}
- **最新内容**:
"""
                for video in comp.get('recent_videos', [])[:5]:
                    report += f"  - {video.get('title', '')} | {video.get('views', '')} | {video.get('time', '')}\n"
                    if video.get('url'):
                        report += f"    {video.get('url')}\n"

                # 策略观察
                report += "- **策略观察**: "
                video_count = len(comp.get('recent_videos', []))
                if video_count >= 3:
                    report += "发布频率较高，保持密切关注。"
                else:
                    report += "发布频率一般。"

                # 检查是否涉及数据恢复/分区
                has_recovery = any('recovery' in v.get('title', '').lower() or
                                   'partition' in v.get('title', '').lower()
                                   for v in comp.get('recent_videos', []))
                if has_recovery:
                    report += "近期有数据恢复/分区管理相关内容，**直接竞品动作**。"
                report += "\n\n"

            elif comp.get('platform') == 'Twitter':
                report += f"""### @{comp.get('account', '')} ({comp.get('followers', '')} followers)
- **平台**: Twitter/X
- **最新推文**:
"""
                for tweet in comp.get('recent_tweets', [])[:3]:
                    report += f"  - {tweet.get('text', '')} | 点赞: {tweet.get('likes', '')}\n"
                report += "\n"

    # 建议选题部分
    report += "---\n\n## 三、建议选题角度\n\n"

    if p0_topics:
        report += "### P0 — 立即跟进（48小时内）\n\n"
        for i, topic in enumerate(p0_topics[:5], 1):
            report += f"""{i}. **{topic['title']}**
   - 热度: {topic['score']}/10
   - 关联产品: """
            if topic['relevance'] == 'strong':
                report += "Data Recovery Wizard / Partition Master\n"
            else:
                report += "可软性植入\n"
            report += f"   - 内容形式: 教程短视频 / YouTube长视频\n"
            report += f"   - 目标平台: YouTube + TikTok同步\n"
            if topic['urls']:
                report += f"   - 参考: {topic['urls'][0]}\n"
            report += "\n"

    if p1_topics:
        report += "### P1 — 本周跟进\n\n"
        for i, topic in enumerate(p1_topics[:5], 1):
            report += f"{i}. **{topic['title']}** (热度: {topic['score']}/10)\n"
            report += f"   - 建议: 结合产品功能做深度内容\n\n"

    if p2_topics:
        report += "### P2 — 长期储备\n\n"
        for i, topic in enumerate(p2_topics[:5], 1):
            report += f"{i}. **{topic['title']}** (热度: {topic['score']}/10)\n"
            report += f"   - 建议: 观察趋势发展\n\n"

    # 数据附录
    report += """---

## 四、数据附录

### 本次搜索关键词
"""
    keywords_seen = set()
    for item in domain_search.get('google', []):
        kw = item.get('keyword', '')
        if kw and kw not in keywords_seen:
            keywords_seen.add(kw)
            report += f"- {kw}\n"

    report += f"""
### 数据来源时间戳
- 报告生成时间: {datetime.now().isoformat()}
- 原始数据文件: {raw_data_path}

---

*本报告由 EaseUS TrendBot 自动生成，数据仅供参考。*
"""

    # 保存报告
    if not output_path:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        output_path = REPORTS_DIR / f"{timestamp}_report.md"

    ensure_dirs()
    REPORTS_DIR.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[成功] 报告已生成: {output_path}")
    return output_path


def main():
    config = load_config()
    if not config:
        print("[错误] 配置文件不存在，请先运行: python config_manager.py init")
        sys.exit(1)

    args = sys.argv[1:]

    # 查找最新的原始数据文件
    raw_data_dir = CONFIG_DIR / "raw_data"
    if not raw_data_dir.exists():
        print("[错误] 未找到原始数据，请先运行 search_executor.py")
        sys.exit(1)

    # 获取最新的搜索数据文件
    data_files = sorted(raw_data_dir.glob("search_*.json"), reverse=True)
    if not data_files:
        print("[错误] 未找到原始数据文件")
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

    # 如果带了--email参数，发送邮件
    if "--email" in args:
        print("[信息] 准备发送邮件...")
        os.system(f'python "{Path(__file__).parent / "email_sender.py"}" --report "{report_path}"')


if __name__ == "__main__":
    main()
