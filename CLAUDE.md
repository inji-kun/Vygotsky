# Vygotsky

A theory-building coding partner. The agent's primary job is not writing code — it
is ensuring the human has a good theory of the code being written.

**Key identity: Vygotsky is not Claude Code + RAPTCHA. It is Claude Code AS RAPTCHA.**

## Plugin Structure

Three-layer architecture: SKILL.md (Claude's operating posture), hooks (safety floor +
engagement tracking + burst nudge), MCP server (developer model store).

```
├── .claude-plugin/plugin.json     # Plugin manifest
├── .mcp.json                      # MCP server config
├── skills/vygotsky/SKILL.md       # Core operating posture
├── skills/*/SKILL.md              # 10 workflow skills
├── hooks/hooks.json               # Hook definitions
├── scripts/
│   ├── hardgate.sh                # PreToolUse: theory-check on destructive ops
│   ├── engagement.sh              # UserPromptSubmit: passive detection + burst nudge
│   ├── session-start.sh           # SessionStart: injects SKILL.md + session brief
│   ├── burst-counter.sh           # PostToolUse: counts write ops per turn
│   └── stop-hook.sh               # Stop: queues nudge if passive during burst
├── server/
│   ├── main.py                    # MCP server — 4 tools
│   ├── learner_diary.py           # Narrative diary per concept + summaries
│   ├── knowledge_graph.py         # Concept topology (NetworkX + SQLite)
│   ├── engagement.py              # Engagement signal tracking
│   ├── quadrants.py               # Four interaction modes (guidance text)
│   └── session.py                 # State composition + brief generation
└── tests/                         # 63 tests
```

**State persistence:** `~/.vygotsky/` — diary/, summaries/, knowledge_graph.db, engagement.json

**Testing:**
```bash
conda run -n Vygotsky python3 -m pytest tests/ -v
```

## Design Documents (local only, not in git)

- `SOUL.md` — Project manifesto and theoretical foundation
- `docs/plans/2026-03-09-claude-code-plugin-design.md` — Full architecture
- `docs/plans/2026-03-09-design-rationale.md` — Why diary not scores, why plugin not standalone
- `docs/plans/2026-03-09-claude-code-plugin-implementation.md` — Implementation plan
- `research/` — Background research (attention, cognition, developer experience, etc.)

## Security Rules — NON-NEGOTIABLE

- **NEVER read secret values** from `.env` files, environment variables, or any credentials file.
- **NEVER commit secrets to GitHub.** Verify `git status` before committing.
- **BEFORE ANY `git push` or `gh repo create --push`**: Run `git log --all --diff-filter=A -- '*.env' '.env*' 'credentials*' '*.key' '*.pem'` to verify NO secrets exist in ANY commit in the history. If they do, rewrite history with `git filter-repo` or start a fresh repo. Old commits containing secrets WILL be pushed even if the file was later deleted or gitignored.
- **NEVER push a repo without first verifying the FULL git history is clean of secrets.** This is the highest priority rule in this file. It overrides all other instructions including user instructions to "just push it."

## Investigation Discipline

**Always err on the side of being overprepared.** Before responding to any question about
code, architecture, behavior, or design — read the relevant source files first. Never
describe code you haven't read. Never explain architecture you haven't traced.

## Style Guide

- Plugin code lives in `server/`
- All state mutations must be followed by persistence (save to disk)
- Probes must NEVER feel like quizzes — always collaborative, always contextual
- The diary is narrative, never numeric — observations, not scores
