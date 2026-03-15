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
        """Get raw orientation data: diary and engagement signals."""
        return {
            "diary": self.diary.get_context(),
            "engagement": self.engagement.get_signals(),
        }

    def generate_brief(self) -> str:
        """Generate a ~500 token session brief — structured snapshot of the
        developer model for injection at session start.

        Derives strong areas, ZPD boundaries, and watch-fors from diary evidence
        types. No knowledge graph yet (Phase 3) — works directly from diary entries.
        """
        concepts = self.diary.list_concepts()
        engagement = self.engagement.get_signals()

        # Categorise concepts by strongest evidence signal
        strong = []       # mastery-tier evidence
        zpd = []          # gap or struggle entries
        acknowledged = [] # acknowledgment-only (low signal)

        mastery_types = {"transfer", "directive", "design_decision", "disagreement",
                         "prediction", "explanation"}
        gap_types = {"gap", "correction"}

        for concept in concepts:
            entries = self.diary.read(concept)
            if not entries:
                continue
            types = {e.get("evidence_type", "acknowledgment") for e in entries}
            # Skip calibration-only entries — they're Claude's voice, not evidence
            signal_types = types - {"calibration", "acknowledgment"}
            if signal_types & mastery_types:
                strong.append((concept, len(entries), max(
                    (t for t in signal_types if t in mastery_types),
                    key=lambda t: list(mastery_types).index(t)
                )))
            elif signal_types & gap_types:
                zpd.append((concept, len(entries)))
            elif signal_types:
                acknowledged.append(concept)

        # Build brief text
        lines = ["## Developer Session Brief"]

        if strong:
            lines.append("\n**Strong areas** (demonstrated understanding):")
            for concept, n, evidence in strong[:6]:
                lines.append(f"  - {concept} ({n} entries, strongest: {evidence})")
        else:
            lines.append("\n**Strong areas:** None recorded yet.")

        if zpd:
            lines.append("\n**ZPD boundaries** (gaps or struggles observed):")
            for concept, n in zpd[:4]:
                lines.append(f"  - {concept} ({n} entries with gap/correction signals)")
        else:
            lines.append("\n**ZPD boundaries:** None flagged yet.")

        # Engagement summary
        lines.append("\n**Engagement:**")
        cp = engagement.get("consecutive_passive", 0)
        if engagement.get("is_passive_alarm"):
            lines.append(f"  ⚠ Passive alarm — {cp} consecutive passive responses. "
                         "Recalibrate before proceeding.")
        elif cp > 0:
            lines.append(f"  {cp} consecutive passive responses — monitor.")
        else:
            lines.append("  No passive alarm. Engagement signals normal.")

        recent = engagement.get("recent_signals", [])
        if recent:
            passive_count = sum(1 for s in recent if s.get("passive"))
            lines.append(f"  Recent: {passive_count}/{len(recent)} passive in last {len(recent)} signals.")

        # Calibration notes (Claude's own strategy history for this developer)
        calibration_notes = []
        for concept in concepts:
            entries = self.diary.read(concept)
            for e in entries:
                if e.get("evidence_type") == "calibration":
                    calibration_notes.append(e["observation"][:120])
        if calibration_notes:
            lines.append("\n**Strategy history** (your prior calibrations):")
            for note in calibration_notes[-2:]:  # last 2 only
                lines.append(f"  - {note}")

        if not strong and not zpd and not calibration_notes:
            lines.append("\n_New developer — no observations yet. Start in senior_peer posture._")

        return "\n".join(lines)

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
