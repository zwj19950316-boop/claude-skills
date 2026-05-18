---
name: game-voice-content-inspiration
description: >
  Discover trending game/entertainment IP characters for voice changer content creation.
  Use this skill whenever the user wants to find popular game characters for voice trolling,
  voice changer videos, character impression content, or gaming content ideas.
  Also handles定向事件交叉调研: when user wants to combine a real-world event (World Cup,
  Olympics, holidays, movie releases) with gaming content to find sound/voice opportunities.
  Triggers on: voice troll ideas, game character voices, popular characters for voice changer,
  trending game characters, voice impression content, gaming voice content inspiration,
  Fortnite/Valorant/Roblox/CS character voices, new game character trends,
  event gaming crossover, World Cup gaming content, holiday gaming sounds,
  movie game collaboration voices, seasonal gaming content ideas.
  Always use this skill when the user mentions voice changer, voice troll, character voices,
  game character impressions, wants content ideas for gaming voice videos,
  or wants to research gaming content tied to a specific event or theme.
---

# Game Voice Content Inspiration

Discover trending game and entertainment IP characters for voice changer content creation.

## Purpose

This skill helps content creators find the most promising game characters for voice trolling,
voice changer videos, and character impression content. It analyzes:
- Current trending games (Fortnite, Valorant, Roblox, CS, etc.)
- Newly released popular games
- Character popularity on YouTube voice troll content
- Content format recommendations (voice troll, sound effect intro, full tutorial)

## 工作模式

本skill支持两种工作模式：

### 模式A: 常规热门角色发现（默认）
按标准流程发现近期热门游戏角色，见下方Workflow。

### 模式B: 定向事件交叉调研（当用户提到特定事件/主题时触发）
当用户提到想结合某个事件（如世界杯、奥运会、春节、电影上映等）做调研时，使用此模式。

**定向调研流程：**
1. 分析事件核心元素（声音、口号、人物、氛围）
2. 搜索游戏与该事件的联动/交叉内容
3. 识别具有事件相关性的游戏角色或音效
4. 评估内容潜力（事件热度 + 游戏受众 + 声音辨识度）
5. 给出内容制作建议

**示例事件交叉点：**
- 世界杯 → 足球游戏角色、球场氛围音效、解说员声音
- 春节 → 中国风游戏角色、鞭炮音效、红色主题皮肤
- 电影上映 → 联动角色、经典台词、主题音效

---

## Workflow

### Step 1: Identify Trending Games

Search for currently trending games that are popular for voice content:

```
Search queries to use (mix Chinese and English for better results):
- "trending games 2025 voice chat" "popular games voice trolling"
- "Fortnite new characters 2025" "Valorant new agents 2025"
- "new popular games 2025" "trending multiplayer games"
- "Roblox popular games 2025" "CS2 new content 2025"
- "游戏变声器" "voice troll 热门" "游戏角色配音"
```

Focus on games released or updated within the last month (近30天). Always use current year (2026) when searching for trending content.

### Step 2: Find Popular Characters

For each trending game, identify characters that:
- Have distinct voices or personalities
- Are recognizable to players
- Have potential for humorous or entertaining voice impressions
- Are currently being discussed in the community

### Step 3: Analyze YouTube Voice Troll Mentions

Search YouTube for voice troll content featuring these characters:

```
Search queries:
- "[game name] [character] voice troll"
- "[game name] voice changer trolling"
- "[character name] impression gaming"
- "voice troll [game name] 2025"
```

Count mentions and assess engagement (views, recent uploads).

### Step 4: Rank by Potential

Create a ranked list considering (所有分析用中文输出):
1. **YouTube提及频率** (近30天voice troll视频数量)
2. **游戏热度** (当前玩家数量和增长趋势)
3. **角色声音辨识度** (独特语音/个性，1-10分)
4. **内容缺口** (供不应求/饱和/小众)
5. **时效性** (近30天更新的角色获得额外加分)

