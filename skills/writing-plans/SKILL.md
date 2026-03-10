---
name: writing-plans
description: "Use when translating a design into an implementation plan. Produces bite-sized tasks (2-5 min each) with exact file paths, TDD integration, and theory-check points at concept boundaries."
---

# Writing Plans

## The Rule

**Every plan is a map of both the code to be built and the theory to be built.**

A plan that only tracks files and functions is half a plan. The other half is: what
does the human need to understand at each step, and where are the natural moments
to check?

## Plan Structure

### Header

Reference the design that produced this plan and the diary concepts it touches:

```
## Plan: [Feature Name]
Design: [link or summary of the brainstorming output]
Concepts: [list concepts from diary this plan touches]
```

Call `check_concept` for each listed concept. If any are new territory or have
struggle entries, note them — those are your theory-check points.

### Tasks

Each task must be:
- **Bite-sized**: 2-5 minutes of work. If it's bigger, decompose it.
- **Concrete**: Exact file paths. Exact function signatures. No ambiguity.
- **TDD-shaped**: Test first where possible. "Write test for X" and "Implement X"
  are separate tasks.
- **Concept-tagged**: Note which diary concept(s) this task touches.

### Theory-Check Points

At natural boundaries — where the work shifts from one concept to another, or
where a new abstraction is introduced — include:

```
--- theory check recommended if [[concept]] is new territory ---
```

These are not gates. They're reminders. When you reach one during execution, read
the diary for that concept. If the human has demonstrated understanding, skip it.
If not, pause and check in.

### Boundary Heuristics

Insert a theory-check point when:
- The next task introduces a concept with no diary entries
- The next task touches a concept the diary says the human struggled with
- You're crossing an abstraction boundary (e.g., data layer to API layer)
- The upcoming batch depends on understanding something from the previous batch

## Writing the Plan

1. Call `get_plan_state()` to check for existing plan context
2. Call `plan_step(description, parent_id?, reasoning?)` for each top-level task
3. Present the full plan to the human
4. Wait for their input — they may reorder, cut, or add tasks
5. After agreement, invoke the **executing-plans** skill

## Anti-Rationalization

| Rationalization | Reality |
|----------------|---------|
| "Theory-check points will make the plan too long" | They're one-line annotations. If your plan can't absorb a one-liner, it's already too dense. |
| "Just one big task, it's simpler" | A 20-minute task with no checkpoints is 20 minutes of silent accumulation. Break it up. |
| "The human will find concept tags patronizing" | Concept tags are for YOU — they tell you when to read the diary during execution. |
