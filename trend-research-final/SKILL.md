---
name: trend-research-final
description: >
  热点话题调研与社交媒体内容选题助手，专精于Windows系统、数据恢复、存储设备领域。
  当用户需要调研热点话题、生成趋势报告、追踪竞争对手内容、获取内容选题建议、
  设置每日/每周热点推送时触发。支持监测Windows更新/故障/存储空间相关热点，
  覆盖Google、YouTube、X(Twitter)、Facebook等平台。
  也适用于EaseUS Data Recovery、EaseUS Partition Master等产品的社媒内容选题。
  用户提到"热点"、"趋势"、"选题"、"竞品"、"对手"、"推送"、"报告"、
  "调研"、"监测"、"Windows"、"数据恢复"、"硬盘"、"存储"等关键词时，
  优先使用此skill。
---

# Trend Research — 热点话题调研 Skill

## 概述

本skill帮助社交媒体运营团队（特别是EaseUS官方账号运营）系统性追踪以下领域的热点话题：

1. **Windows系统热点** — 更新问题、蓝屏故障、系统优化、存储空间管理
2. **数据恢复热点** — 误删恢复、格式化恢复、硬盘损坏、数据丢失场景
3. **存储设备热点** — 移动硬盘、U盘、SSD、NAS、分区管理

核心能力：
- **动态话题提取**：从KOL视频标题中自动聚类话题（TF-IDF + KMeans），不再依赖硬编码关键词
- 跨平台热点搜索（YouTube / Reddit / Google Trends）
- 竞争对手内容追踪与分析
- 热度评估与选题建议（结合EaseUS产品卖点）
- **搜索量曲线**：近7天 Google Trends 搜索热度趋势（pytrends）
- **热点周期预测**：基于话题类型推断热度持续时间（如KB更新蓝屏通常7天修复）
- **YouTube竞争度分析**：近7天相关长视频数量统计与竞争评级
- **选题推荐**：高播放视频标题+主旨、高排名文章标题+主旨各列举3个
- Google Trends 热度佐证（WebSearch 补充真实趋势数据）
- 邮件报告推送
- 定时任务设置（每日 / 每周一）

## 触发场景

以下情况应使用本skill：
- 用户说"调研热点"、"看看最近有什么热点"、"有什么 trending"
- 用户需要"内容选题"、"选题建议"、"写什么内容"
- 用户想"追踪竞争对手"、"分析同行"、"竞品在做什么"
- 用户要求"生成报告"、"推送报告"、"发邮件"
- 用户想"设置每日/每周推送"
- 用户关注 Windows更新/蓝屏/存储空间/数据恢复 等领域动态
- 用户需要为 EaseUS Data Recovery / Partition Master 找宣传切入点

## 依赖要求

- `opencli` 必须已安装且可用（用于YouTube频道抓取和浏览器自动化）
- `firecrawl` 必须已安装且可用（用于网页搜索和全文抓取，替代opencli的Google搜索）
  - 安装：`npm install -g firecrawl-cli`
  - 配置API key：`export FIRECRAWL_API_KEY=your_api_key`
  - 免费额度：每月500 credits
- Python 3.8+（用于报告生成和邮件发送）
- SMTP 邮箱账号（用于报告推送）

## 配置管理

配置文件路径：`~/.config/trend-research/config.json`

### 预设配置（已整合用户提供的账号信息）

首次运行时，会提供以下默认配置模板，用户可修改后保存：

