#!/usr/bin/env bash
# Engagement signal logger. Runs on UserPromptSubmit.
# Writes one JSON line per prompt to ~/.vygotsky/engagement.json
# Outputs system-reminder context when passive alarm triggers.

INPUT=$(cat)

mkdir -p "$HOME/.vygotsky"

echo "$INPUT" | python3 -c "
import json, sys
from pathlib import Path
from datetime import datetime, timezone

data = json.load(sys.stdin)
prompt = data.get('prompt', '')
normalized = prompt.strip().lower().rstrip('.,!?')

passive_patterns = {
    'y','yes','ok','okay','lgtm','sure','fine','go ahead',
    'do it','yep','yeah','k','sounds good','proceed','continue',
    'approved','approve','ack','roger',
    'ship it','merge it','+1','no changes needed','looks good',
}

deflection_patterns = {
    'idk','i don\'t know','i dont know','no idea','just do it',
    'whatever','you decide','skip','doesn\'t matter','dont care',
    'i don\'t care','not sure',
}

passive = normalized in passive_patterns or normalized in deflection_patterns
deflection = normalized in deflection_patterns

# Append signal to log
log_path = Path.home() / '.vygotsky' / 'engagement.json'
entry = json.dumps({
    'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'passive': passive,
    'deflection': deflection,
    'prompt': prompt,
})

with open(log_path, 'a') as f:
    f.write(entry + '\n')

# Count consecutive passive from end of log
consecutive = 0
if log_path.exists():
    lines = log_path.read_text().strip().split('\n')
    for line in reversed(lines):
        try:
            e = json.loads(line)
            if e.get('passive'):
                consecutive += 1
            else:
                break
        except Exception:
            break

context_parts = []

# Burst nudge from previous turn (written by stop-hook.sh)
# Only inject if this prompt is ALSO passive — a substantive follow-up
# means the human is engaged and needs no nudge.
nudge_path = Path.home() / '.vygotsky' / 'pending_nudge'
if nudge_path.exists():
    try:
        burst_count = nudge_path.read_text().strip()
        nudge_path.unlink()
        if passive:
            context_parts.append(
                f'Burst complete: {burst_count} write operation(s) last turn, '
                'previous response was passive. Before starting the next burst, '
                'consider whether a theory check is warranted — your quadrant read '
                'and the diary should guide whether to ask or proceed.'
            )
    except Exception:
        pass

# Passive alarm
if consecutive >= 3:
    context_parts.append(
        f'ENGAGEMENT ALERT: {consecutive} consecutive passive responses. '
        'The user may be rubber-stamping. Before proceeding with any '
        'mutating operation, re-engage: surface a trade-off, ask about '
        'their mental model, or explain why the next step matters.'
    )

if context_parts:
    combined = '<system-reminder>' + ' | '.join(context_parts) + '</system-reminder>'
    print(json.dumps({'additionalContext': combined}))
" || exit 1