### Step 5: Content Format Recommendation

For each top character, recommend the best content format:

| 内容格式 | 推荐场景 |
|----------|----------|
| **Voice Troll（语音恶搞）** | 角色有标志性语音台词、鲜明个性、适合多人游戏 |
| **音效介绍** | 角色有标志性音效/技能、适合短视频内容 |
| **完整教程** | 角色操作复杂有学习曲线、有教育价值、有忠实玩家群体 |

## Output Format

**ALWAYS output in Chinese (中文)** and generate a Word document (.docx) using the bundled script.

### Step 1: Write Markdown Report (in Chinese)

First, compose the full report in Chinese using this structure:

```markdown
# 游戏变声器内容灵感报告

## 执行摘要
- 前3名角色机会
- 优先推荐的内容格式

## 热门游戏分析
### [游戏名称]
- 发布/更新日期: [日期]
- 当前热度: [高/中/低] + 原因
- 值得关注的新角色: [列表]

## 角色热度排名

### 1. [角色名称] ([游戏])
- **YouTube Voice Troll提及度**: [数量/估算]
- **声音辨识度评分**: [1-10]
- **内容缺口**: [饱和/供不应求/小众]
- **推荐格式**: [Voice Troll / 音效介绍 / 完整教程]
- **原因**: [说明]
- **内容创意建议**: [具体想法]

### 2. [角色名称] ([游戏])
...

## 内容策略建议

### 立即机会（本周）
- [角色]: [具体内容创意]

### 短期趋势（本月）
- [角色]: [具体内容创意]

### 新兴机会（观察名单）
- [游戏/角色]: [可能爆火的原因]
```

### Step 2: Generate Word Document

After writing the markdown report, save it to a temporary .md file and run the script:

```bash
python scripts/generate_report.py report.md "游戏变声器内容灵感报告_YYYYMMDD.docx"
```

For定向事件交叉调研, use a filename reflecting the event:
```bash
python scripts/generate_report.py report.md "世界杯游戏音效潜力报告_YYYYMMDD.docx"
```

**Important:**
- The script auto-installs `python-docx` if missing
- Output filename should include date for organization
- Present the .docx file path to the user when complete
- All text in the Word document will be in Chinese with Microsoft YaHei font

---

## 定向事件交叉调研输出格式

当用户要求结合特定事件（如世界杯、奥运会、春节、电影等）时，使用以下结构：

```markdown
# [事件名称] x 游戏变声器内容潜力报告

## 执行摘要
- 事件核心声音元素
- 与游戏受众的交叉机会点
- 前3名音效/角色机会

## 事件分析
### [事件名称]核心元素
- **时间**: [日期]
- **热度**: [高/中/低]
- **标志性声音**: [口号、歌曲、音效、人物声音]
- **受众情绪**: [兴奋/怀旧/爱国/欢乐]

## 游戏交叉点分析
### [游戏名称]
- **联动状态**: [已有联动/潜在机会/无关联]
- **相关角色/皮肤**: [列表]
- **相关音效**: [列表]
- **内容潜力**: [高/中/低]

## 音效/角色潜力排名

### 1. [音效/角色名称] ([游戏/来源])
- **事件关联度**: [1-10]
- **游戏受众匹配度**: [1-10]
- **声音辨识度**: [1-10]
- **YouTube现有内容量**: [多/中/少/无]
- **推荐格式**: [Voice Troll / 音效介绍 / 完整教程 / 氛围音效]
- **原因**: [说明]
- **内容创意建议**: [具体想法]

## 内容策略建议

### 立即机会（事件期间）
- [音效/角色]: [具体内容创意]

### 短期趋势（事件前后1个月）
- [音效/角色]: [具体内容创意]

### 长尾机会（事件后）
- [音效/角色]: [如何延续热度]
```

## 研究指南

