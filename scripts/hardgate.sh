#!/usr/bin/env bash
# HARD-GATE: theory-check layer on top of Claude Code's permission system.
#
# Instead of blocking destructive operations outright, this injects a
# requirement that the USER must demonstrate they understand what the
# operation does before Claude proceeds. Claude Code's own permission
# prompt still fires — this ensures the "allow" is informed, not zombie-mode.
#
# Exit 0 + additionalContext = allow but inject theory-check requirement.
# Exit 0 with no output = allow silently (safe operation).

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_name',''))")
TOOL_INPUT=$(echo "$INPUT" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin).get('tool_input',{})))")

# Only gate Bash, Write, Edit, MultiEdit, NotebookEdit
case "$TOOL_NAME" in
    Bash|Write|Edit|MultiEdit|NotebookEdit) ;;
    *) exit 0 ;;
esac

# Helper: emit a theory-check injection and exit
theory_check() {
    local OPERATION="$1"
    local CONSEQUENCE="$2"
    cat <<EOJSON
{"additionalContext": "<system-reminder>THEORY-CHECK REQUIRED: You are about to perform a destructive operation: ${OPERATION}. Before proceeding, you MUST ask the user to explain IN THEIR OWN WORDS what this operation will do and what the consequences are. A one-word answer ('yes', 'ok', 'do it') is NOT sufficient. The onus is on the user to demonstrate they understand the blast radius. Do not execute until they have. Consequence hint for your reference: ${CONSEQUENCE}</system-reminder>"}
EOJSON
    exit 0
}

# --- Destructive filesystem operations ---
if echo "$TOOL_INPUT" | grep -qiE 'rm\s+-rf|rm\s+-r\s'; then
    theory_check "recursive delete (rm -rf)" "Permanently removes files/directories. No undo. Check what's in the target path."
fi

# --- Destructive git operations ---
if echo "$TOOL_INPUT" | grep -qiE 'git\s+push\s+--force|git\s+push\s+-f\b'; then
    theory_check "git force push" "Overwrites remote history. Other collaborators' work may be lost. Commits on remote not in local will be destroyed."
fi

if echo "$TOOL_INPUT" | grep -qiE 'git\s+reset\s+--hard|git\s+clean\s+-f'; then
    theory_check "destructive git reset/clean" "Discards uncommitted changes permanently. Working directory modifications and staged changes will be lost."
fi

# --- Destructive database operations ---
if echo "$TOOL_INPUT" | grep -qiE 'DROP\s+TABLE|DELETE\s+FROM\s+\w+\s*;'; then
    theory_check "destructive database operation" "Data deletion may be irreversible. Check which table/rows are affected and whether backups exist."
fi

# --- Dangerous system operations ---
if echo "$TOOL_INPUT" | grep -qiE 'chmod\s+777|curl.*\|\s*(ba)?sh'; then
    theory_check "dangerous system operation" "chmod 777 makes files world-writable. Piped remote execution runs unreviewed code with your permissions."
fi

# --- Package publishing ---
if echo "$TOOL_INPUT" | grep -qiE 'npm\s+publish|pip\s+upload|cargo\s+publish'; then
    theory_check "package publishing" "Publishes to a public registry. Version numbers may be permanently consumed. Published packages can be installed by anyone."
fi

# --- Secrets/credentials (write only) ---
if echo "$TOOL_INPUT" | grep -qiE '\.env|credentials|secrets'; then
    if [ "$TOOL_NAME" = "Write" ] || [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "MultiEdit" ]; then
        theory_check "writing to secrets/credentials file" "Secrets files may be committed to git or exposed in logs. Verify .gitignore coverage and access controls."
    fi
fi

exit 0
