"""Knowledge Graph — persisted concept model built from diary observations.

Nodes: concepts with summary, confidence, entry count
Edges: associations derived from [[wiki-links]] in diary entries

Storage: SQLite for persistence across sessions, NetworkX for in-memory ops.
Confidence grows with evidence quality — mastery signals count more.

This is Phase 3 of the v1 architecture. The graph enriches the session brief
with summaries and relationships rather than raw entry counts.
"""

import sqlite3
import networkx as nx
from datetime import datetime, timezone
from pathlib import Path


MASTERY_TYPES = {
    "prediction", "explanation", "transfer",
    "directive", "design_decision", "disagreement",
}
GAP_TYPES = {"gap", "correction"}


class KnowledgeGraph:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.graph = nx.DiGraph()
        self._init_db()
        self._load()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    concept     TEXT PRIMARY KEY,
                    summary     TEXT    DEFAULT '',
                    confidence  REAL    DEFAULT 0.0,
                    entry_count INTEGER DEFAULT 0,
                    compacted   INTEGER DEFAULT 0,
                    updated_at  TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    source      TEXT,
                    target      TEXT,
                    edge_type   TEXT DEFAULT 'associated',
                    mentions    INTEGER DEFAULT 1,
                    updated_at  TEXT,
                    PRIMARY KEY (source, target, edge_type)
                )
            """)

    def _load(self):
        """Load persisted graph into NetworkX on startup."""
        with sqlite3.connect(self.db_path) as conn:
            for row in conn.execute(
                "SELECT concept, summary, confidence, entry_count, compacted FROM nodes"
            ):
                concept, summary, confidence, entry_count, compacted = row
                self.graph.add_node(
                    concept,
                    summary=summary,
                    confidence=confidence,
                    entry_count=entry_count,
                    compacted=bool(compacted),
                )
            for row in conn.execute(
                "SELECT source, target, edge_type, mentions FROM edges"
            ):
                source, target, edge_type, mentions = row
                self.graph.add_edge(source, target, edge_type=edge_type, mentions=mentions)

    def update_from_entry(
        self, concept: str, evidence_type: str, linked_concepts: list[str]
    ) -> None:
        """Update graph when a diary entry is recorded. Called automatically
        by Session.record_observation — not called directly."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Confidence: grows with evidence, higher for mastery signals
        current_conf = (
            self.graph.nodes[concept].get("confidence", 0.0)
            if concept in self.graph else 0.0
        )
        boost = 0.1 if evidence_type in MASTERY_TYPES else 0.03
        confidence = min(1.0, current_conf + boost)

        entry_count = (
            self.graph.nodes[concept].get("entry_count", 0) + 1
            if concept in self.graph else 1
        )

        existing_summary = (
            self.graph.nodes[concept].get("summary", "")
            if concept in self.graph else ""
        )
        existing_compacted = (
            self.graph.nodes[concept].get("compacted", False)
            if concept in self.graph else False
        )

        self.graph.add_node(
            concept,
            summary=existing_summary,
            confidence=confidence,
            entry_count=entry_count,
            compacted=existing_compacted,
        )

        for linked in linked_concepts:
            if self.graph.has_edge(concept, linked):
                self.graph[concept][linked]["mentions"] += 1
            else:
                self.graph.add_edge(concept, linked, edge_type="associated", mentions=1)

        # Persist
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO nodes (concept, confidence, entry_count, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(concept) DO UPDATE SET
                    confidence  = excluded.confidence,
                    entry_count = excluded.entry_count,
                    updated_at  = excluded.updated_at
                """,
                (concept, confidence, entry_count, now),
            )
            for linked in linked_concepts:
                existing = conn.execute(
                    "SELECT mentions FROM edges WHERE source=? AND target=?",
                    (concept, linked),
                ).fetchone()
                mentions = (existing[0] + 1) if existing else 1
                conn.execute(
                    """
                    INSERT INTO edges (source, target, edge_type, mentions, updated_at)
                    VALUES (?, ?, 'associated', ?, ?)
                    ON CONFLICT(source, target, edge_type) DO UPDATE SET
                        mentions   = excluded.mentions,
                        updated_at = excluded.updated_at
                    """,
                    (concept, linked, mentions, now),
                )

    def store_compacted_summary(self, concept: str, summary: str) -> None:
        """Store a synthesized summary (written by Claude) for a concept.
        Called by the compact() MCP tool."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        if concept not in self.graph:
            self.graph.add_node(concept, confidence=0.5, entry_count=0, compacted=False)

        self.graph.nodes[concept]["summary"] = summary
        self.graph.nodes[concept]["compacted"] = True

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO nodes (concept, summary, compacted, updated_at)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(concept) DO UPDATE SET
                    summary    = excluded.summary,
                    compacted  = 1,
                    updated_at = excluded.updated_at
                """,
                (concept, summary, now),
            )

    def get_concept_node(self, concept: str) -> dict | None:
        if concept not in self.graph:
            return None
        return dict(self.graph.nodes[concept])

    def get_strong_concepts(self, min_confidence: float = 0.3) -> list[dict]:
        """Concepts with sufficient confidence — sorted by confidence desc."""
        return sorted(
            [
                {
                    "concept": c,
                    "confidence": d.get("confidence", 0.0),
                    "entry_count": d.get("entry_count", 0),
                    "summary": d.get("summary", ""),
                    "compacted": d.get("compacted", False),
                }
                for c, d in self.graph.nodes(data=True)
                if d.get("confidence", 0.0) >= min_confidence
            ],
            key=lambda x: x["confidence"],
            reverse=True,
        )

    def get_associated_concepts(self, concept: str) -> list[dict]:
        """Concepts linked from this one, sorted by mention count."""
        if concept not in self.graph:
            return []
        return sorted(
            [
                {
                    "concept": target,
                    "mentions": data.get("mentions", 1),
                    "edge_type": data.get("edge_type", "associated"),
                }
                for _, target, data in self.graph.out_edges(concept, data=True)
            ],
            key=lambda x: x["mentions"],
            reverse=True,
        )

    def node_count(self) -> int:
        return self.graph.number_of_nodes()

    def edge_count(self) -> int:
        return self.graph.number_of_edges()
