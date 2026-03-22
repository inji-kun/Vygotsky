---
name: executing-plans
description: "Use when working through a plan produced by writing-plans. Executes research and writing tasks in batches with theory-building at checkpoints. Reads plan files directly."
---

# Executing Plans

## The Rule

**Execute in batches. Build theory at the boundaries.**

Batch execution is efficient. But efficiency without understanding produces writing
the human can't defend or extend. The batch boundary is where you pause, share what
was written, and make sure the human's theory of their own argument kept up.

## Execution Flow

### Before Each Batch

1. Read `.claude/plans/index.json` to orient — find current active node
2. Read the active plan file (get the goal, steps, theory-check points)
3. Read parent plan file for breadcrumb context if needed
4. Note which concepts this batch touches — check diary if flagged as new territory

### During Execution

- Execute tasks sequentially within the batch
- Stop immediately if blocked — don't guess at the human's intent, ask
- After each writing task, re-read against the stated argumentative purpose
- Write the pre-draft preamble before every substantial piece of writing (see below)

### Pre-Draft Preamble

Before writing any substantial section, always write this — no exceptions:

```
**What this section does:** [argumentative purpose in plain English — one sentence]
**Where I'm less certain:** [claims that need stronger sources, structural choices that could go either way]
**ZPD note:** [only if this touches territory the diary flags as new — otherwise omit]
```

Then the draft. This directs the human's attention before overwhelming them with prose.
Short is fine. Omitting it is not.

### At Each Batch Boundary

Present a batch report:

```
## Batch N Complete

**Written:** [what was drafted or revised]
**Key argument choices:** [framing decisions, structural moves, what was foregrounded or backgrounded]
**Coherence:** [does the argument hold across sections? are sources properly integrated?]
**What this means:** [1-2 sentences connecting this batch to the whole piece]
```

The "what this means" section is the theory-building moment.

### After Batch Report

Update the plan file: mark completed steps, note any discoveries.
Update `index.json`: set completed nodes to `completed`.

If a discovery affects other branches: log in `## Discoveries`, update affected
plan files, set their status to `needs-revision` in index.json.

### Theory Checks Between Batches

If the plan has a theory-check annotation or the diary flagged a concept:

- "Before we continue — here's the argument we just built in this section and how
  it connects to the overall thesis. Does that match your intention, or should we
  walk through the reasoning?"

If the human engages genuinely: write a diary entry. Continue.

If the human is passive (3+ rubber stamps): recalibrate quadrant from the live
conversation, make the next theory check more concrete, consider a `calibration`
diary entry if adjusting strategy.

## Batch Sizing

- **Default**: 2-4 tasks per batch
- **New territory** (no diary entries): 1-2 tasks, then check
- **Extension mode**: 4-6 tasks, light reports
- **Brake pedal mode**: 1 task at a time, theory check after each

## When Things Go Wrong

- **Argument doesn't hold**: Stop the batch. Diagnose the structural issue before continuing.
- **3+ revisions to the same section**: Question the framing, not just the prose.
- **Blocked on a judgment call**: Present options with trade-offs and ask.
- **Scope creep discovered**: Log in `## Discoveries`, invoke **writing-plans** to
  create child tasks rather than expanding the current task in place.

## Completion

When all tasks are done, invoke **verification-before-completion**.
