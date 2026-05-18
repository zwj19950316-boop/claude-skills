---
name: youtube-shorts-windows
description: Generate YouTube Shorts scripts about Windows 11 updates, issues, bugs, and how-to topics. Use this skill whenever the user wants to create a YouTube Shorts script about Windows 11 news, Windows updates, Windows bugs/issues, PC troubleshooting, or Windows how-to content. Also trigger when the user mentions "Shorts script", "YouTube Shorts", "Windows 11 content", "Windows update news", or wants to produce short-form Windows/PC content in the style of tech news channels.
---

# YouTube Shorts Windows Script Writer

Generate high-performing YouTube Shorts scripts about Windows 11 updates, issues, and how-to topics.

## Content Analysis

Based on successful video patterns, the script must follow this exact 4-section structure:

### Section 1: Hook (0-3 seconds, ~20-30 words)
- Start with a time reference: "A couple of days ago", "Last week", "Recently"
- State the Windows update KB number or feature name
- Immediately deliver the threat/pain point
- Pattern: "[Time], Windows 11 [released update KBxxxx / got a new feature called X], and it could [negative impact] / [positive benefit]."

### Section 2: Problem/Feature Details (3-15 seconds, ~40-60 words)
- Describe specific symptoms or mechanics
- Include technical details (file sizes, percentages, hardware models)
- Mention affected brands/models when relevant
- Use vivid, concrete language: "pixelated screen", "blue screen of death", "literally disappear"
- Pattern: "Reports show that after [installing this / enabling this], [specific symptom]. [Additional detail with numbers/brands]."

### Section 3: Solution/Action (15-45 seconds, ~50-80 words)
- Provide clear step-by-step fix or workaround
- OR explain the feature mechanics with context
- Include specific UI paths: "go to Settings > Windows Update"
- OR mention alternative tools (e.g., EaseUS Partition Master) with brief usage steps
- For how-to content: numbered steps, specific button names
- Pattern: "If [condition], you can try [action]. First, [step 1]. Then [step 2]. Finally [step 3]."

### Section 4: CTA (last 2 seconds, ~5 words)
- Always end with: "Follow for more."

## Tone and Style Rules

1. **Voice**: Direct, urgent, conversational. Speak TO the viewer (second person).
2. **Sentence style**: Short, punchy sentences. Mix of statement + implication.
3. **Key vocabulary to use naturally**:
   - "literally" (for emphasis on severity)
   - "anyway" (transition to solution)
   - "well" (softening a hard truth)
   - "some" / "certain" (when discussing affected users)
   - "so far" (to indicate ongoing situation)
   - "quoting" (when citing performance numbers)
4. **Avoid**: Overly formal language, long compound sentences, speculative language without attribution ("maybe", "perhaps"), excessive technical jargon without explanation.
5. **Music cues**: Mark natural pause points with `[music]` where a beat drop or transition would enhance engagement. Typically 1-2 per script, placed after key statements.

## Content Types

### Type A: Windows Update Disaster (Videos 1 & 2)
- Focus: KB update causing hardware/software issues
- Hook: Update number + disaster outcome
- Body: Specific symptoms + affected hardware brands
- Solution: Uninstall path OR third-party tool workaround

### Type B: Windows Feature News (Videos 3 & 4)
- Focus: New Windows feature or performance improvement
- Hook: Rhetorical question or provocative statement + feature name
- Body: How it works + performance numbers + controversy/context
- Solution: Not applicable; provide balanced perspective instead

### Type C: How-To/Troubleshooting
- Focus: Solving a specific Windows problem
- Hook: The frustrating problem stated directly
- Body: Root cause (brief) + step-by-step fix
- Solution: Clear numbered steps with exact UI paths

## Input Parameters

The user should provide:
- **topic**: The Windows 11 topic (e.g., "KB5063878 SSD corruption", "new low-latency profile feature")
- **content_type**: A (disaster), B (feature news), or C (how-to)
- **key_details**: Specific technical details, affected hardware, symptoms, or steps
- **angle** (optional): The hook angle - threat, benefit, or curiosity

## Research Step

