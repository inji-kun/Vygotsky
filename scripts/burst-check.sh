#!/usr/bin/env bash
# PreToolUse: check burst counter before write operations.
# If writes exceed threshold, inject a system-reminder telling Claude
# to pause and let the human respond before continuing.

COUNTER_FILE="$HOME/.vygotsky/burst_counter"

count=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)

# Threshold: after 3 writes, nudge Claude to pause
if [ "$count" -ge 3 ]; then
    echo "{\"additionalContext\": \"<system-reminder>BURST PACING: You have made $count write operations this turn without human input. Stop after this operation. Let the human respond before continuing — they need a chance to absorb what just happened. Your preamble for the NEXT batch of work is not a substitute for their input.</system-reminder>\"}"
fi

exit 0
