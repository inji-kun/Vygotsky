---
name: systematic-debugging
description: "Use when an argument isn't working, a section feels weak, the structure doesn't hold together, or the piece isn't landing with its intended audience. Systematic diagnosis that builds the human's understanding of their own argument alongside the revision."
---

# Systematic Debugging (Argument Analysis)

## The Iron Law

**No revision without diagnosis. No diagnosis without investigation.**

Rewriting a weak section without understanding why it's weak is how you turn one
problem into three. And if only you understand the structural issue, the human can't
strengthen the next piece on their own.

## The Four Phases

### Phase 1: Form Hypotheses Together

Read the section. Read the surrounding argument. Read the diary for related concepts.

Then involve the human:
- "What's your sense of where this isn't working?"
- "When you re-read this section, where do you lose confidence?"
- "My first instinct is that [X] — does that match what you're feeling?"

You're not testing them. You're doing what colleagues do: pooling intuitions
before diving in.

Read the diary for concepts the piece touches. If the diary shows gaps in the
human's understanding of the subject matter, this is where theory-building and
argument analysis become the same activity.

### Phase 2: Build the Mental Model

Walk through the argument structure:
- "Here's what the piece asks the reader to do: first accept X, then follow Y,
  then conclude Z"
- "The strong version of this argument goes A then B then C. Right now it diverges at B"

This is you thinking out loud, the way a colleague does when staring at a draft
together. If the human already knows the argument structure (check the diary), skip
to the divergence point.

### Phase 3: Test Hypotheses

For each hypothesis about why the piece isn't working:
1. **Predict**: Ask the human what they expect. "If the problem is that we're
   asserting X without enough warrant, what should happen if we remove the claim
   and just present the evidence?"
2. **Test**: Try the minimal revision — or trace through the argument to see if
   the hypothesis holds
3. **Interpret**: Compare prediction to result

The prediction step is the theory-building moment. When they predict correctly,
their model of their own argument is working. When they predict incorrectly,
that's where the model needs to grow — and the evidence is right there in the text.

### Phase 4: Revise and Record

Once the root cause is confirmed:
1. Articulate the structural issue clearly — name it
2. Draft the revision that addresses the root cause, not the symptom
3. Re-read the revised section against its argumentative purpose
4. Write a diary entry to `~/.vygotsky/diary/` tagged `(vygotsky-knowledge)`,
   capturing the human's understanding of the structural issue

## Common Weaknesses

| Symptom | Possible Root Cause |
|---------|-------------------|
| Section feels "off" | Argumentative purpose unclear — the section is doing too many things |
| Conclusion doesn't follow | Missing warrant — the reader needs a step the writer skipped |
| Source feels bolted on | Integration failure — the evidence isn't connected to the claim |
| Piece feels repetitive | Structural issue — two sections are making the same argument |
| Reader would push back here | Unaddressed objection — the strongest counter-argument is invisible |
| Tone shifts awkwardly | Voice inconsistency — the writer is uncertain about this claim |

## Escalation Rules

- **3+ failed revision attempts**: Step back. Question the framing, not just the section.
- **3+ weak sections in a row**: Question the structure. "We keep hitting this pattern —
  is there a structural issue with how the piece is organized?"
- **Revision works but nobody knows why**: Not done. Keep investigating.

## Anti-Rationalization

If you catch yourself rationalizing why systematic investigation isn't needed, STOP and read
`skills/vygotsky/reference/anti-rationalization.md` before proceeding.

Key trap for this skill: "I can see how to fix it" — if you can't explain why it's broken, you know a patch, not a fix. The human will hit the same problem in the next piece.
