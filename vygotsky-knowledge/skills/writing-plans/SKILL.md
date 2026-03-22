---
name: writing-plans
description: "Use when translating a brainstorm or direction into a structured plan for a written artifact. Produces a recursive file-based plan tree with bite-sized tasks, theory-check points, and cross-cutting discovery tracking."
---

# Writing Plans

## The Rule

**Every plan is a map of both the artifact to be built and the theory to be built.**

A plan that only tracks sections and paragraphs is half a plan. The other half is:
what does the human need to understand about their own argument at each step, and
where are the natural moments to check?

## Plan Storage

Plans live in `.claude/plans/` — markdown files + a JSON index. They're human-readable
and survive compaction. No MCP tools needed.

### index.json

Flat skeleton of all nodes. Compact — titles, statuses, parent IDs only.

```json
{
  "01":       {"t": "Root goal",              "s": "active",   "p": null},
  "01-01":    {"t": "Research phase",         "s": "planned",  "p": "01"},
  "01-01-01": {"t": "Gather sources on X",    "s": "planned",  "p": "01-01"}
}
```

Status values: `planned` | `active` | `completed` | `blocked` | `needs-revision`

### Plan file format

Each node gets a `.md` file named after its ID:

```markdown
# [Task Name]
**ID:** 01-01
**Breadcrumb:** Root goal > Research phase
**Status:** planned
**Children:** 01-01-01, 01-01-02

## Goal
[What this task achieves for the written artifact]

## Steps
[Concrete steps — research to do, arguments to construct, sources to integrate,
sections to draft, structural decisions to make]

## Theory-Check Points
--- theory check recommended if [[concept]] is new territory ---

## Discoveries
[Cross-cutting findings that affect other branches — logged here when found]

## Notes from other branches
[Findings from sibling/cousin tasks that affect this one]
```

## Recursion

Decompose until tasks are 5-10 minutes of work. There's no depth limit — go as
deep as the piece requires (depth 3-4 is common for substantial writing).

When to recurse: a step is bigger than 10 minutes, crosses an argument boundary,
requires integrating a new source, or involves a concept the diary flags as new
territory.

ID convention: `01` > `01-01` > `01-01-01` > `01-01-01-01`. Breadcrumb in each
file gives navigation context without loading the whole tree.

## The Steps of Knowledge Work

Tasks in a writing plan are not "write section 3." They are:
- **Research**: locate, read, and annotate a source
- **Argument construction**: articulate a claim, identify its warrants, anticipate objections
- **Source integration**: weave evidence into the argument without losing the thread
- **Structural decisions**: determine section order, transitions, what to foreground vs. background
- **Drafting**: produce prose for a specific section with a specific argumentative purpose
- **Revision**: strengthen a weak argument, improve coherence, tighten prose

Each type has different theory-building opportunities. Research tasks surface what
the human knows about the field. Argument construction surfaces what they actually
believe. Structural decisions surface how they think about the reader's experience.

## Cross-Cutting Updates

When work at one leaf reveals implications for other branches:

1. Log the discovery in the current file's `## Discoveries` section
2. Update affected files with a `## Notes from other branches` entry
3. Set affected nodes to `needs-revision` in index.json
4. Load only affected files to edit them

## Writing the Plan

1. Read `index.json` if it exists — orient to existing plan state
2. Identify the top-level tasks and decompose recursively
3. Create `.md` files and update `index.json` for each node
4. Present the plan tree to the human
5. Wait for their input — they may reorder, cut, or add tasks
6. After agreement, invoke the **executing-plans** skill

## Theory-Check Points

At argument boundaries — when the framing shifts, when a new source changes the
landscape, when a structural decision shapes what the reader encounters:

```
--- theory check recommended if [[concept]] is new territory ---
```

Not gates. Reminders. During execution, read the diary. If the human has demonstrated
understanding, skip it. If not, pause and check in.

## Anti-Rationalization

If you catch yourself rationalizing why planning isn't needed, STOP and read
`skills/vygotsky/reference/anti-rationalization.md` before proceeding.

Key trap for this skill: "It's just a short piece, we can wing it" — a 2000-word argument with no plan is 2000 words of wandering. The shorter the piece, the more every sentence has to earn its place.
