"""Learner Diary — narrative observations about what this human understands.

NOT a score graph. Claude writes naturalistic observations organized by concept.
Each concept is a markdown file with timestamped entries. Concepts interlink
via [[concept_name]] wiki-style links.

Storage: ~/.vygotsky/diary/
  async_programming.md
  database_migrations.md
  error_handling.md
"""

import re
from datetime import datetime
from pathlib import Path

DEFAULT_DIARY_DIR = Path.home() / ".vygotsky" / "diary"
LINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")


class LearnerDiary:
    def __init__(self, diary_dir: Path | None = None):
        self.diary_dir = diary_dir or DEFAULT_DIARY_DIR
        self.diary_dir.mkdir(parents=True, exist_ok=True)

    def _concept_path(self, concept: str) -> Path:
        """Normalize concept name to a safe filename."""
        safe_name = concept.lower().replace(" ", "_").replace("/", "_")
        return self.diary_dir / f"{safe_name}.md"

    def record(self, concept: str, observation: str) -> None:
        """Append a timestamped observation to a concept's diary file."""
        path = self._concept_path(concept)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n### {timestamp}\n\n{observation}\n"

        if not path.exists():
            header = f"# {concept}\n"
            path.write_text(header + entry)
        else:
            with open(path, "a") as f:
                f.write(entry)

    def read(self, concept: str) -> list[dict]:
        """Read all diary entries for a concept. Returns list of {timestamp, observation}."""
        path = self._concept_path(concept)
        if not path.exists():
            return []

        content = path.read_text()
        entries = []
        parts = re.split(r"### (\d{4}-\d{2}-\d{2} \d{2}:\d{2})\n", content)
        # parts[0] is header, then alternating timestamp/content
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                entries.append({
                    "timestamp": parts[i],
                    "observation": parts[i + 1].strip(),
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