Before writing, gather current information:
1. Search for the specific Windows update KB number or feature name to verify details
2. Identify affected hardware models, specific error messages, or performance metrics
3. Find the exact uninstall path or solution steps from Microsoft or reputable sources
4. Note any official Microsoft responses or patch timelines
5. Search Google Trends or social media (Reddit, X/Twitter, Microsoft forums) for discussion volume and sentiment
6. Identify related keywords and search trends that could inform the title and SEO

## Output Format

Produce a comprehensive content brief in this format:

```
# [Title - SEO optimized, under 60 characters]

## Topic Analysis

**Type**: [A/B/C]
**Estimated Duration**: [XX] seconds
**Word Count**: [XXX] words

### Topic Summary
[2-3 sentences explaining what this topic is about and why it matters to Windows 11 users right now]

### Why This Matters
[Analysis of the user pain point or interest driver. Who is affected? How severe is the issue? Is there a workaround or fix available?]

### Content Angle Recommendation
[Suggest the best angle based on research: threat/urgency, curiosity, benefit, controversy, or how-to. Explain why this angle works for this specific topic.]

---

## Market Intelligence

### Search Trend Analysis
**Primary Keywords**: [main keyword, e.g., "Windows 11 KB5063878"]
**Related Trending Queries**: [3-5 related searches people are actively looking for]
**Search Intent**: [Informational/Transactional/Problem-solving - what does the searcher want?]
**Trend Direction**: [Rising/Stable/Peaking/Fading - is interest growing or dying down?]

### Social Media Discussion Summary
**Reddit**: [Key threads and sentiment from r/Windows11, r/pcmasterrace, r/techsupport]
**X/Twitter**: [Notable tweets, influencer mentions, hashtag volume]
**Microsoft Forums**: [Official response status, user complaint volume]
**YouTube**: [Are other creators already covering this? What's the gap you can fill?]

**Overall Sentiment**: [Negative/Concerned/Positive/Curious - what is the emotional temperature?]
**Discussion Volume**: [High/Medium/Low - how much buzz is there?]
**Audience Urgency**: [High/Medium/Low - do people need an answer NOW or is this evergreen?]

### Competitive Landscape
[Are other tech channels covering this? What angle are they taking? What's missing from their coverage that you can provide?]

### Content Opportunity Score
**Timeliness**: [1-10] - How fresh is this topic?
**Search Demand**: [1-10] - Are people actively searching for this?
**Emotional Hook**: [1-10] - Does this trigger strong emotions (fear, frustration, curiosity)?
**Ease of Production**: [1-10] - How easy is this to research and script?
**Overall Score**: [1-10] - Should you prioritize this?

---

## Script

[Script text with [music] cues inserted, following the 4-section structure]

---

## Visual Notes
- [0-3s]: [What shows on screen]
- [3-15s]: [What shows on screen]
- [15-45s]: [What shows on screen]
- [45-60s]: [What shows on screen]

---

## Sources
- [Link or source description]

---

## Recommended Next Steps
[Suggest follow-up content ideas, related topics, or how to time the publication for maximum impact]
```

## Examples

### Example 1: Type A - Update Disaster
**Input**: KB5063878, SSDs disappearing/corrupting during heavy writes, Fison controllers affected including Corsair MP600 and SanDisk Extreme Pro

**Output**:
```
# Windows 11 Update KB5063878 Is Destroying SSDs

**Type**: A
**Estimated Duration**: 50 seconds
**Word Count**: 128 words

---

A couple of days ago, Windows 11 released update KB5063878, and it could be a disaster for your SSD. Reports show that after installing this update, some SSDs literally disappear or even get corrupted during heavy file transfers, especially if you're writing more than 50 GB, and the drive is already about 60% full. Most of the cases so far are on SSDs with Fison controllers. That includes the Corsair MP600 and the SanDisk Extreme Pro, but some other discs are also affected. Anyway, if this has you concerned and the update's already on your system, you can try going to Settings and Windows Update. Here, select update history and uninstall updates. Then you can find KB5063878 and hit uninstall to roll back. If you haven't updated yet, you may consider pausing Windows Update for a while until Microsoft releases a fixed patch. Follow for more.

---

**Visual Notes**:
- [0-3s]: Windows Update screen showing KB5063878
- [3-15s]: SSD corruption warning screens, file transfer failure
- [15-45s]: Settings > Windows Update > Update history > Uninstall updates path
- [45-50s]: Pause updates toggle

**Sources**:
- Windows 11 KB5063878 release notes
- User reports on Reddit/MS forums
```