```json
{
  "brand": {
    "name": "EaseUS",
    "youtube": "@Easeus-official",
    "tiktok": "@easeus_official",
    "products": ["EaseUS Data Recovery Wizard", "EaseUS Partition Master"]
  },
  "domains": {
    "windows-system": {
      "description": "Windows系统更新、故障、优化",
      "keywords": [
        "Windows 11 update problems",
        "Windows 10 update stuck",
        "Windows blue screen",
        "Windows not booting",
        "Windows storage full",
        "C drive full Windows",
        "Windows system repair",
        "Windows partition resize",
        "Windows 24H2 issues",
        "KB update problems"
      ]
    },
    "data-recovery": {
      "description": "数据恢复场景和需求",
      "keywords": [
        "recover deleted files",
        "hard drive data recovery",
        "SD card recovery",
        "USB drive not showing files",
        "formatted drive recovery",
        "recycle bin recovery",
        "SSD data recovery",
        "external hard drive corrupted",
        "photo recovery",
        "document recovery"
      ]
    },
    "storage-device": {
      "description": "存储设备和分区管理",
      "keywords": [
        "partition manager",
        "resize partition",
        "merge partitions",
        "SSD vs HDD",
        "external SSD review",
        "NAS setup",
        "USB flash drive repair",
        "disk full solution",
        "move space from D to C",
        "extend C drive"
      ]
    }
  },
  "competitors": {
    "youtube": [
      "@Britec09", "@Jayztwocents", "@UFDTech", "@METAPCs",
      "@cleverfiles", "@ThioJoe", "@ZachsTechTurf", "@TheGrumpySysadmin",
      "@RecoveritDataRecoverySoftware", "@Tenorshare4DDiGDataRecovery",
      "@BrenTech", "@WCT", "@CyberCPU", "@AskYourComputerGuy",
      "@CrownGEEK", "@BrettInTech"
    ],
    "twitter": ["Windows"],
    "facebook": []
  },
  "email": {
    "smtp_server": "",
    "smtp_port": 587,
    "username": "",
    "password": "",
    "to_address": "zhousibo@info.easeus.com.cn, zhouweijiao@info.easeus.com.cn",
    "from_address": "EaseUS TrendBot <trend@easeus.com>"
  },
  "report": {
    "language": "zh",
    "max_hot_topics": 15,
    "competitor_video_limit": 5,
    "enable_email": false
  }
}
```

### 配置初始化流程

1. 检查 `~/.config/trend-research/config.json` 是否存在
2. 如果不存在，展示上述默认配置模板
3. 询问用户是否使用默认配置，或逐项修改（特别是邮箱配置）
4. 保存配置后，后续运行直接读取

## 工作流程

### 标准工作流：生成热点报告

```
1. 检查配置 → 2. 执行搜索 → 3. 竞品追踪 → 4. 分析数据 → 5. 生成报告 → 6. 发送邮件（可选）
```

#### Step 1: 检查配置

运行 `python scripts/config_manager.py check`，确认配置完整。
如缺失，提示用户运行初始化。

#### Step 2: 执行跨平台搜索

使用 `firecrawl` 执行网页搜索（推荐，替代opencli的Google搜索）：

**Firecrawl 搜索（每个领域5个核心关键词，中英双语）：**
```bash
# Windows系统
firecrawl search "Windows 11 update problems 2026" --limit 10 --json -o .firecrawl/win_update.json
firecrawl search "Windows blue screen fix 2026" --sources news --limit 10 --json -o .firecrawl/win_bsod.json

# 数据恢复
firecrawl search "recover deleted files free" --limit 10 --json -o .firecrawl/data_recovery.json
firecrawl search "data recovery software review 2026" --limit 10 --json -o .firecrawl/data_recovery_review.json

# 存储设备
firecrawl search "C drive full how to fix" --limit 10 --json -o .firecrawl/c_drive.json
firecrawl search "best partition manager 2026" --limit 10 --json -o .firecrawl/partition.json
```

**Firecrawl 搜索+全文抓取（获取更完整的内容）：**
```bash
# 带全文抓取的搜索（消耗更多credits，但内容更完整）
firecrawl search "Windows 11 update problems" --scrape --limit 5 --json -o .firecrawl/win_update_scraped.json
```

搜索策略：
- **英文关键词为主**（因为竞品和主流技术内容多为英文，且Google英文搜索结果更丰富）
- 每个领域至少搜索3-5个不同角度的关键词
- 同时覆盖"问题型"（how to fix / recover）和"产品型"（best tool / review）关键词
- 使用 `--sources news` 捕捉突发热点
- 使用 `--tbs qdr:d` 只获取过去一天的内容（用于日报）

**YouTube 搜索（仍使用opencli）：**
```bash
opencli youtube search "Windows update fix" --limit 20 -f yaml
opencli youtube search "data recovery tutorial" --limit 20 -f yaml
opencli youtube search "C drive full" --limit 20 -f yaml
opencli youtube search "partition resize" --limit 20 -f yaml
```

**Twitter/X 搜索（仍使用opencli）：**
```bash
opencli twitter search "Windows update" --filter top --limit 15 -f yaml
opencli twitter search "data recovery" --filter top --limit 15 -f yaml
opencli twitter search "C drive full" --filter top --limit 15 -f yaml
```

