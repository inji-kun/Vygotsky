# Vygotsky v1 Architecture Plan
*2026-03-14*

## The Problem

v0 field test (Dartboard Energy session) confirmed the theory-building posture works.
Two engineering problems emerged:

1. **Batch size**: Claude made large changes without adequate preamble — human had to
   brake manually. Fix: mandatory pre-diff preamble baked into posture.

2. **MCP context bloat**: 8 tool calls per session — get_session_state, get_concept,
   record_observation, set_quadrant, plan_step, complete_step, get_plan_state —
   each adding tokens. Heavy for what it buys.

---

## Design Principles (from research + gstack)

- **One inject at session start, nothing mid-session** (gstack: modular context injection)
- **Quadrant is ephemeral** — derived from session brief + live conversation observation,
  never stored as server state. Transitions happen in Claude's reasoning, not a database.
- **Files are state for planning** — flat markdown + JSON index, no server
  (Sable-Point: empirical proof, depth 4-5, multi-session, resilient)
- **MCP earns its keep only where files can't** — cross-session, cross-repo developer model
- **Two-pass before code** — ZPD callouts first, then diff
  (gstack: two-pass review separates critical from informational)

---

## What Changes

### 1. Pre-Diff Preamble (immediate, SKILL.md only)

Before ANY code change, mandatory:

```
**What's changing:** [core logic in plain English]
**Where I'm less certain:** [Claude's blindspots, places that need human eyes]
**ZPD note:** [if this touches new territory for you, flagged here]
```

Then the diff. Human's attention is directed before being overwhelmed.
Baked into SKILL.md as a hard requirement, not a suggestion.

---

### 2. Planning Machinery → Files (remove plan_tree MCP, supersede superpowers planning)

**Remove:** `server/plan_tree.py`, tools: `plan_step`, `complete_step`, `get_plan_state`

**Rewrite:** `brainstorming` and `writing-plans` skills to incorporate recursive hierarchical
planning natively. This supersedes how superpowers describes brainstorming/planning.
The brainstorming skill ends by handing off to writing-plans; writing-plans now produces
a recursive file-based plan tree instead of calling MCP tools.

**Replace with:** `writing-plans` and `executing-plans` skills writing to `.claude/plans/`

**File structure:**
```
.claude/plans/
  index.json                     # flat skeleton — all nodes, compact
  01-root-goal.md                # depth 1
  01-01-aurora.md                # depth 2
  01-01-01-ercot.md              # depth 3
  01-01-01-01-forecast.md        # depth 4
  01-01-01-01-01-merged.md       # depth 5
```

**Each plan file standard header:**
```markdown
# [Task Name]
**ID:** 01-01-01
**Breadcrumb:** Root goal → Aurora → ERCOT
**Status:** in_progress | planned | completed | needs-revision | blocked
**Children:** 01-01-01-01, 01-01-01-02

## Goal
## Steps
## Discoveries
## Notes from other branches
```

**index.json (flat, compact):**
```json
{
  "01":       {"t": "Extract vendor data",  "s": "active",   "p": null},
  "01-01":    {"t": "Aurora",               "s": "active",   "p": "01"},
  "01-01-01": {"t": "ERCOT",               "s": "planned",  "p": "01-01"}
}
```

**Cross-cutting updates** (the 2.3.5 → 3.3.X pattern):
- Discovery logged in source file's `## Discoveries` section
- Affected branches updated with `## Notes from other branches`
- Index status set to `needs-revision` on affected nodes
- Claude reads index skeleton (already in context) → loads only affected files → edits

**Depth 4-5:** breadcrumb in each file gives navigation context. Claude loads:
current file + breadcrumb chain (titles only) + sibling list + root summary.
Bounded context cost regardless of depth.

**Why files beat MCP here:** Sable-Point ran 14 sub-plans, 4,200 lines, multiple
sessions, structure held. JSON format corruption is the documented failure mode for
LLM-edited complex structures. Markdown is self-repairing. Index.json is small,
stable, targeted edits only — within reliable territory.

---

### 3. MCP → Developer Model Store Only (3 tools)

**Remove:** `set_quadrant`, `get_concept` (mid-session reads), `get_learner_context`,
planning tools (above), most of `session.py`

**Keep and evolve:** `learner_diary.py` → feeds knowledge graph

