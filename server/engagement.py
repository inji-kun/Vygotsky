"""Engagement Signal Log — narrative engagement tracking.

Same philosophy as the diary: log raw signals, let Claude judge qualitatively.
No numeric scores. No EWMA. Just facts about what the user said.

The hook writes signals. The server reads them. Claude interprets.

Storage: ~/.vygotsky/engagement.json (JSON lines, one per prompt)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Passive acceptance patterns — rubber-stamping responses
PASSIVE_PATTERNS = {
    "y", "yes", "ok", "okay", "lgtm", "sure", "fine", "go ahead",
    "do it", "yep", "yeah", "k", "sounds good", "proceed", "continue",
    "approved", "approve", "ack", "roger",
    "ship it", "merge it", "+1", "no changes needed", "looks good",
}

# Deflection patterns — explicitly avoiding engagement
DEFLECTION_PATTERNS = {
    "idk", "i don't know", "i dont know", "no idea", "just do it",
    "whatever", "you decide", "skip", "doesn't matter", "dont care",
    "i don't care", "not sure",
}

PASSIVE_LIMIT = 3


@dataclass
class EngagementTracker:
    """Reads the engagement signal log and provides summary signals.

    INVARIANT: The log file is append-only JSON lines.
    INVARIANT: No numeric scores. Claude judges qualitatively.
    """
    state_path: Path

    def __post_init__(self):
        self.state_path = Path(self.state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def record_signal(self, prompt: str, passive: bool, deflection: bool) -> None:
        """Append a signal entry to the log."""
        from server.util import atomic_write

        entry = json.dumps({
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "passive": passive,
            "deflection": deflection,
            "prompt": prompt,
        })

        # Append to log file
        if self.state_path.exists():
            content = self.state_path.read_text()
            atomic_write(self.state_path, content + entry + "\n")
        else:
            atomic_write(self.state_path, entry + "\n")

    def record_prompt(self, prompt: str) -> None:
        """Classify and record a user prompt."""
        normalized = prompt.strip().lower().rstrip(".,!?")
        passive = normalized in PASSIVE_PATTERNS
        deflection = normalized in DEFLECTION_PATTERNS
        self.record_signal(prompt, passive=passive or deflection, deflection=deflection)

    def _read_log(self) -> list[dict]:
        """Read all signal entries from the log file."""
        if not self.state_path.exists():
            return []
        entries = []
        for line in self.state_path.read_text().strip().split("\n"):
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return entries

    def recent_signals(self, n: int = 10) -> list[dict]:
        """Return the last N signal entries for Claude to read qualitatively."""
        return self._read_log()[-n:]

    @property
    def consecutive_passive(self) -> int:
        """Count consecutive passive signals from the end of the log."""
        entries = self._read_log()
        count = 0
        for entry in reversed(entries):
            if entry.get("passive"):
                count += 1
            else:
                break
        return count

    @property
    def consecutive_deflection(self) -> int:
        """Count consecutive deflection signals from the end of the log."""
        entries = self._read_log()
        count = 0
        for entry in reversed(entries):
            if entry.get("deflection"):
                count += 1
            else:
                break
        return count

    def is_passive_alarm(self) -> bool:
        """Check if consecutive passive responses exceed the limit."""
        return self.consecutive_passive >= PASSIVE_LIMIT

    def get_signals(self) -> dict:
        """Return engagement signals for Claude to interpret qualitatively."""
        return {
            "recent_signals": self.recent_signals(),
            "consecutive_passive": self.consecutive_passive,
            "consecutive_deflection": self.consecutive_deflection,
            "is_passive_alarm": self.is_passive_alarm(),
        }

    def reset_session(self) -> None:
        """Reset the log for a new session. Called by SessionStart hook."""
        from server.util import atomic_write
        atomic_write(self.state_path, "")