**YouTube 搜索：**
```bash
opencli youtube search "Windows update fix" --limit 20 -f yaml
opencli youtube search "data recovery tutorial" --limit 20 -f yaml
opencli youtube search "C drive full" --limit 20 -f yaml
opencli youtube search "partition resize" --limit 20 -f yaml
```

**Twitter/X 搜索：**
```bash
opencli twitter search "Windows update" --filter top --limit 15 -f yaml
opencli twitter search "data recovery" --filter top --limit 15 -f yaml
opencli twitter search "C drive full" --filter top --limit 15 -f yaml
```

**Facebook 搜索（如可用）：**
```bash
opencli facebook search "Windows 11 problems" --limit 10 -f yaml
```

**TikTok 搜索（辅助，opencli支持）：**
```bash
opencli tiktok search "windows tips" --limit 10 -f yaml
opencli tiktok search "data recovery" --limit 10 -f yaml
```

#### Step 3: 追踪竞争对手内容

对于配置中的每个竞争对手：

**YouTube 频道最新视频：**
```bash
opencli youtube channel "@Britec09" --limit 5 -f yaml
opencli youtube channel "@cleverfiles" --limit 5 -f yaml
opencli youtube channel "@RecoveritDataRecoverySoftware" --limit 5 -f yaml
# ... 依此类推
```

**Twitter/X 账号动态：**
```bash
opencli twitter search "from:Windows" --filter top --limit 15 -f yaml
```

**竞品分析重点：**
- 近7天内发布的内容
- 标题中是否包含热点关键词
- 观看量/互动数据表现
- 内容形式（教程、评测、新闻解读）
- 是否涉及数据恢复/分区管理类产品

#### Step 4: 分析数据

使用 `scripts/report_generator.py` 分析收集的数据：

**热度评估维度：**
1. **搜索热度**：Google搜索结果数量、News出现频率
2. **视频热度**：YouTube视频观看量、发布频率
3. **社媒热度**：Twitter互动数（点赞+转发）
4. **时效性**：48小时内权重最高，7天内次之
5. **产品关联度**：与EaseUS产品（数据恢复/分区管理）的关联程度

**热度评分算法（1-10分）：**
- **基础分**（0-3分）：话题在搜索平台出现次数
- **互动分**（0-2分）：YouTube平均观看 / Twitter平均点赞
- **时效分**（0-3分）：24小时内+3分，3天内+2分，7天内+1分
- **新闻分**（0-1分）：Google News中出现+1分
- **产品关联分**（0-1分）：可直接关联EaseUS产品+1分

**选题优先级分类：**
- **P0（立即跟进）**：热度≥8分，且与EaseUS产品强相关
- **P1（本周跟进）**：热度6-7分，或有一定产品关联
- **P2（储备观察）**：热度4-5分，长期趋势

#### Step 5: 生成报告（含话题深度分析 + 数据清洗 + 增强分析）

报告输出格式：Markdown

报告保存路径：`~/.config/trend-reports/YYYY-MM-DD_report.md`

**新增功能（增强分析）：**
每个热门话题自动包含以下四个维度的深度分析：

**A. 搜索量曲线（近7天）**
- 通过 `pytrends` 获取 Google Trends 搜索热度数据
- 输出：日期-分数序列、趋势方向（上升/下降/平稳/波动）、峰值日期
- 以 ASCII 柱状图形式展示在报告中

**B. 热点周期预测**
- 基于话题类型推断典型热度持续时间
- Windows更新问题：~7天（微软通常3-7天发布补丁）
- 蓝屏/崩溃：~14天（驱动级问题1-2周稳定）
- 存储空间/C盘满：~30天（持续性痛点，长期内容布局）
- 数据恢复：~14天（脉冲式热点，误删事件后1-2周爆发）
- SSD/硬件升级：~45天（季节性话题，单轮1-2个月）
- 附带行动建议：紧急/短期/中长期

**C. YouTube竞争度分析（近7天）**
- 搜索相关关键词，统计近7天上线视频
- 区分长视频（≥5分钟）与短视频
- 竞争评级：🔴 激烈（≥20长视频）/ 🟡 中等（10-19）/ 🟢 较低（<10）
- 附带差异化建议

**D. 选题推荐**
- **YouTube高播放视频**：列举3个高播放视频标题 + 内容主旨（解决方案/对比评测/新闻解读/避坑提醒/技巧分享）
- **高排名文章**：列举3个高排名文章标题 + 内容主旨 + 链接

