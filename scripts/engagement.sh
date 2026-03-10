#!/usr/bin/env bash
# Engagement signal tracker. Runs on UserPromptSubmit.
# Writes engagement data to ~/.vygotsky/engagement_signals.json
# Outputs system-reminder context when passive alarm triggers.

INPUT=$(cat)

mkdir -p "$HOME/.vygotsky"

# Pass the full JSON input to Python via stdin (avoids shell injection)
echo "$INPUT" | python3 -c "
import json, sys
from pathlib import Path

data = json.load(sys.stdin)
prompt = data.get('prompt', '')

state_file = Path.home() / '.vygotsky' / 'engagement_signals.json'

# Load current state
state = {}
if state_file.exists():
    try:
        state = json.loads(state_file.read_text())
    except Exception:
        pass

passive_patterns = {
    'y','yes','ok','okay','lgtm','sure','fine','go ahead',
    'do it','yep','yeah','k','sounds good','proceed','continue',
    'approved','approve','ack','roger','whatever','just do it',
    'idk','skip','dont care',\"i don't care\",\"doesn't matter\"
}
normalized = prompt.strip().lower().rstrip('.,!?')

consecutive = state.get('consecutive_passive', 0)
if normalized in passive_patterns:
    consecutive += 1
else:
    consecutive = 0

state['consecutive_passive'] = consecutive
state['last_prompt_length'] = len(prompt.split())
state_file.write_text(json.dumps(state, indent=2))

# Output context injection if passive alarm
if consecutive >= 3:
    result = {
        'additionalContext': (
            '<system-reminder>'
            f'ENGAGEMENT ALERT: {consecutive} consecutive passive responses. '
            'The user may be rubber-stamping. Before proceeding with any '
            'mutating operation, re-engage: surface a trade-off, ask about '
            'their mental model, or explain why the next step matters.'
            '</system-reminder>'
        )
    }
    print(json.dumps(result))
"
