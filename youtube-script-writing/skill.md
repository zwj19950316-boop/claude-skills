---
name: youtube-script-writing
description: Generate high-quality YouTube how-to tutorial scripts with SEO-optimized titles, professional hooks, and structured content. Supports EaseUS software tutorials, data recovery guides, and tech content.
---

# YouTube Script Writing Skill

## STEP 0 — Read Before Doing Anything

Before generating any content, read these files:
- `product-knowledge.md` — find the section for the user-specified product only
- `cover-design-specs.md` — thumbnail prompt requirements

Do not skip this step.

---

## STEP 1 — Analyze Input

Collect from user:
- **Topic** (e.g. "SD card data recovery on Mac")
- **Keywords** (3–5 core terms)
- **Duration** (e.g. "5 minutes")
- **Product** (e.g. "EaseUS Data Recovery Wizard")

Then decide:
- **Has free method?** → Use Structure A
- **No viable free method?** → Use Structure B
- **Hook template?** → Match from rules below

---

## STEP 2 — Generate Output

### CRITICAL RULE: Text-First Approval Process
**ALL scripts must be generated as plain text first and shown to the user for approval BEFORE creating any file.**

1. Generate complete script content in plain text format
2. Present to user for review and approval
3. Only after user confirms "approved" or "looks good" → proceed to export as `.docx` or `.md`
4. Never skip this step - even for repeat requests

### Output all content in **English only**.

### Output Checklist

### Output Checklist
- [ ] 3 SEO-optimized titles
- [ ] Video outline with timing
- [ ] Full script (mixed mode — see below)
- [ ] 3 thumbnail DALL-E prompts
- [ ] SEO tags + description suggestions

---

## VIDEO STRUCTURE

**Structure A — Has free method:**
```
[Hook] → [Free Method(s)] → [Rehook] → [Product Intro] → [Tutorial Steps] → [Result] → [CTA]
```

**Structure B — No free method:**
```
[Hook] → [Problem Education] → [Product Intro] → [Tutorial Steps] → [Result] → [CTA]
```

### Free Method Rules (Structure A only)
- Present free method first — acknowledge it works
- State its specific limitation clearly
- Define the boundary: "if your situation is X, this won't work"
- Do NOT include backup-dependent methods (File History, Time Machine) for accidental deletion scenarios — users in that situation don't have a backup

---

## SCRIPT RULES

### Style
- Open with the viewer's problem as a situation, not a question
- Cut all filler: "don't panic", "great news", "let's dive in", "this is super important"
- Use "So" to transition between sections
- Short sentences. One idea per sentence.
- Use numbers, not vague words ("3 ways" not "several ways")
- Close steps with "And that's it" or "pretty quick and easy"

### Tone
- Calm and direct. Never hyped or emotional.
- First-person walkthrough, not lecture-style
- Professional but conversational

---

## HOOK (≤15 seconds | ≤35 words)

Must include:
1. Problem identification (2–3s)
2. Solution preview (3–5s)
3. Value promise (5–7s)

No backstory. No "welcome back". No filler.

**Template A — Problem-Direct:**
> "[Problem]? Here are [N] ways to [fix it]—starting completely free."
> Example: "Lost your GoPro footage? Here are 3 ways to get it back—starting completely free."

**Template B — Emotional Hook:**
> "That moment when [problem]? I've been there. Here's exactly how to [fix it]."

**Template C — Number Promise:**
> "[N] ways to [fix problem]—starting with completely free options."

**Matching rule:**
- "how to / fix / recover" → Template A
- Emotional loss (memories, important files) → Template B
- Multiple methods available → Template C

**Don'ts:**
- ❌ "Last summer, I was on a trip to Hawaii..."
- ❌ "GoPro cameras are great for action sports, but sometimes..."
- ❌ "Before we get started, make sure to subscribe..."

---

## PRODUCT INTRODUCTION (20–30 seconds total)

### Order (must follow exactly):
1. Present free method → acknowledge it works
2. State its specific limitation
3. Define the boundary case
4. Introduce product as the only viable option
5. Name the product

**❌ Wrong:** "Today I'm going to show you how to use DRW to recover your files."
**✅ Right:** "The built-in method works for simple cases, but it can't recover files from a formatted card. If that's your situation, the only option that actually works is a dedicated recovery tool. I'll be using DRW today."

### Structure (7 parts, total 20–30s):
1. **承接 Rehook** (2–3s) — 1 sentence, directly respond to Rehook
2. **Technical truth** (6–8s) — 1–2 sentences, explain why free method fails
3. **Consequence** (4–6s) — 1 sentence, what the user actually experiences
4. **Product intro** (5–6s) — 1 sentence, logical conclusion not recommendation
5. **One core differentiator** (4–5s) — 1 sentence, only the one that solves THIS problem
6. **Scope** (2–3s) — 1 sentence, use "regardless of" or "works on both"
7. **Transition** (2s) — "So here's how to..."