**原有功能：**
- **数据相关性清洗**：每个话题自动过滤与主题无关的视频（相关性阈值0.25）
- **话题深度分析**：每个话题包含：
  - 事件背景（从视频标题推断时间线、关键版本、问题类型）
  - YouTube博主讨论方向（问题诊断/解决方案/教程/对比评测等）
  - 新闻媒体关注角度（基于话题类型推断媒体报道框架）
  - Reddit用户讨论特征（社区讨论模式、用户情绪、高赞建议）

**报告结构：**
```markdown
# 热点话题调研报告 — EaseUS社媒选题参考

> 报告日期：YYYY-MM-DD
> 监测领域：Windows系统 / 数据恢复 / 存储设备
> 数据来源：Google / YouTube / X(Twitter) / Facebook
> 品牌：EaseUS

## 执行摘要
- 热点话题总数：XX个
- P0级选题（立即跟进）：X个
- P1级选题（本周跟进）：X个
- 竞品动态：X个账号有新内容

---

## 一、热点话题排行

### TOP 1: [话题标题]
- **热度评分**: x.x/10
- **优先级**: P0 / P1 / P2
- **来源平台**: Google / YouTube / X
- **相关链接**:
  - [来源1标题](url)
  - [来源2标题](url)
- **热度指标**:
  - Google搜索相关结果：xx条
  - YouTube相关视频：xx个（清洗前xx个，过滤xx个无关视频）
  - Twitter相关推文：xx条（最高互动：xx）
- **时效性**: 24h内 / 3天内 / 7天内
- **EaseUS结合建议**:
  - 产品切入点：Data Recovery / Partition Master
  - 内容角度：...
  - 目标平台：YouTube / TikTok / X
  - 预估受众：...

#### 事件背景
[基于视频标题自动推断：时间线、关键版本/补丁、问题类型]

#### YouTube博主讨论方向
- **问题诊断**: 博主A分析原因...
- **解决方案**: 博主B提供修复步骤...
- **教程实操**: 博主C制作手把手教程...

#### 新闻媒体关注角度
- 科技媒体报道框架...
- 安全影响分析...

#### Reddit用户讨论特征
- r/xxx 社区讨论热点...
- 用户情绪倾向...
- 高赞建议汇总...

#### 搜索量曲线（近7天）
```
**Windows 11 update** — 趋势: 上升 | 均值: 52.3 | 峰值: 78 (2026-05-23)
近4天: ████ █████ ████████ ██████
```

#### 热点周期预测
- **预估热度持续**: 约 7 天
- **模式判断**: 微软通常会在问题曝光后 3-7 天内发布补丁修复，紧急情况下 24-48 小时推出热修复。
- **行动建议**: 🔴 紧急窗口期，建议 48 小时内发布内容抢占流量

#### YouTube 竞争度分析（近7天）
| 指标 | 数值 |
|------|------|
| 相关视频总数 | 35 |
| 长视频（≥5min） | 22 |
| 短视频（<5min） | 13 |
| 平均时长 | 8.5 分钟 |
| 竞争评级 | 🔴 竞争激烈 |

**建议**: 长视频供给饱和，建议差异化角度或 Shorts 形式切入

#### 选题参考
**YouTube 高播放视频参考**
1. **Windows 11 24H2 Update Causing Major Problems - How to Fix** (1.2M views)
   - 内容主旨: 解决方案/教程
   - 时长: 12:34

2. **New Windows 11 Build 26120 Issues and Workarounds** (890K views)
   - 内容主旨: 新闻解读
   - 时长: 8:15

3. **Fix Windows Update Error 0x800f081f in 2 Minutes** (650K views)
   - 内容主旨: 解决方案/教程
   - 时长: 2:05

**高排名文章参考**
1. **Windows 11 24H2 Update Problems and Fixes**
   - 链接: https://...
   - 内容主旨: 解决方案/教程
   - 摘要: Microsoft has released a new update for Windows 11 that causes...

2. **How to Fix Windows 11 Update Stuck at 99%**
   - 链接: https://...
   - 内容主旨: 解决方案/教程
   - 摘要: If your Windows 11 update is stuck, try these steps...

3. **Windows 11 KB5034441 Update Fails to Install**
   - 链接: https://...
   - 内容主旨: 新闻解读
   - 摘要: The latest KB update is causing installation issues for many users...

### TOP 2: ...

---

## 二、竞争对手内容追踪

### @Britec09（901K订阅）
- **最新内容**:
  | 视频标题 | 发布时间 | 观看量 | 与EaseUS关联 |
  |---------|---------|--------|-------------|
  | ... | ... | ... | ... |
- **内容策略观察**:
  - 本周发布频率：X条
  - 热点响应速度：...
  - 可借鉴/差异化点：...

### @RecoveritDataRecoverySoftware（竞品）
- **最新内容**:
  | 视频标题 | 发布时间 | 观看量 | 产品宣传点 |
  |---------|---------|--------|-----------|
  | ... | ... | ... | ... |
- **威胁评估**：...

---

## 三、建议选题角度

### P0 — 立即跟进（48小时内）
1. **[选题标题]**
   - 关联热点：...
   - EaseUS产品结合点：Data Recovery Wizard / Partition Master
   - 内容形式：教程 / 测评 / 短平快tips
   - 目标平台：YouTube + TikTok同步
   - 参考素材：...

### P1 — 本周跟进
...

### P2 — 长期储备
...

---

## 四、数据附录

### 本次搜索关键词
...

### 数据来源时间戳
...
```

