"""Session Manager — composes diary and engagement state.

Quadrant determination happens in Claude's reasoning (from diary + engagement
signals), not in server state. Planning lives in .claude/plans/ files, not here.
"""

from __future__ import annotations

from pathlib import Path

from server.learner_diary import LearnerDiary, LINK_PATTERN, slugify
from server.engagement import EngagementTracker
from server.knowledge_graph import KnowledgeGraph, MASTERY_TYPES, GAP_TYPES

DEFAULT_STATE_DIR = Path.home() / ".vygotsky"


class Session:
    """Composes diary, engagement, and knowledge graph state.

    INVARIANT: diary, engagement, and graph are initialized on construction.
    """

    def __init__(self, state_dir: Path | None = None):
        self.state_dir = state_dir or DEFAULT_STATE_DIR
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.diary = LearnerDiary(self.state_dir / "diary")
        self.engagement = EngagementTracker(self.state_dir / "engagement.json")
        self.graph = KnowledgeGraph(self.state_dir / "knowledge_graph.db")

    def record_observation(self, concept: str, observation: str, evidence_type: str = "acknowledgment") -> None:
        """Record a diary entry and update the knowledge graph atomically.
        Calibration entries are Claude's private strategy — skip graph update."""
        self.diary.record(concept, observation, evidence_type=evidence_type)
        if evidence_type == "calibration":
            return
        slug = slugify(concept)
        linked = list(set(slugify(c) for c in LINK_PATTERN.findall(observation)))
        self.graph.update_from_entry(slug, evidence_type, linked)

    def get_state(self) -> dict:
        """Get raw orientation data: diary and engagement signals."""
        return {
            "diary": self.diary.get_context(),
            "engagement": self.engagement.get_signals(),
        }

    def generate_brief(self) -> str:
        """Generate a ~500 token session brief — structured developer model snapshot.

        Strong areas and ZPD determined from diary evidence types.
        Concept summaries (if written by compact()) shown when available.
        Graph used only for topology (linked concepts).
        """
        concepts = self.diary.list_concepts()
        engagement = self.engagement.get_signals()

        lines = ["## Developer Session Brief"]

        # --- Developer-level summary (if compact("developer", ...) was called) ---
        dev_summary = self.diary.read_summary("developer")
        if dev_summary:
            lines.append(f"\n**Developer model:** {dev_summary[:200]}")

        # --- Strong areas ---
        strong = []
        for concept in concepts:
            entries = self.diary.read(concept)
            if not entries:
                continue
            types = {e.get("evidence_type", "acknowledgment") for e in entries}
            signal_types = types - {"calibration", "acknowledgment"}
            if signal_types & MASTERY_TYPES:
                strongest = next(
                    t for t in ["transfer", "directive", "design_decision",
                                "prediction", "explanation", "disagreement"]
                    if t in signal_types
                )
                strong.append((concept, len(entries), strongest))

        if strong:
            lines.append("\n**Strong areas** (demonstrated understanding):")
            for concept, n, evidence in strong[:5]:
                summary = self.diary.read_summary(concept)
                if summary:
                    lines.append(f"  - **{concept}**: {summary[:120]}")
                else:
                    lines.append(f"  - {concept} ({n} entries, strongest: {evidence})")
                # Surface key associations from graph topology
                assoc = self.graph.get_associated_concepts(concept)[:2]
                if assoc:
                    links = ", ".join(a["concept"] for a in assoc)
                    lines.append(f"    ↳ linked to: {links}")
        else:
            lines.append("\n**Strong areas:** None recorded yet.")

        # --- ZPD boundaries ---
        zpd = []
        for concept in concepts:
            entries = self.diary.read(concept)
            if not entries:
                continue
            types = {e.get("evidence_type", "acknowledgment") for e in entries}
            if types & GAP_TYPES:
                zpd.append((concept, len(entries)))

        if zpd:
            lines.append("\n**ZPD boundaries** (gaps or struggles observed):")
            for concept, n in zpd[:4]:
                lines.append(f"  - {concept} ({n} entries)")
        else:
            lines.append("\n**ZPD boundaries:** None flagged yet.")

        # --- Engagement ---
        lines.append("\n**Engagement:**")
        cp = engagement.get("consecutive_passive", 0)
        if engagement.get("is_passive_alarm"):
            lines.append(
                f"  ⚠ Passive alarm — {cp} consecutive passive responses. "
                "Recalibrate before proceeding."
            )
        elif cp > 0:
            lines.append(f"  {cp} consecutive passive responses — monitor.")
        else:
            lines.append("  No passive alarm.")

        recent = engagement.get("recent_signals", [])
        if recent:
            passive_count = sum(1 for s in recent if s.get("passive"))
            lines.append(
                f"  Recent: {passive_count}/{len(recent)} passive "
                f"in last {len(recent)} signals."
            )

        # --- Calibration history ---
        calibration_notes = []
        for concept in concepts:
            for e in self.diary.read(concept):
                if e.get("evidence_type") == "calibration":
                    calibration_notes.append(e["observation"][:120])
        if calibration_notes:
            lines.append("\n**Strategy history** (your prior calibrations):")
            for note in calibration_notes[-2:]:
                lines.append(f"  - {note}")

        if not concepts:
            lines.append("\n_New developer — no observations yet. Start in senior_peer posture._")
        elif self.graph.edge_count() > 0:
            lines.append(f"\n_{self.graph.edge_count()} concept associations tracked._")

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
        links = [slugify(l) for l in self.diary.get_links(concept)]
        result = []
        for link_name in links:
            link_entries = self.diary.read(link_name)
            if link_entries:
                types = [e.get("evidence_type", "acknowledgment") for e in link_entries]
                strength_order = [
                    "transfer", "directive", "design_decision", "disagreement",
                    "prediction", "explanation", "extension",
                    "correction", "connection",
                    "gap", "acknowledgment", "calibration",
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
