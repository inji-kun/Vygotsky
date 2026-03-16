#!/usr/bin/env bash
# PostToolUse: increment burst counter on write operations.
# Resets to 0 each time the Stop hook fires.

mkdir -p "$HOME/.vygotsky"
COUNTER_FILE="$HOME/.vygotsky/burst_counter"

count=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
echo $((count + 1)) > "$COUNTER_FILE"

exit 0
