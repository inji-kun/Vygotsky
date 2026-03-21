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

# Check if last human prompt was passive (using node instead of python3)
last_passive=$(node -e "
const fs = require('fs');
const path = require('path');
const os = require('os');
const logPath = path.join(os.homedir(), '.vygotsky', 'engagement.json');
try {
  const lines = fs.readFileSync(logPath, 'utf8').trim().split('\n').filter(Boolean);
  if (!lines.length) { console.log('false'); process.exit(); }
  const last = JSON.parse(lines[lines.length - 1]);
  console.log(last.passive ? 'true' : 'false');
} catch { console.log('false'); }
" 2>/dev/null || echo "false")

if [ "$last_passive" = "true" ]; then
    echo "$count" > "$NUDGE_FILE"
fi

exit 0