**New MCP shape — 3 tools:**

| Tool | Purpose |
|------|---------|
| `get_session_brief()` | Generate ~500 token developer model snapshot at session start |
| `record_observation(concept, evidence_type, observation)` | Append to diary (unchanged) |
| `compact(concept?)` | Trigger reflection pass — consolidate raw diary → graph nodes |

**What the session brief contains (~500 tokens):**
```
Developer: [name, role, experience signals]
Current project context: [what they're building]
Strong areas: [concepts with mastery/transfer evidence]
ZPD boundaries: [concepts with gaps/struggle entries]
Watch for: [recurring blindspots, deflection patterns]
Engagement signals: [recent passive/active trend]
Active plan: [current .claude/plans/ root task if any]
```

This replaces ALL mid-session reads. Claude loads it once at start, works from it.
No `get_concept` calls needed — the brief already surfaces the relevant ZPD info.
Quadrant is determined from the brief by Claude at session start, updated continuously
from live conversation observation — no tool call needed for transitions.

---

### 4. Developer Model Store (knowledge graph)

The diary grows to hundreds of sessions. Needs rich representation for:
- ZPD boundary detection ("is this person ready for concurrent React?")
- Blindspot tracking across projects
- Preference/style modeling
- Scaffolding fade decisions

**Diary entry types (extended):**

The existing 11 evidence types (gap → acknowledgment → explanation → ... → transfer)
cover observations about the developer. Add one new type:

- `calibration` — Claude journaling to itself about adjusting engagement strategy.
  Not an observation about the developer — Claude's own reasoning voice.
  Counts toward the session total; happens only when a genuine strategy shift occurs.

**Recording discipline — aim for 2-3 diary entries per session total (across all types):**

The diary builds a model of a person across sessions. Some signals within a session
are genuinely strong — a clear demonstration, an accurate self-report, a revealing
mistake. Others are noise. There's no hard rule: be wary of overfitting, treat
it as a multi-session process, and hold single-session observations lightly unless
the signal is unusually clear.

Rules:
- **Prefer high-confidence observations.** When uncertain, either don't record or record
  the uncertainty explicitly: "may be navigating by intuition — needs more sessions to confirm."
- **Single-session signals are weak.** Cross-session patterns are what the diary is for.
- **2-3 entries per session is the target.** If you're recording more, you're overfitting.
- **Calibration entries count toward the total** — they're not free.
- **`record_observation` returns silently (`ok` only)** — diary content is Claude's
  private working memory, not a report card for the developer.

Graph edges (in the knowledge graph) accumulate confidence across sessions. A `conflates`
edge needs to appear in multiple sessions before shaping the session brief. One confused
exchange is noise. Three sessions with the same confusion is a structural gap worth acting on.

Example:
```markdown
### 2026-03-14T15:30:00Z [calibration]
Three rubber-stamps on schema decisions. Feels like overwhelm not disinterest.
Shifting SP → Sparring. Will surface the FK tradeoff explicitly rather than
presenting a solution. If engagement picks up, move back to SP.
```

Lives in the same concept diary file as knowledge entries (calibration is usually
concept-triggered). Clearly distinct by type tag — Claude's voice, not evidence.
Compaction extracts strategy patterns: "rubber-stamping on DB schema = overwhelm,
smaller batches + explicit tradeoffs was the fix." Feeds session brief as strategy
recommendation.

**Three layers:**

```
Raw diary entries (append-only, narrative markdown per concept)
    ↓ compact() — reflection pass
Concept nodes (summary + evidence distribution + strongest signal)
    ↓ graph construction
Knowledge graph: concepts, mental models, blindspots, preferences,
    skill edges, ZPD relationships
    ↓ get_session_brief()
~500 token inject at session start
```

**Graph nodes:**
- Concepts (`async/await`, `database transactions`, `React hooks`)
- Mental models (`thinks of Redux as global variable store`)
- Blindspots (`underestimates cascade effects in schema changes`)
- Preferences (`bottom-up explanation`, `gets frustrated by over-explanation`)

**Graph edges:**
- `understands_via` (concept → concept, with evidence type)
- `conflates` (concept ↔ concept — confusion signal)
- `unlocks` (concept → concept — ZPD relationship)
- `avoids` (concept — anxiety/deflection signal)
- `built_on` (concept → concept — mastery path)

