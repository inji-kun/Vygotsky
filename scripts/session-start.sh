#!/usr/bin/env bash
# SessionStart hook for Vygotsky plugin.
# 1. Writes a session marker to ~/.vygotsky/sessions/
# 2. On normal start: injects compact core SKILL.md into the conversation
# 3. On compaction: injects state-reload instruction (not full SKILL.md)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- Write session marker ---
SESSIONS_DIR="$HOME/.vygotsky/sessions"
mkdir -p "$SESSIONS_DIR"

# Read hook input to get session info
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id','unknown'))" 2>/dev/null || echo "unknown")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CWD=$(pwd)

# Write session marker
cat > "$SESSIONS_DIR/${TIMESTAMP//:/-}_${SESSION_ID}.json" <<MARKER
{
  "session_id": "$SESSION_ID",
  "started_at": "$TIMESTAMP",
  "cwd": "$CWD",
  "plugin_version": "0.2.0",
  "vygotsky_active": true
}
MARKER

# --- Inject context based on event type ---
SKILL_PATH="${PLUGIN_ROOT}/skills/vygotsky/SKILL.md"

if [ ! -f "$SKILL_PATH" ]; then
    echo '{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Error: Vygotsky SKILL.md not found"}}' >&2
    exit 1
fi

# Detect if this is a compaction resume
EVENT_TYPE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('type','startup'))" 2>/dev/null || echo "startup")

if [ "$EVENT_TYPE" = "compact" ]; then
    # Post-compaction: inject state reload instruction, NOT full SKILL.md
    echo "Vygotsky session resumed after compaction. Call get_session_state() immediately to re-orient on diary, engagement, quadrant, and plan state." | \
    python3 -c "
import json, sys
context = sys.stdin.read().strip()
wrapper = '<EXTREMELY_IMPORTANT>\n' + context + '\n</EXTREMELY_IMPORTANT>'
output = {'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': wrapper}}
print(json.dumps(output))
"
else
    # Normal start: inject compact core SKILL.md (Python handles all escaping)
    python3 -c "
import json, sys
context = sys.stdin.read()
wrapper = '<EXTREMELY_IMPORTANT>\nYou are Vygotsky — a theory-building coding partner.\n\n' + context + '\n</EXTREMELY_IMPORTANT>'
output = {'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': wrapper}}
print(json.dumps(output))
" < "$SKILL_PATH"
fi

exit 0
