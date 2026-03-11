---
name: executing-plans
description: "Use when implementing a plan produced by writing-plans. Executes tasks in batches with theory-building at checkpoints. Tracks engagement and adjusts posture throughout."
---

# Executing Plans

## The Rule

**Execute in batches. Build theory at the boundaries.**

Batch execution is efficient. But efficiency without understanding produces code
nobody can maintain. The batch boundary is where you pause, share what was built,
and make sure the human's theory kept up.

## Execution Flow

### Before Each Batch

1. Call `get_plan_state()` to orient
2. Identify the concepts this batch touches
3. Call `get_concept` for each — read what the diary says
4. If any concept is new territory or has struggle entries, flag it for a
   theory check after the batch

### During Execution

- Execute tasks sequentially within the batch
- Stop immediately if blocked — don't guess, ask
- Run tests after each implementation task
- **Never commit to main without explicit consent**

### At Each Batch Boundary

Present a batch report:

```
## Batch N Complete

**Built:** [what was implemented]
**Key decisions:** [any choices made during implementation]
**Tests:** [pass/fail status]
**What this means:** [1-2 sentences connecting code to the broader design]
```

The "what this means" section is the theory-building moment. Don't explain the
code — explain what it *does* in the context of the system.

### Theory Checks Between Batches

If the plan has a theory-check annotation or the diary flagged a concept:

- "Before we continue — here's what we just built and what it means for [concept].
  Does that match your mental model, or should we walk through it?"

If the human engages: call `record_observation`. Continue.

If the human is passive (3+ "ok", "sure", "looks good"):
- Call `set_quadrant` — engagement has likely shifted
- Make the next theory check more concrete
- Note the pattern in the diary

## Batch Sizing

- **Default**: 3-5 tasks per batch
- **New territory** (no diary entries): 1-2 tasks, then check
- **Extension mode** (high skill + high engagement): 5-8 tasks, light reports
- **Brake pedal mode**: 1 task at a time, theory check after each

## When Things Go Wrong

- **Test failure**: Stop the batch. Diagnose before continuing.
- **3+ consecutive failures**: Question architecture, not just implementation.
- **Blocked on a decision**: Present options with trade-offs and ask.
- **Scope creep**: Stop and re-plan. Invoke **writing-plans** for the new scope.

## Completion

When all tasks are done, invoke **finishing-a-development-branch** to handle
merge strategy.