#### Step 6: 补充 Google Trends 数据（WebSearch / Firecrawl）

**方案A：使用 Firecrawl（推荐）**
```bash
# 搜索趋势相关文章
firecrawl search "Windows 11 update trend May 2026" --sources news --limit 5 --json -o .firecrawl/trends_win.json
firecrawl search "data recovery trend 2026" --sources news --limit 5 --json -o .firecrawl/trends_data.json
```

**方案B：使用 WebSearch 工具**
由于 `opencli google search` 和 `pytrends` 在自动化环境中常被 Google 反爬虫拦截，Google Trends 热度数据需由 Claude 通过 `WebSearch` 工具补充：

**操作流程：**
1. 读取报告中的动态话题列表（如 "Windows Updates", "Security Updates"）
2. 对每个话题执行 WebSearch：
   ```
   Google Trends "Windows 11 update" May 2026 interest over time
   Google Trends "Intel Arc canceled" May 2026 search interest
   ```
3. 将获取到的趋势佐证（新闻 coverage、行业数据、搜索峰值描述）整理成结构化数据
4. 写入对应 raw_data JSON 文件的 `websearch_trends` 字段
5. 重新运行 `report_generator_v2.py` 生成带趋势佐证的报告

**数据格式：**
```json
{
  "websearch_trends": {
    "Topic Name": {
      "trend_indicator": "高热度/爆发式/持续上升",
      "evidence": ["新闻事实1", "新闻事实2"],
      "sources": ["https://..."]
    }
  }
}
```

#### Step 7: 发送邮件（如果启用）

使用 `scripts/email_sender.py` 发送报告：

```bash
python scripts/email_sender.py --report ~/.config/trend-reports/YYYY-MM-DD_report.md
```

邮件主题：`[EaseUS热点日报] YYYY-MM-DD — XX个高价值选题待跟进`

邮件正文：报告摘要 + Markdown报告附件或内嵌

### 定时推送工作流

用户要求设置定时任务时：

**每日推送：**
- 使用 `CronCreate` 创建每天运行的任务
- Cron表达式：`7 9 * * *`（每天上午9:07，避开整点）
- 执行命令：运行完整工作流并发送邮件
- 报告标题含"[EaseUS热点日报]"

**每周推送（周一）：**
- 使用 `CronCreate` 创建每周一运行的任务
- Cron表达式：`7 9 * * 1`（每周一上午9:07）
- 报告标题含"[EaseUS热点周报]"
- 增加"本周趋势总结"和"下周预判"板块

**查看/取消定时任务：**
- 使用 `CronList` 列出任务
- 使用 `CronDelete` 取消指定任务

## 命令使用参考

### 用户常用指令

| 用户指令 | skill响应 |
|---------|----------|
| "生成今日热点报告" | 执行完整工作流，生成报告并展示 |
| "发送热点报告到邮箱" | 生成报告 + 发送邮件 |
| "设置每日热点推送" | 配置CronCreate定时任务 |
| "设置每周一热点推送" | 配置CronCreate每周一任务 |
| "查看竞争对手动态" | 仅执行Step 3（竞品追踪） |
| "更新配置" | 重新运行配置初始化 |
| "只搜Windows更新热点" | 指定领域，缩小搜索范围 |
| "找Partition Master相关热点" | 围绕特定产品搜索 |

