#!/usr/bin/env bash
# Stop hook: check burst size + last engagement signal.
# If writes happened and last response was passive, queue a nudge
# for the next turn via ~/.vygotsky/pending_nudge.

mkdir -p "$HOME/.vygotsky"
COUNTER_FILE="$HOME/.vygotsky/burst_counter"
NUDGE_FILE="$HOME/.vygotsky/pending_nudge"
ENGAGEMENT_FILE="$HOME/.vygotsky/engagement.json"

count=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
echo 0 > "$COUNTER_FILE"

# No writes this turn — nothing to nudge about
if [ "$count" -eq 0 ]; then
    exit 0
fi

# Check if last human prompt was passive
last_passive=$(python3 -c "
import json
from pathlib import Path

log = Path.home() / '.vygotsky' / 'engagement.json'
if not log.exists():
    print('false')
    exit()

lines = [l for l in log.read_text().strip().split('\n') if l.strip()]
if not lines:
    print('false')
    exit()

try:
    last = json.loads(lines[-1])
    print('true' if last.get('passive') else 'false')
except Exception:
    print('false')
" 2>/dev/null || echo "false")

if [ "$last_passive" = "true" ]; then
    echo "$count" > "$NUDGE_FILE"
fi

exit 0
