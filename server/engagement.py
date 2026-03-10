"""Engagement Tracker — structural signal analysis for user engagement.

Tracks behavioral signals: prompt length, question marks, specificity markers,
passive acceptance patterns, and sustained engagement (flow state).

Ported from mini-agent-fork/engagement.py, simplified for MCP server use.
The hook writes engagement data to a state file; the MCP server reads it.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

# Passive acceptance patterns — responses indicating rubber-stamping
PASSIVE_PATTERNS = {
    "y", "yes", "ok", "okay", "lgtm", "sure", "fine", "go ahead",
    "do it", "yep", "yeah", "k", "sounds good", "proceed", "continue",
    "approved", "approve", "ack", "roger",
}

# Deflection patterns — user explicitly avoiding engagement
DEFLECTION_PATTERNS = {
    "idk", "i don't know", "i dont know", "no idea", "just do it",
    "whatever", "you decide", "skip", "doesn't matter", "dont care",
    "i don't care", "not sure",
}


@dataclass
class EngagementTracker:
    """Tracks learner engagement within and across sessions.

    INVARIANT: consecutive_passive counts consecutive passive/deflection responses.
    INVARIANT: current_score is EWMA over recent signal scores.
    """
    state_path: Path
    current_score: float = 0.7
    consecutive_passive: int = 0
    flow_state_start: float | None = None
    _scores: list[float] = field(default_factory=list)

    # Config
    window_size: int = 10
    passive_limit: int = 3
    flow_threshold_seconds: float = 45.0

    def __post_init__(self):
        self.state_path = Path(self.state_path)
        self._load()

    def record_prompt(self, prompt: str) -> None:
        """Record a user prompt and update engagement signals."""
        normalized = prompt.strip().lower().rstrip(".,!?")

        if normalized in PASSIVE_PATTERNS or normalized in DEFLECTION_PATTERNS:
            self.consecutive_passive += 1
            score = 0.1 if normalized in DEFLECTION_PATTERNS else 0.2
            self.flow_state_start = None
        else:
            self.consecutive_passive = 0
            score = _score_prompt(prompt)
            if score >= 0.5:
                if self.flow_state_start is None:
                    self.flow_state_start = time.time()
            else:
                self.flow_state_start = None

        self._scores.append(score)
        if len(self._scores) > self.window_size:
            self._scores = self._scores[-self.window_size:]
        self.current_score = _ewma(self._scores)
        self.save()

    def is_passive_alarm(self) -> bool:
        """Check if consecutive passive responses exceed the limit."""
        return self.consecutive_passive >= self.passive_limit

    def is_in_flow(self) -> bool:
        """Check if the user is in a sustained flow state."""
        if self.flow_state_start is None:
            return False
        return (time.time() - self.flow_state_start) >= self.flow_threshold_seconds

    def get_signals(self) -> dict:
        """Return a summary of current engagement signals."""
        return {
            "current_score": round(self.current_score, 2),
            "consecutive_passive": self.consecutive_passive,
            "is_passive_alarm": self.is_passive_alarm(),
            "is_in_flow": self.is_in_flow(),
        }

    def save(self) -> None:
        """Persist engagement state to disk."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "current_score": self.current_score,
            "consecutive_passive": self.consecutive_passive,
            "flow_state_start": self.flow_state_start,
            "scores": self._scores,
        }
        self.state_path.write_text(json.dumps(data, indent=2))

    def _load(self) -> None:
        """Load engagement state from disk if it exists."""
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text())
                self.current_score = data.get("current_score", 0.7)
                self.consecutive_passive = data.get("consecutive_passive", 0)
                self.flow_state_start = data.get("flow_state_start")
                self._scores = data.get("scores", [])
            except (json.JSONDecodeError, KeyError):
                pass


def _ewma(values: list[float], alpha: float = 0.3) -> float:
    """Exponentially weighted moving average. Recent signals weighted more."""
    if not values:
        return 0.7
    result = values[0]
    for v in values[1:]:
        result = alpha * v + (1 - alpha) * result
    return result


def _score_prompt(prompt: str) -> float:
    """Score a user prompt by structural engagement indicators.

    Uses length, question marks, and specificity markers (file paths, line numbers,
    error messages). Not gameable by stuffing tech words.
    """
    words = prompt.split()
    if not words:
        return 0.0

    length_score = min(1.0, len(words) / 30.0)

    question_count = prompt.count("?")
    question_score = min(1.0, question_count * 0.4)

    specificity_signals = 0
    specificity_signals += sum(
        1 for w in words
        if "/" in w or w.endswith((".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".h", ".md"))
    )
    specificity_signals += len(re.findall(r"\blines?\s*\d+", prompt, re.IGNORECASE))
    specificity_signals += len(re.findall(r":\d+", prompt))
    specificity_signals += len(re.findall(
        r"\b(?:Error|Exception|Traceback|TypeError|ValueError|KeyError|AttributeError)\b",
        prompt,
    ))
    specificity_score = min(1.0, specificity_signals * 0.25)

    return 0.5 * length_score + 0.25 * question_score + 0.25 * specificity_score