1. **优先时效性**: 近30天更新的游戏角色获得+2辨识度加分
2. **检查上传日期**: 关注近1个月内上传的YouTube内容以确保趋势准确性
3. **交叉验证**: Twitch/Reddit上热门但YouTube上尚未大量出现的角色 = 高机会
4. **避免过度饱和**: 如果某角色本月已有50+个voice troll视频，标记为"饱和"
5. **考虑全球吸引力**: 在多个地区流行的游戏角色潜力更高

## Example

**User**: "帮我找一些适合做变声器内容的游戏角色，最近有什么热门的"

**Output Process**:
1. 先用中文撰写完整markdown报告
2. 运行 `python scripts/generate_report.py report.md "游戏变声器内容灵感报告_20250512.docx"`
3. 向用户展示生成的Word文档路径

**常规调研示例**:
```markdown
# 游戏变声器内容灵感报告

## 执行摘要
- 最佳机会: [新Fortnite角色] - 仅3个voice troll视频，辨识度高
- 推荐格式: Voice Troll（多人友好， recognizable voice lines）

## 热门游戏分析
### Fortnite (第六章第二赛季)
- 发布/更新日期: 2025年3月
- 当前热度: 非常高
- 值得关注的新角色: [角色A], [角色B]

## 角色热度排名
### 1. [角色A] (Fortnite)
- **YouTube Voice Troll提及度**: 3个视频（近30天）
- **声音辨识度评分**: 9/10（独特口音和口头禅）
- **内容缺口**: 供不应求
- **推荐格式**: Voice Troll
- **原因**: 新角色，声音独特，竞争少
- **内容创意建议**: "用[角色A]声音在排位赛里trolling小队"
```

**定向事件交叉调研示例**:
```markdown
# 世界杯 x 游戏变声器内容潜力报告

## 执行摘要
- 标志性声音: 球场欢呼、解说员激情解说、国歌、Waka Waka等主题曲
- 最佳机会: FIFA游戏解说员声音 + Fortnite足球皮肤

## 事件分析
### 世界杯核心元素
- **时间**: 2026年6-7月
- **热度**: 极高
- **标志性声音**: 球场欢呼声、解说员GOAL喊声、呜呜祖拉、主题曲
- **受众情绪**: 兴奋、爱国、集体狂欢

## 游戏交叉点分析
### FIFA 26 / EA FC 26
- **联动状态**: 天然关联
- **相关角色**: 知名解说员（如Martin Tyler经典声音）
- **相关音效**: 进球欢呼、裁判哨声、点球紧张氛围
- **内容潜力**: 极高

## 音效潜力排名
### 1. 解说员GOAL喊声 (EA FC 26)
- **事件关联度**: 10/10
- **游戏受众匹配度**: 9/10
- **声音辨识度**: 10/10
- **YouTube现有内容量**: 少
- **推荐格式**: 音效介绍
- **原因**: 世界杯期间"GOAL!"是最具感染力的声音，游戏解说员声音可被提取用于击杀集锦
- **内容创意建议**: "把FPS游戏击杀做成世界杯进球集锦风格，用EA FC解说员声音配音"
```

## Tools to Use

- Use `firecrawl-search` skill for web research on trending games and YouTube content
- Use `WebSearch` tool for quick fact-checking on release dates and character info
- Use `WebFetch` to extract detailed content from specific YouTube videos or gaming news sites

## Notes

- **ALWAYS output in Chinese (中文)** - all reports, analysis, and recommendations must be in Chinese
- Always verify game update dates - stale information leads to missed opportunities
- If a character has no voice lines, recommend Sound Effect Intro format instead
- Consider the user's platform (YouTube Shorts vs long-form) when recommending formats
- Voice troll content performs best with characters that have: catchphrases, accents, or emotional range
- Game names and character names can remain in English (e.g., Fortnite, Valorant), but all analysis and descriptions must be in Chinese
- The Word document uses Microsoft YaHei font for proper Chinese text rendering
