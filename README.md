<p align="center">
  <img src="assets/lev-vygotsky.jpg" alt="Lev Semyonovich Vygotsky (1896–1934)" width="200" />
</p>

<h1 align="center">Vygotsky</h1>

<p align="center"><em>Theory-building partners for <a href="https://docs.anthropic.com/en/docs/claude-code">Claude Code</a></em></p>

<p align="center">
  <a href="#tldr">TL;DR</a> · <a href="#install">Install</a> · <a href="#one-more-prompt">The Problem</a> · <a href="#the-evidence">The Evidence</a> · <a href="#how-it-works">How It Works</a>
</p>

---

<a id="tldr"></a>

**TL;DR:** AI tools produce output without understanding. In controlled studies, people who delegate to AI score below 40% on conceptual mastery; people who *inquire* with AI score 65%+. Vygotsky is a set of Claude Code plugins that structure every session around mutual theory building. One side of the coin: a narrative diary and engagement tracking let Claude build a theory of *your* understanding — what you've demonstrated, where you're engaged, where you're drifting. The other side: intent decompression, recursive planning, and iterative enrichment let Claude build a richer theory of *your intent* — what you actually mean, what you're trying to build, and where its model of you is wrong.

This is a research project, not a finished product. The theory is grounded in real evidence (see below). The implementation is careful. But it hasn't been validated at scale — we're sharing it because we think the ideas matter and we want people to try them and tell us what happens.

## Install

From inside Claude Code:

```
/plugin marketplace add inji-kun/vygotsky
```

### vygotsky-code — for software development

```
/plugin install vygotsky-code@vygotsky
```

