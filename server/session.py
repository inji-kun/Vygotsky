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

# Short posture summaries for set_quadrant responses (~50 tokens each)
QUADRANT_POSTURES = {
    "extension": "Light touch. Trust their judgment. One sentence of reasoning before acting.",
    "sparring": "Surface trade-offs. Re-engage critical thinking. Make reasoning visible.",
    "senior_peer": "Collaborative scaffolding. Walk through step by step. Explain why before what.",
    "brake_pedal": "Slow down. Smaller steps. Confirm understanding before proceeding.",
}


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
        """Set the current quadrant. Returns posture + transition message."""
        if quadrant not in QUADRANTS:
            return {"error": f"Invalid quadrant: {quadrant}. Must be one of {QUADRANTS}"}

        old = self._quadrant
        self._quadrant = quadrant
        transition = get_transition_message(old, quadrant)

        return {
            "quadrant": quadrant,
            "posture": QUADRANT_POSTURES.get(quadrant, ""),
            "transition": transition,
        }

    def get_state(self) -> dict:
        """Get everything Claude needs to orient itself."""
        return {
            "diary": self.diary.get_context(),
            "engagement": self.engagement.get_signals(),
            "quadrant": {
                "current": self._quadrant,
                "posture": QUADRANT_POSTURES.get(self._quadrant, ""),
            },
            "plan": self.plan_tree.get_plan_state(),
        }

    def get_concept_summary(self, concept: str) -> dict:
        """Summary view: evidence quality + linked concepts + engagement."""
        entries = self.diary.read(concept)
        evidence_summary = self.diary.get_evidence_summary(concept)
        linked = self._get_linked_with_evidence(concept)

        return {
            "concept": concept,
            "has_diary_entries": len(entries) > 0,
            "evidence_summary": evidence_summary,
            "linked_concepts": linked,
            "engagement_signals": self.engagement.get_signals(),
        }

    def get_concept_full(self, concept: str) -> dict:
        """Full view: all entries + linked concepts with evidence."""
        entries = self.diary.read(concept)
        linked = self._get_linked_with_evidence(concept)

        return {
            "concept": concept,
            "entries": entries,
            "linked_concepts": linked,
        }

    def _get_linked_with_evidence(self, concept: str) -> list[dict]:
        """Get linked concepts with their evidence summaries."""
        links = self.diary.get_links(concept)
        result = []
        for link_name in links:
            link_entries = self.diary.read(link_name)
            if link_entries:
                types = [e.get("evidence_type", "acknowledgment") for e in link_entries]
                # Rank: mastery > learning > gap > acknowledgment
                strength_order = [
                    "directive", "design_decision", "disagreement",
                    "prediction", "explanation", "transfer", "application",
                    "question", "correction", "gap", "acknowledgment",
                ]
                strongest = "acknowledgment"
                for t in strength_order:
                    if t in types:
                        strongest = t
                        break
                result.append({
                    "concept": link_name,
                    "entries": len(link_entries),
                    "strongest_evidence": strongest,
                })
            else:
                result.append({
                    "concept": link_name,
                    "entries": 0,
                    "strongest_evidence": "none",
                })
        return result

    def should_theory_check(self, concept: str) -> dict:
        """Legacy method — use get_concept_summary instead."""
        return self.get_concept_summary(concept)
