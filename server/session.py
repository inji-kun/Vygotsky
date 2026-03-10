"""Session Manager — composes diary, engagement, plan tree, and quadrant state.

The session does NOT compute the quadrant — it stores Claude's qualitative
judgment and provides it back on request. All quadrant determination happens
in SKILL.md via Claude reading the diary + engagement signals.
"""

from __future__ import annotations

from pathlib import Path

from server.learner_diary import LearnerDiary
from server.engagement import EngagementTracker
from server.plan_tree import PlanTree
from server.quadrants import get_quadrant_guidance, get_transition_message, QUADRANTS

DEFAULT_STATE_DIR = Path.home() / ".vygotsky"


class Session:
    """Composes all Vygotsky state into a single session interface.

    INVARIANT: diary, engagement, and plan_tree are initialized on construction.
    INVARIANT: _quadrant is always a valid quadrant string.
    """

    def __init__(self, state_dir: Path | None = None):
        self.state_dir = state_dir or DEFAULT_STATE_DIR
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.diary = LearnerDiary(self.state_dir / "diary")
        self.engagement = EngagementTracker(self.state_dir / "engagement.json")
        self.plan_tree = PlanTree(self.state_dir / "plans")
        self._quadrant: str = "senior_peer"  # safe default

    def set_quadrant(self, quadrant: str) -> dict:
        """Set the current quadrant. Returns guidance + transition message."""
        if quadrant not in QUADRANTS:
            return {"error": f"Invalid quadrant: {quadrant}. Must be one of {QUADRANTS}"}

        old = self._quadrant
        self._quadrant = quadrant
        transition = get_transition_message(old, quadrant)

        return {
            "quadrant": quadrant,
            "guidance": get_quadrant_guidance(quadrant),
            "transition": transition,
        }

    def get_state(self) -> dict:
        """Get everything Claude needs to orient itself."""
        return {
            "diary": self.diary.get_context(),
            "engagement": self.engagement.get_signals(),
            "quadrant": {
                "current": self._quadrant,
                "guidance": get_quadrant_guidance(self._quadrant),
            },
            "plan": self.plan_tree.get_plan_state(),
        }

    def should_theory_check(self, concept: str) -> dict:
        """Check what we know before proceeding with a concept.

        Returns diary entries + engagement signals so Claude can decide
        whether to theory-check. The server doesn't decide — Claude does.
        """
        entries = self.diary.read(concept)
        diary_text = ""
        if entries:
            diary_text = "\n\n".join(
                f"### {e['timestamp']}\n{e['observation']}" for e in entries
            )

        return {
            "concept": concept,
            "has_diary_entries": len(entries) > 0,
            "diary_context": diary_text,
            "linked_concepts": self.diary.get_links(concept),
            "engagement_signals": self.engagement.get_signals(),
        }
