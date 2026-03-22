---
name: iterative-enrichment
description: "Use when building any substantial written artifact. Produces the artifact through progressive fidelity levels — each level a checkpoint where the human corrects the decompression before investment increases."
---

# Iterative Enrichment

## The Rule

**Each intermediate is not a useful artifact in itself — it is a mirror reflecting
your understanding of the human's intent at a fidelity level where correction is cheap.**

A thesis statement is easy to redirect. An annotated outline is easy to restructure.
A rough draft is harder. A polished draft is expensive. The entire process is designed
so that misalignment surfaces early, when fixing it costs minutes instead of hours.

## The Five Fidelity Levels

### Level 1: Thesis Statement (1-2 sentences)

Capture the core claim or argument in its most compressed form. This is the seed
from which the entire piece grows.

Present it to the human. Not as a fait accompli — as a mirror:
- "Here's what I think you're arguing. Is this the piece you want to write?"

**What to watch for**: If the human corrects the thesis, that correction is the
most valuable signal of the entire process. Record it. It tells you where your
model of their intent was wrong.

**Do not proceed until the human has genuinely engaged with the thesis.** "Looks good"
is not engagement. Engagement sounds like: "Yes, but the emphasis should be more on X"
or "That's the right direction but I'd frame it as Y."

### Level 2: Structural Outline

Sections, their purpose, and how they connect. No prose — just the skeleton.

For each section:
- What argumentative work it does
- Why it comes in this order (what does the reader need to have accepted before arriving here?)
- How it connects to the sections around it

Present to the human:
- "Here's how I'd organize the argument. The key structural choice is [X] — does
  that sequence work for how you think about this?"

**What to watch for**: Structural disagreements here save enormous rework later.
If the human wants to reorder, that tells you something about how they conceive
of the argument's logic — record it.

### Level 3: Annotated Outline

Flesh out each section with:
- Key arguments and claims to be made
- Sources to integrate and how they'll be used
- Open questions that need resolving before drafting
- The strongest objection the section needs to handle

Present to the human section by section:
- "For [section], here's the argument I'd build. The open question is [X] — what's
  your instinct there?"

**What to watch for**: This is where the human's actual beliefs about the subject
matter surface. When they push back on a claim or suggest a different use of a source,
they're revealing their theory of the field. That's diary-worthy.

### Level 4: Rough Sections

Full prose, imperfect, focused on getting the argument down. Don't polish — prioritize
argumentative completeness over sentence-level quality.

Present each section with a preamble:
- What argumentative work this section does
- Where the prose is weakest (flag it yourself)
- Where you made judgment calls the human should check

**What to watch for**: The human's reaction to rough prose reveals their standards
and priorities. Do they focus on argument? On evidence? On voice? On audience?
Record these preferences — they're stable across pieces.

### Level 5: Polished Draft

Refined prose, transitions, coherence check across sections. This is where sentence-level
craft matters.

Before presenting, invoke **verification-before-completion**:
- Does the argument hold end-to-end?
- Are sources properly integrated?
- Does the structure serve the reader?
- Is the thesis supported?

## The Enrichment Discipline

### At EVERY Level

1. **Present** the current fidelity level to the human
2. **Wait** for genuine engagement — not a rubber stamp
3. **Record** what the engagement revealed (diary entry tagged `(vygotsky-knowledge)`)
4. **Check alignment** — does your model of their intent match theirs?
5. **Only then** proceed to the next level

### Handling Rubber Stamps

If the human says "looks good" or "go ahead" without engaging:
- Pick the most consequential choice at this fidelity level
- Make it concrete and specific
- "Just checking — we're arguing X rather than Y, which means the piece won't
  address Z. That the right call for this audience?"

This is not a quiz. It's what a co-author says before investing the next round of work.

### Skipping Levels

The human may ask to skip a level ("just start writing"). Discuss the trade-off:
- "We can — the risk is that if the structure doesn't work, we'll be revising prose
  instead of an outline. Want to do a quick structural check first, or dive in?"

Ultimately respect their choice. But name the cost.

### Backing Up

If a higher-fidelity level reveals a problem at a lower level (e.g., rough prose
reveals a structural issue), go back to the appropriate level. Don't patch at the
wrong fidelity.

- "The prose is exposing a structural issue — section 3 is trying to do two things.
  Let me back up to the outline level and we can decide how to split it."

## Why This Works

The progressive fidelity model works because of how human intent operates: people
often don't know exactly what they want to say until they see an imperfect version
of it. Each level gives them something concrete to react to — and reaction is
cheaper than generation.

The key insight is not "iterate until it's good." The key insight is: **each
intermediate exists to be corrected, and each correction teaches you something
about what the human actually means.**

A thesis they don't correct tells you nothing. A thesis they rewrite tells you
everything.

## Diary Entries

At each level transition, write a diary entry capturing:
- What the human corrected or confirmed
- What this reveals about their intent, their theory of the audience, or their
  understanding of the subject matter
- Evidence type: typically `argument_choice`, `structural_decision`, `correction`,
  or `explanation`

Tag all entries `(vygotsky-knowledge)`.

## Anti-Rationalization

If you catch yourself rationalizing why a fidelity level can be skipped, STOP and read
`skills/vygotsky/reference/anti-rationalization.md` before proceeding.

Key trap for this skill: "I understand what they want, I can jump to prose" — if you understood perfectly, the thesis statement takes 10 seconds to confirm. If you didn't, you just saved hours of rework.