### Template A — Technical Limitation (use when free method exists but has limits):
```
"But here's the thing—[technical reason in one sentence].
[Consequence with visual detail].
It's for this specific reason that we're using [Product] today.
[One core capability that directly addresses the technical problem].
[Scope — regardless of / works on both].
So here's how to [transition]."
```

### Template B — Problem Education (use when no free method):
```
"[Explain problem in plain language].
[Obvious fix] is the obvious fix, but [specific consequence].
Which is why the right order is [correct sequence].
The most important thing: [one key rule].
The way we're going to do this is by using [Product].
[Product] [one core capability].
So here's how to [transition]."
```

### ❌ Don'ts:
- ❌ Feature list: "EaseUS supports 1000+ file types, HDD/SSD/USB..."
- ❌ Emotional: "This amazing software will save your precious memories!"
- ❌ No logical setup: "So let's use EaseUS Data Recovery Wizard."
- ❌ More than 1 differentiator

### ✅ Best Practices:
- Technical truth must be specific: ✅ "the file system is damaged, so tools that rely on it find nothing" ❌ "free tools have limitations"
- Consequence must be visual: ✅ "you end up with fragmented files that won't play" ❌ "the recovery might not work"
- Product intro = logical conclusion: ✅ "It's for this reason we're using EaseUS" ❌ "I recommend EaseUS"
- One differentiator matched to scenario:
  - SD card formatted/corrupted → deep scan / raw sector read
  - RAW disk / drive error → bypass file system errors

---

## TUTORIAL STEPS

Every step = **Action + Result + Advantage**

Never describe the interface. Never describe the process. Describe what the user will see and what it means.

**Template:**
> "When you [action], you'll see [specific screen change]. This means [direct benefit / risk reduced / time saved]."

**Result language:**
- ✅ "you can confirm which files are fully intact"
- ✅ "this cuts down your search time significantly"
- ❌ "the scan completes successfully"
- ❌ "you can see the files"

---

## REHOOK (every 60–90 seconds)

**3–5 min video timing:**
- 1:30 — First Rehook (confirm value)
- 3:00 — Second Rehook (prevent drop-off)
- 4:30 — Final Rehook (guide to end)

**Rehook is dynamic, not templated. Choose one approach per Rehook:**
1. **Progress recap** — "So far we've recovered 80% of your files..."
2. **Value preview** — "Next, we'll set up auto-backup so this never happens again..."
3. **Handle resistance** — "You might wonder why we skipped that option—it's because..."
4. **Key moment** — "This next click is the one that actually commits the changes..."

**Rehook must naturally lead into Product Intro:**
- Rehook ends with problem/state → Product Intro explains why → introduces product as logical solution
- Never repeat the same pain point the Rehook already said

**❌ Don'ts:**
- ❌ Same sentence pattern every time
- ❌ Preview something that already happened
- ❌ Fake urgency: "This is the most important part" (used 3 times)

---

## SEO TITLES (generate 3)

Use these formulas:
- `[N] Ways to [Fix Problem] (2026)`
- `How to [Fix Problem] for [Specific Situation]`
- `[Fix Problem] in Less Than [Time] — FREE`

Rules:
- Lead with the problem or outcome, not the tool
- Mirror exact search phrases users type
- Include device/OS when relevant (Mac, Windows 11, iPhone)
- Under 60 characters
- Include "without [fear]" where relevant: "without data loss", "without formatting"

---

## CTA

**Mid-video** (after first result shown):
> "If this video is helping you out so far, hit that like button—it really helps the channel. Let me know in the comments if you got your files back."

**End CTA — product:**
> "I'll leave a link in the description where you can download [Product] for free—go check that out if you need it."
> "Like I said, they give you 2GB of free recovery, so if you only have a few files, it's totally free. Go give it a try."

**Subscribe:**
> "If you found this helpful, consider subscribing for more tech tips."

---

## PRODUCT SCOPE RULE

Only use content for the product the user specifies.
`product-knowledge.md` contains multiple products — do not reference or mention products that were not requested.

---

## THUMBNAIL PROMPTS (generate 3)

Each prompt must follow specs from `cover-design-specs.md`:
- 1280×720px, 16:9, under 2MB
- High contrast text, readable on small screens
- No text in bottom-right corner
- High brightness/vibrancy
- Include face if possible (improves CTR)

---

## OUTPUT FORMAT

**Script mode (mixed):**
- **Full word-for-word:** Hook, Product Intro, all Rehooks, CTA
- **Outline only:** Free methods, Tutorial steps, Result section

**File:** Export as `.docx` containing:
- 3 SEO titles
- Video outline with timing
- Full script
- SEO tags + description
- 3 thumbnail prompts
