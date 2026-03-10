---
name: brainstorming
description: "Use when exploring a new feature, refactoring idea, or design problem. Builds shared understanding of the problem space before any code is written. No code until design is presented, discussed, and approved."
---

# Brainstorming

## The Rule

**No code until the design is presented and the human has engaged with it.**

Not "presented and approved." Presented and *engaged with*. If they say "looks good"
without engaging with the trade-offs, you haven't finished brainstorming — you've
just gotten a rubber stamp.

## The Process

### 1. Build Shared Understanding of the Problem Space

Don't jump to solutions. First, make sure you and the human are looking at the same
problem. Read the relevant code. Read the diary for related concepts.

Ask the kind of questions a colleague asks when they sit down next to you:
- "What's the actual problem we're solving here?"
- "What have you already tried or considered?"
- "What constraints are we working within?"

**Do NOT** run through a checklist. Have a conversation. If you already know the
answer from the diary, don't re-ask — build on what's established.

### 2. Explore the Design Space Together

Surface at least two viable approaches. For each one:
- What it gives you
- What it costs you
- Where it gets tricky

The human should be thinking about these trade-offs, not just picking from a menu.
Ask: "Which of these trade-offs matters more for this project?" or "Where do you
think we'll feel the pain first?"

### 3. Present the Design

Once you've converged, write up the design clearly:
- **Approach**: What we're building and why this shape
- **Key decisions**: The trade-offs we made and why
- **Risks**: What could go wrong and how we'd know

Present it as a proposal, not a decree. The human should be able to push back on
any part of it.

### 4. Confirm Engagement, Not Just Approval

If the human rubber-stamps ("looks good", "sure", "go ahead") without engaging
with the substance:
- Pick the most consequential trade-off and make it concrete
- "Just to make sure we're aligned — we're choosing X over Y, which means Z. That
  feel right for this use case?"

This is not a quiz. It's the kind of thing you'd say to a colleague before investing
a week of work.

### 5. Record and Transition

After genuine engagement:
- Call `record_observation` to diary what the human demonstrated understanding of
- Invoke the **writing-plans** skill to translate the design into executable steps

## Anti-Rationalization

| Rationalization | Reality |
|----------------|---------|
| "The design is obvious, let's just start coding" | If it's obvious, articulating it takes 30 seconds. If it's not, you just saved hours. |
| "They said 'just do it'" | Acknowledge their urgency. Present the design briefly. A 2-minute discussion prevents a 2-hour rewrite. |
| "I already know the best approach" | You might. But if the human doesn't understand *why*, they can't extend it, debug it, or maintain it. |
| "Exploring alternatives will slow us down" | The brainstorm IS the work. Code without shared theory is technical debt with interest. |
