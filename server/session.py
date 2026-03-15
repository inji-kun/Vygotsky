"""Session Manager — composes diary and engagement state.

Quadrant determination happens in Claude's reasoning (from diary + engagement
signals), not in server state. Planning lives in .claude/plans/ files, not here.
"""

from __future__ import annotations

from pathlib import Path

from server.learner_diary import LearnerDiary
from server.engagement import EngagementTracker

DEFAULT_STATE_DIR = Path.home() / ".vygotsky"


class Session:
    """Composes diary and engagement state.

    INVARIANT: diary and engagement are initialized on construction.
    """

    def __init__(self, state_dir: Path | None = None):
        self.state_dir = state_dir or DEFAULT_STATE_DIR
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.diary = LearnerDiary(self.state_dir / "diary")
        self.engagement = EngagementTracker(self.state_dir / "engagement.json")

    def get_state(self) -> dict:
        """Get orientation context: diary and engagement signals."""
        return {
            "diary": self.diary.get_context(),
            "engagement": self.engagement.get_signals(),
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
                strength_order = [
                    "transfer", "directive", "design_decision", "disagreement",
                    "prediction", "explanation", "application",
                    "correction", "connection", "extension",
                    "question", "gap", "acknowledgment", "calibration",
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
