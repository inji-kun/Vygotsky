#!/usr/bin/env bash
# SessionStart hook for Vygotsky plugin.
# 1. Writes a session marker to ~/.vygotsky/sessions/
# 2. Injects core Vygotsky SKILL.md into the conversation (like superpowers injects using-superpowers)

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
  "plugin_version": "0.1.0",
  "vygotsky_active": true
}
MARKER

# --- Inject core skill content ---
escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

SKILL_CONTENT=$(cat "${PLUGIN_ROOT}/skills/vygotsky/SKILL.md" 2>&1 || echo "Error reading Vygotsky SKILL.md")
SKILL_ESCAPED=$(escape_for_json "$SKILL_CONTENT")

SESSION_CONTEXT="<EXTREMELY_IMPORTANT>\nYou are Vygotsky — a theory-building coding partner.\n\n**Below is your core operating posture. For workflow-specific skills (debugging, TDD, planning, etc.), use the Skill tool:**\n\n${SKILL_ESCAPED}\n</EXTREMELY_IMPORTANT>"

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "${SESSION_CONTEXT}"
  }
}
EOF

exit 0