### 脚本命令参考

```bash
# 配置管理
python scripts/config_manager.py init      # 交互式初始化
python scripts/config_manager.py check     # 检查配置完整性
python scripts/config_manager.py show      # 显示当前配置（脱敏）

# 搜索执行（YouTube KOL抓取 + 动态话题聚类）
python scripts/search_executor_v3.py                 # 完整流程

# 话题提取（独立测试动态聚类）
python scripts/topic_extractor.py                    # 测试聚类效果

# Google Trends（需环境支持 pytrends）
python scripts/trends_fetcher.py                     # 测试 Trends 获取

# 报告生成
python scripts/report_generator_v2.py                # 生成Markdown报告
python scripts/export_word.py                        # 导出Word文档
python scripts/report_generator_v2.py --email        # 生成后发送邮件

# 邮件发送
python scripts/email_sender.py --report ./report.md

# 增强分析（独立测试）
python scripts/enhanced_analytics.py "Windows 11 update" update windows
```

## 脚本说明

- **`scripts/config_manager.py`** — 配置CRUD，支持交互式初始化，内置默认模板
- **`scripts/search_executor_v3.py`** — YouTube KOL抓取 + 动态话题聚类 + Reddit搜索
- **`scripts/topic_extractor.py`** — 动态话题提取（TF-IDF + KMeans），从视频标题自动聚类
- **`scripts/trends_fetcher.py`** — Google Trends 数据获取（pytrends），需配合代理或本地环境使用
- **`scripts/report_generator_v2.py`** — 读取搜索数据，生成带KOL提及/结合度/差异化建议的Markdown报告（已集成增强分析）
- **`scripts/topic_analyzer.py`** — 话题深度分析（事件背景、YouTube/新闻/Reddit多维度讨论、数据相关性清洗）
- **`scripts/enhanced_analytics.py`** — **增强分析模块**：搜索量曲线 + 热点周期预测 + YouTube竞争度 + 选题推荐
- **`scripts/export_word.py`** — 将Markdown报告导出为Word文档
- **`scripts/email_sender.py`** — SMTP邮件发送，支持HTML格式和附件
- **`references/report_template.md`** — 报告模板和示例

## 重要提示

1. **首次使用必须先初始化配置**，邮箱配置留空则禁用邮件推送
2. **firecrawl需要API key**，免费额度500 credits/月，超出需付费
3. **opencli需要浏览器自动化**，确保系统有可用的Chrome/Edge浏览器
4. **部分平台可能需要登录**（Twitter/X、Facebook），如果opencli无法获取数据：
   - 回退到 `firecrawl search`
   - 或先用 `opencli browser init` 完成登录
5. **Facebook数据获取经常受限**，优先依赖firecrawl/Google/YouTube/Twitter数据
6. **热度评分是综合估算**，用于横向对比和优先级排序，不是精确数据
7. **TikTok支持有限**，opencli tiktok主要用于辅助参考
8. **尊重平台规则**，搜索频率不宜过高，避免触发反爬虫
9. **敏感信息保护**，邮箱密码明文存储在本地配置文件，注意文件权限
10. **数据清洗说明**：报告中的视频数据已自动过滤与主题无关的内容（相关性阈值0.25），清洗统计在报告中展示

## 故障排除

| 问题 | 解决方案 |
|-----|---------|
| opencli 命令未找到 | 确认 opencli 已安装并添加到 PATH |
| firecrawl 命令未找到 | 运行 `npm install -g firecrawl-cli` 安装 |
| firecrawl API key 无效 | 检查 `FIRECRAWL_API_KEY` 环境变量是否设置 |
| firecrawl credits 不足 | 免费额度500/月，超出需升级或等待下月重置 |
| 浏览器启动失败 | 检查Chrome/Edge是否安装，运行 `opencli doctor` 诊断 |
| Twitter/X 搜索无结果 | 可能需登录，改用 firecrawl search 备选 |
| YouTube频道信息获取失败 | 检查频道handle是否正确（需包含@） |
| 邮件发送失败 | 检查SMTP配置，Gmail需使用应用专用密码 |
| 报告为空 | 检查关键词配置，尝试扩大搜索范围 |
| Facebook数据获取失败 | Facebook限制严格，可忽略或改用 firecrawl |
| 竞品视频数据不全 | 频道可能设置了隐私，跳过即可 |
