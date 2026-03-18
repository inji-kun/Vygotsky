#!/usr/bin/env bash
# SessionStart hook for Vygotsky plugin.
# Injects three blocks at session start (once — nothing mid-session):
#   1. SKILL.md  — Claude's operating posture
#   2. Session brief — developer model snapshot (generated from diary)
#   3. Active plan  — .claude/plans/index.json if present in project dir
#
# On compaction: injects a lightweight state-reload instruction instead.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- Ensure state directory exists (first run on clean machine) ---
SESSIONS_DIR="$HOME/.vygotsky/sessions"
mkdir -p "$SESSIONS_DIR"

# --- Clear turn-level state from prior session ---
echo 0 > "$HOME/.vygotsky/burst_counter"
rm -f "$HOME/.vygotsky/pending_nudge"

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null || echo "unknown")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CWD=$(pwd)

cat > "$SESSIONS_DIR/${TIMESTAMP//:/-}_${SESSION_ID}.json" <<MARKER
{
  "session_id": "$SESSION_ID",
  "started_at": "$TIMESTAMP",
  "cwd": "$CWD",
  "plugin_version": "0.2.0",
  "vygotsky_active": true
}
MARKER

# --- Detect event type ---
EVENT_TYPE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('type','startup'))" 2>/dev/null || echo "startup")

SKILL_PATH="${PLUGIN_ROOT}/skills/vygotsky/SKILL.md"

if [ ! -f "$SKILL_PATH" ]; then
    echo '{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Error: Vygotsky SKILL.md not found"}}' >&2
    exit 1
fi

if [ "$EVENT_TYPE" = "compact" ]; then
    # Post-compaction: lightweight reload instruction only
    python3 -c "
import json, sys
msg = ('Vygotsky session resumed after compaction. '
       'Call get_session_brief() immediately to re-orient on the developer model. '
       'Then check .claude/plans/index.json if a plan is active.')
wrapper = '<EXTREMELY_IMPORTANT>\n' + msg + '\n</EXTREMELY_IMPORTANT>'
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': wrapper}}))
"
else
    # Normal start: generate brief + read plan index, inject all three blocks
    python3 -c "
import json, sys, os
from pathlib import Path

# Block 1: SKILL.md
skill_path = sys.argv[1]
skill = Path(skill_path).read_text()

# Block 2: Session brief (generated from diary)
try:
    sys.path.insert(0, sys.argv[2])  # plugin root on path
    from server.session import Session
    brief = Session().generate_brief()
except Exception as e:
    brief = f'(Session brief unavailable: {e})'

# Block 3: Active plan index (project-local, optional)
plan_index_path = Path(os.getcwd()) / '.claude' / 'plans' / 'index.json'
if plan_index_path.exists():
    try:
        plan_raw = plan_index_path.read_text()
        plan_block = '## Active Plan Index\n```json\n' + plan_raw + '\n```'
    except Exception:
        plan_block = ''
else:
    plan_block = ''

# Assemble context
parts = ['You are Vygotsky — a theory-building coding partner.\n', skill]
parts.append('\n---\n')
parts.append(brief)
if plan_block:
    parts.append('\n---\n')
    parts.append(plan_block)

context = '\n'.join(parts)
wrapper = '<EXTREMELY_IMPORTANT>\n' + context + '\n</EXTREMELY_IMPORTANT>'
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': wrapper}}))
" "$SKILL_PATH" "$PLUGIN_ROOT"
fi

exit 0