### Example 2: Type B - Feature News
**Input**: Windows 11 low-latency profile, CPU burst for 1-3 seconds, 40-70% app launch speed improvement, comparison to Apple/Linux

**Output**:
```
# Windows 11's New "Low-Latency Profile" Is Just CPU Cheating

**Type**: B
**Estimated Duration**: 55 seconds
**Word Count**: 142 words

---

Why should Microsoft make Windows better for you? Your computer just needs to work harder. The latest update to get Windows 11 faster is called low-latency profile, and the non-door folks are saying that it's a big improvement, especially for lower-end systems. Its whole goal is to get apps to launch way faster. Not by making the apps more efficient, but by bursting your CPU to maximum speed for 1 to 3 seconds. They're quoting between 40 and 70% speed increases for app and start menu launch times. And while some call this move lazy development and cheating, Microsoft says, "Nah. This is how modern systems make apps feel fast. Apple does it, and you love it. And Linux isn't any better. They don't have to boost your chip because it does less work and integrates fewer services." Now, thankfully, none of this means that Windows isn't still getting efficiency enhancements. They're still working to make the operating system lighter overall, but they're starting with quick, cheap wins first. If your PC is slow because it's not being fully utilized, well, then they're going to make sure it's running at its maximum potential first. Follow for more.

---

**Visual Notes**:
- [0-3s]: Slow PC vs fast PC split screen
- [3-15s]: Task Manager showing CPU burst to 100%
- [15-45s]: App launch speed comparison, Apple/Linux logos
- [45-55s]: Windows 11 logo with "quick wins" text

**Sources**:
- Microsoft Windows Insider Blog
- Performance benchmark reports
```

### Example 3: Type A with Third-Party Tool
**Input**: KB5083769, boot loops on HP/Dell, pixelated screen then BSOD, recovery fails, EaseUS Partition Master boot repair tool

**Output**:
```
# Windows 11 Update KB5083769 Causes Boot Loops

**Type**: A
**Estimated Duration**: 52 seconds
**Word Count**: 135 words

---

Last week Windows 11 released the update KB5083769, [music] and it can cause boot loops on some PCs. Reports show that after installing this update, some users see a pixelated screen followed by a blue screen of death crash and a message suggesting Windows needs to be recovered, but after attempting recovery, it still returns to the same issue and puts you in an endless loop. This issue has mainly popped up on HP and Dell computers so [music] far. If you're facing this problem, besides uninstalling the KB update or reinstalling the system, you can try EaseUS Partition Master's blue screen repair tool. First, insert a USB drive into another working computer and create bootable media with it. Then plug it into the affected PC and go to BIOS. Change the boot order to boot your PC from the USB. Once launched, open the tool, go to the toolkit, and find boot repair [music] section. There you'll get a blue screen error report and can start the repair process. Follow for more. [music]

---

**Visual Notes**:
- [0-3s]: BSOD screen with KB5083769 text overlay
- [3-15s]: Pixelated screen animation, HP/Dell logos
- [15-45s]: EaseUS Partition Master interface, bootable USB creation steps
- [45-52s]: Boot repair process running

**Sources**:
- Windows 11 KB5083769 release notes
- EaseUS support documentation
```

## Writing Guidelines

1. Always verify KB numbers and technical details through search before writing
2. Keep scripts between 120-150 words for 45-60 second Shorts
3. Use [music] cues at emotional peaks or transition points (1-2 per script max)
4. Include specific numbers, percentages, and brand names when available
5. For Type A, always provide BOTH the uninstall path AND the "pause updates" advice
6. For Type B, present controversy fairly but keep the channel's skeptical tone
7. For Type C, number the steps and use exact UI element names
8. Never exceed 60 seconds in spoken duration - aim for 50-55 seconds