**Local embedded store:** Kuzu (embedded graph DB, Python bindings, Cypher queries,
no server process) or NetworkX + SQLite as fallback. No external services.

**Compaction (reflection pass):**
LangMem reflection pattern — take N raw diary entries for a concept, run synthesis:
"Given these observations, what does this developer's current understanding of
[concept] look like? What are the gaps? What's the strongest signal?"
Output becomes the concept node summary. Raw entries archived, not deleted.

Triggers: on `compact()` call, or automatically when concept exceeds N entries.

---

### 5. SKILL.md Gets Heavier

v0 SKILL.md was lean because MCP was doing state work. In v1 MCP does less
mid-session, so SKILL.md carries more posture:

- Pre-diff preamble (mandatory, hard requirement)
- Session brief slot (injected dynamically at start)
- Quadrant table (unchanged — Claude determines from brief, mode-locks)
- Planning file conventions (how to create/update .claude/plans/)
- Theory check posture (unchanged)
- Anti-rationalization reference (unchanged)

Session start injection becomes:
```
[SKILL.md core]
[Session brief from get_session_brief()]
[Active plan root if .claude/plans/index.json exists]
```

Three blocks, injected once. Nothing injected mid-session except on explicit tool call.

---

## What This Removes

| Component | Removed | Replaced By |
|-----------|---------|-------------|
| `server/plan_tree.py` | ✓ | `.claude/plans/` file convention |
| `plan_step`, `complete_step`, `get_plan_state` tools | ✓ | writing-plans / executing-plans skills |
| `set_quadrant` tool | ✓ | Mode-lock from session brief |
| Mid-session `get_concept` reads | ✓ | Session brief covers ZPD state |
| `session.py` quadrant/plan state | ✓ | Brief + SKILL.md |
| MCP planning state in `~/.vygotsky/plans/` | ✓ | `.claude/plans/` in project |

---

## What This Adds

| Component | Purpose |
|-----------|---------|
| Knowledge graph store (Kuzu) | Rich developer model, traversable |
| Session brief generation | One-shot context load, replaces mid-session reads |
| Compaction / reflection pass | Diary stays manageable, signal improves over time |
| `.claude/plans/` file convention | Lightweight, git-tracked, depth 4-5 |
| Pre-diff preamble requirement | Directs attention before overwhelming with code |

---

## Phasing

### Phase 1 — Quick wins, no architecture change (1-2 days)
1. Add pre-diff preamble to SKILL.md (mandatory, hard requirement)
2. Remove `set_quadrant` tool — quadrant is ephemeral, lives in Claude's reasoning
3. Rewrite `brainstorming` skill — recursive hierarchical planning handoff, supersedes superpowers
4. Rewrite `writing-plans` skill — file-based plan tree (.claude/plans/ convention, depth 4-5,
   breadcrumbs, index.json, Discoveries sections for cross-cutting updates)
5. Update `executing-plans` skill — reads/updates plan files, no MCP calls
6. Remove planning MCP tools (plan_step, complete_step, get_plan_state, plan_tree.py)
7. Add `calibration` evidence type to learner_diary.py
8. Update tests

### Phase 2 — Session brief + MCP reduction (3-5 days)
1. Design session brief format + generation logic
2. Rewrite `get_session_state` → `get_session_brief` (generates snapshot from diary + graph)
3. Remove mid-session `get_concept` pattern from SKILL.md + skills
4. Rewrite session-start hook to inject brief
5. MCP down to 3 tools
6. Update tests

### Phase 3 — Knowledge graph + compaction (1-2 weeks)
1. Research Kuzu vs NetworkX+SQLite for local graph store
2. Design graph schema (nodes, edges, evidence → graph properties)
3. Implement graph construction from diary
4. Implement compaction / reflection pass
5. Enrich session brief with graph-derived ZPD + blindspot data
6. Update tests

---

## Success Criteria

- Dartboard-style session: theory-building quality maintained or improved
- MCP tool calls per session: ≤ 2 (record_observation at natural moments, brief at start)
- Pre-diff preamble: present in every code change, felt as useful not bureaucratic
- Plan depth 4-5: works across sessions, cross-cutting updates handled
- Context bloat: measurably reduced vs v0 (track tool call count per session)