Replaces [superpowers](https://github.com/anthropics/claude-plugins-official). If you have superpowers enabled, disable it first:

```
/plugin disable superpowers
```

### vygotsky-knowledge — for writing, research, and knowledge work

*Early stage.* The same framework adapted for knowledge work — writing proposals, synthesizing research, building arguments. The theory says this should work across any domain where a human and an AI are co-building an artifact. This is our first attempt at proving that claim.

```
/plugin install vygotsky-knowledge@vygotsky
```

**Recommended: vault access** (so Claude can read/search your Obsidian vault):

```
claude mcp add --transport stdio obsidian -- npx -y mcp-obsidian /path/to/your/vault
```

**Optional: document editing** (for docx/pptx/xlsx/pdf — requires LibreOffice):

```
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

### Both plugins

You can install both. They share a diary (entries tagged by plugin) but track engagement independently — because the same person can be an expert in one domain and building skill in another.

```
/plugin install vygotsky-code@vygotsky
/plugin install vygotsky-knowledge@vygotsky
```

**Requirements:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with plugin support. No additional dependencies — Node.js is already present. No permissions setup needed — diary writes use Claude's native Write tool.

---

*The rest of this is an essay about why these plugins exist. If you just want to try them, you're done — they're installed.*

---

<a id="one-more-prompt"></a>

## One More Prompt

> *"AI coding tools are addictive and nobody's talking about it. Agentic coding triggers the same variable ratio reinforcement as slot machines — intermittent dopamine + adrenaline hits that make it near-impossible to stop. I ended up seeing a doctor because my brain wouldn't shut off at night — got prescribed medication to block wakefulness receptors just so I could sleep."*
>
> — **Quentin Rousseau**, [*One More Prompt*](https://blog.quent.in/posts/2026/03/09/one-more-prompt-the-dopamine-trap-of-agentic-coding/), March 2026

> *"I stopped working out because I didn't want to get out of my chair. I sat around in PJ's all day and didn't shower very often. Didn't brush my teeth. This is why I don't play slot machines."*

> *"It's very easy to run the wrong direction very quickly with AI, and feel like you're making progress without actually having a material impact on your goal."*

> *"AI coding tools promised to make us 1000x developers. Instead, many of us are drowning in half-finished projects, endless re-planning, and a strange new anxiety that comes from having TOO MUCH capability."*

> *"Dealing with AI coding is like wading through a swamp and leaves you exhausted."*
>
> — **Andrew Ng**

These are developers. But the pattern is not about coding.

A [Harvard Business School study](https://www.hbs.edu/faculty/Pages/item.aspx?num=64700) gave 758 BCG consultants access to GPT-4. On tasks within the AI's capability frontier, they were 25% faster with 40% higher quality. On tasks *outside* the frontier, they performed **19 percentage points worse** than consultants without AI — and couldn't tell the difference. A [study in *Science*](https://www.science.org/doi/10.1126/science.adw3000) analyzing 2.1 million preprints found that AI-polished academic papers were *less* likely to survive peer review — polished language masking substantive weakness. [Stanford HAI](https://hai.stanford.edu/news/ai-trial-legal-models-hallucinate-1-out-6-or-more-benchmarking-queries) found that leading AI legal research tools hallucinate on 17–34% of queries. An [MIT Media Lab study](https://arxiv.org/abs/2506.08872) using EEG found that people who wrote essays with ChatGPT showed the weakest neural connectivity patterns — and the effect carried over even after the AI was removed.

And when economists at the [University of Copenhagen](https://www.nber.org/papers/w33777) studied 25,000 workers across Denmark, they found that despite 47% adoption, AI produced **precisely zero** measurable impact on earnings, wages, or hours — confidence intervals ruling out effects larger than 1%.

The same gap between what the tool makes you *feel* (faster, more capable) and what it actually *produces* in the person using it (dependency, erosion of understanding). Developers experience it most visibly because coding is where AI adoption is deepest. But the mechanism is domain-general.

What's going on?

---

## We've Seen This Before

The dominant UX paradigm for the last two decades has been: minimize friction, maximize engagement, optimize for ease of use. This is what good product design has meant since the iPhone — make it seamless, remove every obstacle between the user and the action.

In the 2000s, this paradigm found its business model: the attention economy. Social media feeds, notification systems, infinite scrolls — all engineered to capture and hold human attention, because attention could be sold to advertisers. The side effects — anxiety, sleep disruption, compulsive checking, shortened attention spans — were not the intent. They were the natural consequence of optimizing for engagement without asking what that engagement *cost* the person.

Now the same paradigm has produced its inversion. You might call it the inattention economy.

The pitch from AI tools is: *you don't need to pay attention to the details anymore*. Let the agent handle it. Let it write the code, draft the proposal, synthesize the research, review the contract. Your job is to direct, not to understand. The value proposition is your *disengagement* from the substance of your own work — the less you need to understand, the more valuable the tool.

The people building these tools are talented engineers following the same UX playbook that produced every great product of the last twenty years: remove friction, increase ease, ship faster. The problem is that the playbook's optimization target — frictionless use — is wrong for tools that shape human capability.

The side effects mirror Web 2.0's, inverted:

- **Attention economy**: compulsive *engagement* with content you don't need — anxiety, shortened attention spans, loss of deep focus
- **Inattention economy**: compulsive *delegation* of work you don't understand — anxiety, loss of competence, growing artifacts nobody can maintain or defend

Different mechanism, but the same gap between what the tool makes you *feel* (productive, powerful, fast) and what it actually *produces* in the person using it (dependence, erosion of understanding, a degraded relationship to your own work).

Garry Tan stayed up 19 hours coding with Claude Code and publicly called himself "addicted" — and the community celebrated it. Steve Yegge described sprinting out of the room and slamming the door to stop himself coding at 2 AM. These are stories of a reward loop that has become decoupled from the thing it's supposed to reward.

It would be a shame if AI — arguably the most consequential technology of this era — followed the same trajectory as social media. Not because the technology is bad, or because anyone has bad intentions, but because the UX paradigm needs to evolve for tools that shape what people can do.

### From UX to RX

UX asks: *was that easy?* Was the interaction smooth? Did the user accomplish their task with minimal friction?

RX asks a different question: *what remained after the tool was closed?*

RX stands for Razvitie Experience — from развитие (*razvitie*), the Russian word Lev Vygotsky used for the specific kind of development that happens in the Zone of Proximal Development. Razvitie means something like "unfolding of capability" — something becoming what it has the potential to become. It's broader than "learning" (which sounds like school) and more specific than "growth" (which sounds like self-help).

*Non scholae sed vitae discimus* — we learn not for school, but for life. RX takes this seriously as a design criterion. The measure of a tool is not how it felt to use, but what the person can do — in their work, in their craft — that they couldn't do before.

This isn't opposed to UX. Ease of use still matters, and friction for its own sake is just bad design. But RX adds a question that UX doesn't ask: does this interaction leave the person more capable, or more dependent? If your tool is frictionless but the person who uses it for a year understands less than when they started, something has gone wrong — and it's not a side effect. It's the predictable outcome of optimizing for the wrong thing.

Vygotsky is an attempt to implement RX — starting with software development, and extending to knowledge work broadly.

---

<a id="the-evidence"></a>

## The Evidence

### The Perception-Reality Gap

The [METR Study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) (July 2025) ran a randomized controlled trial with 16 experienced open-source developers — average 22,000+ stars, 1M+ lines of code — working on their own repositories:

- Developers took **19% longer** with AI tools
- They expected AI to speed them up by **24%**
- After experiencing the measured slowdown, they *still believed* AI had sped them up by **20%**
- AI introduced "extra cognitive load and context-switching"

This is not a misunderstanding. It is a documented cognitive phenomenon: **automation complacency** — the same thing that causes airline pilots to miss instrument warnings, nuclear plant operators to overlook anomalies, and drivers to rear-end the car in front of them while autopilot is engaged. Decades of human factors research predicted this. We just didn't think it would happen to developers.

The [JetBrains Developer Survey](https://www.jetbrains.com/lp/devecosystem-2025/) (24,534 developers, 194 countries) confirmed the pattern at scale: **90%** report saving time, while controlled studies show the opposite. Satisfaction dropped from **70%+ to 60%** in a single year — the gap between perceived and actual productivity seems to be closing, and not in the direction people expected.

### Inquiry vs. Delegation

The [Anthropic Skills Study](https://www.anthropic.com/research/learning-skills-with-ai) (January 2026) — a randomized controlled trial with 52 engineers — found the mechanism:

- AI-assisted developers scored **17% lower** on conceptual mastery — nearly two letter grades
- AI reduced task completion time by up to **80%**
- Speed came at the *direct cost* of understanding

But the critical finding was not the average — it was the variance:

- Developers who used AI for **conceptual inquiry** — asking why, probing assumptions, requesting explanations — scored **65%+**
- Developers who used AI for **code delegation** — letting it generate solutions — scored **below 40%**

The difference between these groups was not ability or experience — it was mode of engagement. The tool, the tasks, and the population were the same. The outcomes were wildly different depending on whether the developer was thinking with the AI or delegating to it.

> *"Rather than eliminating time pressure, LLM use shifted it from debugging to understanding, verifying, and documenting AI-generated solutions."*

### Beyond Coding

The coding evidence is the most controlled, but the pattern appears wherever AI meets knowledge work. The BCG study (above) showed the same perception-reality gap among consultants. The *Science* study showed it in academic publishing — more papers, lower acceptance rates. The Copenhagen study showed it economy-wide — massive adoption, zero productivity impact.

A [review in *Springer Nature*](https://link.springer.com/chapter/10.1007/978-3-032-11748-9_5) documented measurable competency decline within months of AI adoption across medical, legal, and professional practice. A [study of 666 participants](https://www.mdpi.com/2075-4698/15/1/6) found a significant negative correlation between AI usage frequency and critical thinking ability, mediated by cognitive offloading — the more you trust the tool, the less you think for yourself.

The mechanism is the same everywhere: the AI produces output that *looks* competent, the human accepts it because checking requires effort the output doesn't reward, and understanding silently erodes. The domain doesn't matter. The interaction design does.

### Why This Happens: The Cognitive Science

**The 10-bit bottleneck.** Caltech researchers (2024) quantified what designers have intuited for decades: conscious human thought operates at approximately **10 bits per second**. Sensory systems gather a billion bits per second. Any tool that dumps information at compute speed is fighting human neurology. The streaming text that makes an AI agent look impressively fast is, from the perspective of human cognition, a firehose aimed at a teacup.

**Cognitive load theory.** John Sweller (1988) distinguished three types of cognitive load. *Intrinsic* load is the complexity inherent in the task — you can't reduce it. *Extraneous* load is the extra effort imposed by poor information design — undifferentiated text streams, context that scrolled away, information presented faster than you can process it. *Germane* load is the effort devoted to building understanding — the productive struggle of figuring something out. Most developer tools minimize all cognitive load indiscriminately, treating friction as universally bad. This is wrong. Extraneous load should be eliminated. Germane load should be *cultivated*. The right kind of friction — at the right moment, at the right intensity — is what produces understanding.

**The fragility of attention.** Gloria Mark's research at UC Irvine showed that it takes approximately **25 minutes** to refocus after an interruption. People compensate by working faster, which increases stress and cortisol. The mere *possibility* of notification creates anticipatory anxiety, even when no notification comes. Flow states are fragile and valuable. Importantly, **self-interruptions** (choosing to check something) cost less than external interruptions — the nervous system responds differently to voluntary versus involuntary attention shifts. A well-placed theory check, one that the developer experiences as part of the work rather than an interruption to it, doesn't carry a 25-minute refocus cost. It's collaborative thinking, not a context switch.

**What disengagement actually looks like.** The person who types "ok" and "looks good" and hopes for the best isn't lazy. They've hit the point where extraneous cognitive load has overwhelmed their capacity to process, and they've switched from trying to understand to trying to get through it. Sweller's framework predicts this: when total load exceeds working memory, germane processing — the kind that builds understanding — is the first thing to go. The person who can't stop prompting at 2 AM isn't unusually disciplined either. Rousseau identified the mechanism: variable ratio reinforcement, the same schedule that makes slot machines compelling. Neither state produces understanding, and both are predictable responses to an interaction design that offers no calibration and no natural stopping points.

---

## Knowledge Work as Theory Building

Peter Naur ([1985](https://pages.cs.wisc.edu/~remzi/Naur.pdf)) argued that programming is not the production of code but the building of a **theory** — a mental model of the problem domain, the solution architecture, and the relationship between them. Code is an artifact of theory. Without the theory, the code is unmaintainable, even if it works perfectly.

This is not specific to programming. An academic proposal is an artifact of a theory about a field and where it needs to go. A legal brief is an artifact of a theory about how the law applies to the facts. A research synthesis is an artifact of a theory about what the literature says and what it means. In every case, the artifact without the theory is a liability — it cannot be defended, extended, or revised by the person who holds it. And in every case, AI tools are producing the artifact while bypassing the theory construction that gives the artifact its value.

When the Hacker News community rediscovered Naur in July 2025 — after the METR study showed AI makes experienced developers slower — the connection was immediate: AI disrupts theory-building. But the disruption is not limited to code. The BCG consultant who accepts AI-generated strategy slides without building a theory of the market has acquired a liability. The academic who submits an AI-polished paper without deeply engaging with the argument has acquired a liability. The artifact looks competent. The person holding it is not.

"Struggle" — the traditional mechanism for theory construction — is really just a word for germane cognitive load. And germane load can take forms other than doing the work by hand. The Anthropic study showed this: the tight communication loop between human and AI — asking why, probing assumptions, predicting outcomes — *is* the productive struggle. It just doesn't look like what struggle used to look like.

Lev Vygotsky ([1896–1934](https://en.wikipedia.org/wiki/Lev_Vygotsky)) showed that cognitive development happens in the space between what you can do alone and what you can do with guidance — the *Zone of Proximal Development*. The guidance must be calibrated. And critically, the scaffolding must *fade*: good guidance creates competence, then withdraws. Yesterday's guided discovery becomes today's autonomous skill.

### Two Minds, One Shared Front-End

But there is a deeper problem. As the evolutionary biologist Robin Dunbar showed, human language evolved for a specific purpose: to build theories of other minds. Hominin brains grew with the need to recursively model what others believe, what others believe others believe, and so on. Language is the front-end through which two back-ends co-build theories about one another and the world.

When a human and an AI communicate through the same front-end — what looks like English — both sides are operating under a misguided assumption: that they speak the same language. The vocabulary and grammar are shared, but the implicit context is not. Humans evolved to decode one another with sparse signals because shared biology and culture fill the gaps. LLMs lack that shared context. The human gives an underspecified prompt (natural for human-to-human). The model one-shots a plausible response (rewarded by RLHF). And the output — optimized for the appearance of helpfulness rather than the fidelity of intent reconstruction — produces exactly the kind of low-information-density text that triggers skim mode. Attention disengages not because the human is careless, but because the output gives attention nothing to grip.

The synthesis: if the core problem is two minds miscommunicating through a shared front-end, the solution is a process that makes the miscommunication visible and correctable. This is what Vygotsky does — from two directions.

One side of the coin: a **narrative diary** and **engagement tracking** let Claude build a theory of *your* understanding — what you've demonstrated, where you're engaged, where you're drifting. This is Claude modeling your output.

The other side: **intent decompression**, **recursive planning**, and **iterative enrichment** let Claude build a richer theory of *your intent* — what you actually mean, what you're trying to build, and where its model of you is wrong. This is Claude modeling your input.

The human's job is to construct and maintain the persistent theory. The AI's job is twofold — **compile that theory into an artifact**, and **scaffold the theory-building itself**. The AI is not just a generator. It is a collaborator in the thinking — participating in the conversation that builds your understanding of what's being built, while building its own understanding of what you actually want.

---

<a id="how-it-works"></a>

## How It Works

Vygotsky is a set of [Claude Code plugins](https://docs.anthropic.com/en/docs/claude-code/plugins) that restructure how Claude interacts with you. **vygotsky-code** replaces [superpowers](https://github.com/anthropics/claude-plugins-official) for software development. **vygotsky-knowledge** extends the same framework to writing, research, and knowledge work — designed for use with [Obsidian](https://obsidian.md/) vaults.

### Getting Started with vygotsky-knowledge

If you're using the knowledge work plugin with Obsidian, the setup is straightforward: open Claude Code inside your vault directory. Your vault is just a folder of markdown files — Claude can read and write them directly.

```bash
cd ~/path/to/your/vault
claude
```

For search and structured queries across your vault, add the recommended MCP server:

```bash
claude mcp add --transport stdio obsidian -- npx -y mcp-obsidian ~/path/to/your/vault
```

This gives Claude tools to search your notes by content, read specific files, and understand the vault's structure. It reads the markdown files directly from disk — Obsidian doesn't need to be running.

### The Diary

Claude maintains a **narrative diary** of what you've demonstrated understanding of, organized by concept. No numbers, no grades, no scores — just timestamped observations:

> *"Traced the race condition in the WebSocket handler back to the missing mutex on shared state. Explained why the lock needs to be per-connection, not global — understands the performance trade-off."*

> *"Explained the tension between Dunbar's social brain hypothesis and distributed cognition clearly. Chose to frame language as UX paradigm rather than cognitive prerequisite — understands the theoretical stakes."*

Why narrative instead of numeric? Because "React: 7/10" tells you nothing. Numbers compress away the information that matters. The diary builds across sessions and across plugins — so Claude never re-explains what you already know, and never assumes you know what you haven't demonstrated.

### Theory Checks

Throughout the session, Claude weaves in moments that check whether you're building a theory of the work — not after the fact, but as part of the conversation. In code, it might walk you through a design choice and ask if it matches your mental model. In writing, it might surface a structural tension and ask how you think about it. The form varies by domain. The purpose is the same: keeping you engaged with the substance.

The tone is always collaborative — a colleague thinking out loud, not a teacher quizzing you:

> *"So this migration drops the `legacy_users` table after copying to `users_v2`. If the copy fails halfway, we'd need to restore from backup — there's no rollback path built in. That feel right, or should we add a verification step?"*

> *"We're arguing X rather than Y in section 3, which means the piece won't address Z. That the right call for this audience?"*

Never: *"Can you explain what this migration does?"* Never: *"Do you understand the argument?"*

The difficulty of the question is the same. The experience of being asked is completely different. One triggers defensiveness; the other triggers thinking.

### Engagement Tracking

Three rubber stamps in a row — "looks good", "sure", "go ahead" — and Claude adjusts. Theory checks become more concrete. Batch sizes shrink. The interaction mode shifts to give you more surface area to engage with.

The person typing "ok" and "y" is present but not processing — germane cognitive load has dropped to zero. Vygotsky detects this and responds not with a penalty, but with a recalibration that makes re-engagement easier.

### Four Interaction Modes

Vygotsky's central insight was that the Zone of Proximal Development is narrow, personal, and dynamic — what stretches one person paralyzes another, and where you are shifts as you work. The plugin operationalizes this through four modes, arranged on two axes: how much skill you've demonstrated in the current domain, and how engaged you are right now.

|  | **High engagement** | **Low engagement** |
|---|---|---|
| **High skill** | **Extension** — scaffolding fades. Larger batches, light-touch theory maintenance. You drive. | **Sparring** — you have the skills but you're skimming. Claude surfaces trade-offs and asks for your reasoning on decisions that matter. |
| **Building skill** | **Senior Peer** — the highest-leverage mode for growth. Claude breaks tasks into steps, invites you to predict outcomes, builds the theory collaboratively. | **Brake Pedal** — unfamiliar territory plus low engagement is the highest-risk state. One concept at a time. Walk through what's actually happening before changing it. |

The modes are not rewards or punishments. Extension is where scaffolding has done its job and withdraws — this is the Vygotskian fade, not a gold star. Brake Pedal is not a penalty for being disengaged; it's the recognition that when someone has stopped processing (typing "ok", "sure", "go ahead"), pushing harder makes it worse. You shrink the scope until re-engagement becomes possible.

Transitions happen within a session and in both directions. You might start in Senior Peer, demonstrate solid understanding, shift to Extension — then hit an unfamiliar subsystem and move back to Senior Peer. Claude never announces transitions — the shift is felt in the pace and depth of interaction, not declared. The quadrant is Claude's internal judgment, continuously updated from the live conversation.

### Workflow Skills

**vygotsky-code** (10 skills):

| Skill | Core principle |
|-------|---------------|
| **brainstorming** | No code until you've *engaged* with the trade-offs — not just approved them |
| **writing-plans** | Concept-tagged tasks with theory-check points at abstraction boundaries |
| **executing-plans** | Batch reports with "what this means." Batch size adapts to mode. |
| **systematic-debugging** | No fix without a root cause. Hypotheses formed *together*. |
| **test-driven-development** | One sentence on what each test proves and why it matters |
| **dispatching-parallel-agents** | You understand the shape *before* and the meaning *after* |
| **verification-before-completion** | "Should work" is not verification |
| **using-git-worktrees** | Always oriented on which directory holds which state |
| **finishing-a-development-branch** | Merge strategies with enough context to choose |
| **writing-skills** | Meta-skill for extending Vygotsky while preserving its soul |

**vygotsky-knowledge** (7 skills):

| Skill | Core principle |
|-------|---------------|
| **brainstorming** | No draft until you've *engaged* with the argument — not just approved the framing |
| **iterative-enrichment** | Each intermediate is a mirror of intent at a fidelity where correction is cheap |
| **writing-plans** | Tasks track both the artifact and the theory being built |
| **executing-plans** | Batch reports: what was written, key argument choices, what this means |
| **systematic-debugging** | No revision without diagnosis. Where is the argument actually weak? |
| **verification-before-completion** | Re-read the artifact against its stated goals. Evidence before assertions. |
| **writing-skills** | Meta-skill for extending Vygotsky while preserving its soul |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Plugin Marketplace                             │
│  vygotsky-code    — software development        │
│  vygotsky-knowledge — writing & research        │
├─────────────────────────────────────────────────┤
│  Per-Plugin Layer                               │
│  SKILL.md — domain-specific operating posture   │
│  session-start.sh — domain-specific brief       │
│  Workflow skills — domain-specific processes     │
├─────────────────────────────────────────────────┤
│  Shared Hooks — Safety floor + engagement       │
│  PreToolUse: theory-check on destructive ops    │
│  PreToolUse: burst pacing (mid-turn check)      │
│  PostToolUse: burst counter on write ops        │
│  Stop: queues theory-check nudge if passive     │
│  UserPromptSubmit: passive engagement detection  │
├─────────────────────────────────────────────────┤
│  Shared State — ~/.vygotsky/                    │
│  diary/ — shared, entries tagged by plugin      │
│  summaries/ — synthesized concept summaries     │
│  plugins/{name}/ — per-plugin engagement state  │
│  No MCP server. No external dependencies.       │
└─────────────────────────────────────────────────┘
```

State persists in `~/.vygotsky/` across sessions. The diary is shared across plugins — the same person's understanding is one continuous model. Engagement tracking is per-plugin — because the same person can be an expert in code and a novice in academic writing.

---

## What This Looks Like in Practice

A person using Vygotsky finishes a session having:

- **Constructed a theory** of the work being built — their primary contribution
- **Produced an artifact** that faithfully compiles that theory — the AI's contribution
- **Built understanding through collaboration** — the AI scaffolded the theory construction through well-placed questions, walkthrough moments, and predictions
- **Developed skills that transfer** beyond this session — recorded in the diary

You can close your laptop at a reasonable hour. Not because you lack ambition, but because you know what was built, why it's shaped that way, and what to do next. There's no compulsion to check on agents at 2 AM, because you're not a spectator watching a slot machine — you're someone who understands what was built and can trust the result.

The felt productivity matches the actual productivity. The satisfaction doesn't decline over time. It deepens.

---

## Related Work

Most AI tools optimize for task completion speed — how fast can the output be produced, how little does the person need to do. That's a reasonable goal, and these tools are genuinely good at it. But it leaves open the question of what happens to the person's understanding over time.

AI coding agents (Claude Code, Cursor, Copilot) optimize for getting code written. AI writing tools (ChatGPT, Claude.ai) optimize for producing polished text. Multi-agent terminals (cmux, Architect) optimize for throughput. None of them ask whether you understood what was produced, or whether you could reproduce, extend, or defend it on your own.

Vygotsky tries to.

---

## References

### Coding
- **METR** (2025). *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity.* [metr.org](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- **Anthropic** (2026). *How AI Assistance Impacts the Formation of Coding Skills.* [anthropic.com/research](https://www.anthropic.com/research/learning-skills-with-ai)
- **JetBrains** (2024–2025). *Developer Ecosystem Survey.* 24,534 developers, 194 countries.

### Knowledge work
- **Dell'Acqua, McFowland, Mollick et al.** (2023). *Navigating the Jagged Technological Frontier.* Harvard Business School Working Paper 24-013. 758 BCG consultants. [hbs.edu](https://www.hbs.edu/faculty/Pages/item.aspx?num=64700)
- **Kusumegi et al.** (2025). *Scientific production in the era of large language models.* Science 390, 1240-1243. 2.1M preprints. [science.org](https://www.science.org/doi/10.1126/science.adw3000)
- **Humlum & Vestergaard** (2025). *Large Language Models, Small Labor Market Effects.* NBER Working Paper 33777. 25,000 workers. [nber.org](https://www.nber.org/papers/w33777)
- **Stanford HAI** (2024). *Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools.* [hai.stanford.edu](https://hai.stanford.edu/news/ai-trial-legal-models-hallucinate-1-out-6-or-more-benchmarking-queries)
- **Kosmyna et al.** (2025). *Your Brain on ChatGPT: Accumulation of Cognitive Debt.* MIT Media Lab. arXiv:2506.08872. [arxiv.org](https://arxiv.org/abs/2506.08872)

### Foundations
- **Peter Naur** (1985). *Programming as Theory Building.* Microprocessing and Microprogramming 15.
- **Lev Vygotsky** (1978). *Mind in Society: The Development of Higher Psychological Processes.*
- **Robin Dunbar** (1998). *Grooming, Gossip, and the Evolution of Language.* Harvard University Press.
- **Gloria Mark** (2023). *Attention Span.* HarperCollins.
- **John Sweller** (1988). *Cognitive Load During Problem Solving.* Cognitive Science 12(2).
- **Caltech** (2024). *The 10-Bit Bottleneck: Quantifying Conscious Information Processing.*
- **Gerlich** (2025). *AI Tools in Society: Impacts on Cognitive Offloading and the Future of Critical Thinking.* Societies 15(6). [mdpi.com](https://www.mdpi.com/2075-4698/15/1/6)
- **Quentin Rousseau** (2026). *One More Prompt: The Dopamine Trap of Agentic Coding.* [blog.quent.in](https://blog.quent.in/posts/2026/03/09/one-more-prompt-the-dopamine-trap-of-agentic-coding/)

---

## Development

```bash
claude --plugin-dir ./vygotsky-code       # run code plugin locally
claude --plugin-dir ./vygotsky-knowledge  # run knowledge plugin locally
```

## License

MIT
