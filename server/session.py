"""Session Manager — composes diary and engagement state.

Quadrant determination happens in Claude's reasoning (from diary + engagement
signals), not in server state. Planning lives in .claude/plans/ files, not here.
"""

from __future__ import annotations

from pathlib import Path

from server.learner_diary import LearnerDiary, LINK_PATTERN
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
        """Record a diary entry and update the knowledge graph atomically."""
        self.diary.record(concept, observation, evidence_type=evidence_type)
        linked = LINK_PATTERN.findall(observation)
        self.graph.update_from_entry(concept, evidence_type, linked)

    def get_state(self) -> dict:
        """Get raw orientation data: diary and engagement signals."""
        return {
            "diary": self.diary.get_context(),
            "engagement": self.engagement.get_signals(),
        }

    def generate_brief(self) -> str:
        """Generate a ~500 token session brief — structured developer model snapshot.

        Uses knowledge graph when available (richer summaries + relationships).
        Falls back to raw diary entry analysis for new developers.
        """
        concepts = self.diary.list_concepts()
        engagement = self.engagement.get_signals()

        lines = ["## Developer Session Brief"]

        # --- Strong areas ---
        # Prefer graph summaries (compacted) over raw entry counts
        graph_strong = self.graph.get_strong_concepts(min_confidence=0.3)
        if graph_strong:
            lines.append("\n**Strong areas** (from knowledge graph):")
            for node in graph_strong[:5]:
                concept = node["concept"]
                if node["compacted"] and node["summary"]:
                    # Rich: use compacted summary
                    lines.append(f"  - **{concept}**: {node['summary'][:100]}")
                else:
                    lines.append(
                        f"  - {concept} (confidence: {node['confidence']:.2f}, "
                        f"{node['entry_count']} entries)"
                    )
                # Surface key associations
                assoc = self.graph.get_associated_concepts(concept)[:2]
                if assoc:
                    links = ", ".join(a["concept"] for a in assoc)
                    lines.append(f"    ↳ linked to: {links}")
        else:
            # Fall back: scan diary directly
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
                    lines.append(f"  - {concept} ({n} entries, strongest: {evidence})")
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
                node = self.graph.get_concept_node(concept)
                conf = node["confidence"] if node else 0.0
                zpd.append((concept, len(entries), conf))

        if zpd:
            lines.append("\n**ZPD boundaries** (gaps or struggles observed):")
            for concept, n, conf in zpd[:4]:
                lines.append(f"  - {concept} ({n} entries, confidence: {conf:.2f})")
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

        # --- Graph stats ---
        if self.graph.node_count() > 0:
            lines.append(
                f"\n_Graph: {self.graph.node_count()} concepts, "
                f"{self.graph.edge_count()} associations._"
            )
        else:
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
