"""Learner Diary — narrative observations about what this human understands.

NOT a score graph. Claude writes naturalistic observations organized by concept.
Each concept is a markdown file with timestamped entries. Concepts interlink
via [[concept_name]] wiki-style links.

Storage: ~/.vygotsky/diary/
  async-programming.md
  database-migrations.md
  error-handling.md
"""

import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DIARY_DIR = Path.home() / ".vygotsky" / "diary"
LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")

# Matches: ### 2026-03-10T14:32:00Z [explanation]
ENTRY_PATTERN = re.compile(r"### (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) \[(\w+)\]\n")

VALID_EVIDENCE_TYPES = {
    "prediction", "explanation", "question", "application", "transfer",
    "correction", "disagreement", "directive", "design_decision",
    "gap", "acknowledgment", "calibration",
}


def _escape_observation(text: str) -> str:
    """Escape ### in observation text to prevent parsing ambiguity."""
    return text.replace("\n###", "\n\\###")


def _unescape_observation(text: str) -> str:
    """Unescape ### in observation text after parsing."""
    return text.replace("\n\\###", "\n###")


class LearnerDiary:
    def __init__(self, diary_dir: Path | None = None):
        self.diary_dir = diary_dir or DEFAULT_DIARY_DIR
        self.diary_dir.mkdir(parents=True, exist_ok=True)

    def _concept_path(self, concept: str) -> Path:
        """Normalize concept name to a safe filename using hyphen slugification."""
        safe_name = re.sub(r"[^a-z0-9]+", "-", concept.lower()).strip("-")
        return self.diary_dir / f"{safe_name}.md"

    def record(self, concept: str, observation: str, evidence_type: str = "acknowledgment") -> None:
        """Append a timestamped observation to a concept's diary file."""
        from server.util import atomic_write

        if evidence_type not in VALID_EVIDENCE_TYPES:
            evidence_type = "acknowledgment"

        path = self._concept_path(concept)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        escaped = _escape_observation(observation)
        entry = f"\n### {timestamp} [{evidence_type}]\n\n{escaped}\n"

        if not path.exists():
            header = f"# {concept}\n"
            atomic_write(path, header + entry)
        else:
            content = path.read_text()
            atomic_write(path, content + entry)

    def read(self, concept: str) -> list[dict]:
        """Read all diary entries for a concept. Returns list of {timestamp, evidence_type, observation}."""
        path = self._concept_path(concept)
        if not path.exists():
            return []

        content = path.read_text()
        entries = []
        parts = re.split(r"### (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) \[(\w+)\]\n", content)
        # parts[0] is header, then alternating timestamp/evidence_type/content
        for i in range(1, len(parts), 3):
            if i + 2 < len(parts):
                entries.append({
                    "timestamp": parts[i],
                    "evidence_type": parts[i + 1],
                    "observation": _unescape_observation(parts[i + 2].strip()),
                })
        return entries

    def list_concepts(self) -> list[str]:
        """List all concepts that have diary entries."""
        return [p.stem for p in self.diary_dir.glob("*.md")]

    def get_links(self, concept: str) -> list[str]:
        """Get concepts linked from this concept's diary via [[concept_name]]."""
        path = self._concept_path(concept)
        if not path.exists():
            return []
        content = path.read_text()
        return list(set(LINK_PATTERN.findall(content)))

    def get_evidence_summary(self, concept: str) -> str:
        """Return a human-readable summary of evidence types for a concept."""
        entries = self.read(concept)
        if not entries:
            return "No entries"
        counts = Counter(e.get("evidence_type", "acknowledgment") for e in entries)
        parts = [f"{count} {etype}{'s' if count > 1 else ''}" for etype, count in counts.most_common()]
        return f"{len(entries)} entries — {', '.join(parts)}"

    def get_context(self, max_concepts: int = 10) -> str:
        """Return a narrative summary of the learner for Claude to read.

        Returns the most recently updated concept entries as readable text,
        not a data structure. Claude reads this like reading a colleague's notes.
        """
        concept_files = sorted(
            self.diary_dir.glob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        parts = []
        for path in concept_files[:max_concepts]:
            content = path.read_text()
            parts.append(content.strip())

        if not parts:
            return "No observations yet. This is a new learner."

        return "\n\n---\n\n".join(parts)
