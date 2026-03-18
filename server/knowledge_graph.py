"""Knowledge Graph — concept topology derived from diary observations.

Nodes: concepts with entry count (for ordering)
Edges: associations derived from [[wiki-links]] in diary entries

Storage: SQLite for persistence, NetworkX for in-memory traversal.

Summaries live in ~/.vygotsky/summaries/ as plain markdown files —
not here. This module is topology only.
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
                    entry_count INTEGER DEFAULT 0,
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
            for row in conn.execute("SELECT concept, entry_count FROM nodes"):
                concept, entry_count = row
                self.graph.add_node(concept, entry_count=entry_count)
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

        entry_count = (
            self.graph.nodes[concept].get("entry_count", 0) + 1
            if concept in self.graph else 1
        )
        self.graph.add_node(concept, entry_count=entry_count)

        for linked in linked_concepts:
            if self.graph.has_edge(concept, linked):
                self.graph[concept][linked]["mentions"] += 1
            else:
                self.graph.add_edge(concept, linked, edge_type="associated", mentions=1)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO nodes (concept, entry_count, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(concept) DO UPDATE SET
                    entry_count = excluded.entry_count,
                    updated_at  = excluded.updated_at
                """,
                (concept, entry_count, now),
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

    def get_concept_node(self, concept: str) -> dict | None:
        if concept not in self.graph:
            return None
        return dict(self.graph.nodes[concept])

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
