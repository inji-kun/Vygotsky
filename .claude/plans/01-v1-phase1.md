# v1 Phase 1 — Quick Wins
**ID:** 01
**Breadcrumb:** v1 Phase 1
**Status:** active
**Children:** 01-01, 01-02, 01-03, 01-04, 01-05, 01-06, 01-07, 01-08, 01-09

## Goal
Reduce MCP overhead and improve interaction quality without touching the core
architecture. No knowledge graph, no session brief yet. Just: pre-diff preamble,
kill planning MCP, rewrite planning skills to file-based, add calibration type,
tighten diary discipline.

## Steps
See child plans 01-01 through 01-09.

## Constraints
- Branch: `v1-phase1` off main
- Tests must pass after each removal
- Don't touch learner_diary.py core logic (except adding calibration type)
- Don't touch engagement.py
- Don't touch hardgate.sh
