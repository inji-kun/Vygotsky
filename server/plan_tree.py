"""Recursive Plan Tree — hierarchical task tracking with markdown artifacts.

Each plan gets a directory with:
- tree.json: structure, status, theory-check flags
- step_NNN.md: step content (rationale, reasoning)
- step_NNN_summary.md: completion summary (what was built, what user understood)

Storage: ~/.vygotsky/plans/
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_PLANS_DIR = Path.home() / ".vygotsky" / "plans"


@dataclass
class PlanStep:
    """A single step in the recursive plan hierarchy."""
    id: str
    description: str
    parent_id: str | None = None
    status: str = "pending"  # pending, active, done
    substeps: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "parent_id": self.parent_id,
            "status": self.status,
            "substeps": self.substeps,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


class PlanTree:
    """Tracks the recursive plan hierarchy with markdown artifacts.

    INVARIANT: steps dict contains all steps by ID.
    INVARIANT: current_step_id points to the currently active step (or None).
    INVARIANT: Each plan gets its own directory with tree.json + step markdown files.
    """

    def __init__(self, plans_dir: Path | None = None):
        self.plans_dir = plans_dir or DEFAULT_PLANS_DIR
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.steps: dict[str, PlanStep] = {}
        self.current_step_id: str | None = None
        self._next_id: int = 1
        self._current_plan_id: str | None = None

    def _gen_step_id(self) -> str:
        step_id = f"step_{self._next_id}"
        self._next_id += 1
        return step_id

    def _gen_plan_id(self) -> str:
        existing = list(self.plans_dir.glob("plan_*"))
        next_num = len(existing) + 1
        return f"plan_{next_num:03d}"

    def _plan_dir(self) -> Path:
        """Get or create the current plan's directory."""
        if self._current_plan_id is None:
            self._current_plan_id = self._gen_plan_id()
        d = self.plans_dir / self._current_plan_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _save_tree(self) -> None:
        """Persist the tree skeleton to tree.json."""
        plan_dir = self._plan_dir()
        data = {
            "steps": {k: v.to_dict() for k, v in self.steps.items()},
            "current_step_id": self.current_step_id,
            "next_id": self._next_id,
            "plan_id": self._current_plan_id,
        }
        (plan_dir / "tree.json").write_text(json.dumps(data, indent=2))

    def _write_step_markdown(self, step: PlanStep, reasoning: str = "") -> None:
        """Write the step's markdown file."""
        plan_dir = self._plan_dir()
        content = f"# {step.description}\n\n"
        if reasoning:
            content += f"## Reasoning\n\n{reasoning}\n\n"
        content += f"**Status:** {step.status}\n"
        if step.parent_id:
            parent = self.steps.get(step.parent_id)
            if parent:
                content += f"**Parent:** {parent.description}\n"
        (plan_dir / f"{step.id}.md").write_text(content)

    def plan_step(
        self,
        description: str,
        parent_id: str | None = None,
        reasoning: str = "",
    ) -> dict:
        """Declare a new step in the plan hierarchy.

        No parent_id = top-level step (starts a new plan if none active).
        With parent_id = decomposition of an existing step.
        """
        step_id = self._gen_step_id()

        if parent_id and parent_id in self.steps:
            parent = self.steps[parent_id]
            step = PlanStep(
                id=step_id,
                description=description,
                parent_id=parent_id,
                status="active",
            )
            parent.substeps.append(step_id)
        else:
            step = PlanStep(
                id=step_id,
                description=description,
                status="active",
            )

        self.steps[step_id] = step
        self.current_step_id = step_id
        self._write_step_markdown(step, reasoning)
        self._save_tree()

        return {
            "step_id": step_id,
            "plan_id": self._current_plan_id,
            "breadcrumb": self._get_breadcrumb(),
            "theory_check_recommended": parent_id is not None,
        }

    def complete_step(self, step_id: str, summary: str) -> dict:
        """Mark a step complete with a summary."""
        if step_id not in self.steps:
            return {"error": f"Step {step_id} not found"}

        step = self.steps[step_id]
        step.status = "done"
        step.completed_at = time.time()

        # Write summary markdown
        plan_dir = self._plan_dir()
        summary_content = f"# {step.description} — Summary\n\n{summary}\n"
        (plan_dir / f"{step_id}_summary.md").write_text(summary_content)

        # Move current to parent
        if self.current_step_id == step_id:
            self.current_step_id = step.parent_id

        self._save_tree()

        # Find next sibling
        next_step = None
        if step.parent_id and step.parent_id in self.steps:
            parent = self.steps[step.parent_id]
            for sub_id in parent.substeps:
                if self.steps[sub_id].status == "pending":
                    next_step = sub_id
                    break

        return {
            "completed": step_id,
            "breadcrumb": self._get_breadcrumb(),
            "next_step": next_step,
            "theory_check_recommended": step.parent_id is not None,
        }

    def get_plan_state(self) -> dict:
        """Return compact state: breadcrumb, active step, siblings."""
        breadcrumb = self._get_breadcrumb()

        if self.current_step_id is None:
            return {
                "breadcrumb": breadcrumb,
                "active_step": None,
                "siblings": [],
                "has_active_plan": self._has_active_plan(),
            }

        current = self.steps[self.current_step_id]
        siblings = []
        if current.parent_id and current.parent_id in self.steps:
            parent = self.steps[current.parent_id]
            siblings = [
                {"id": s, "description": self.steps[s].description, "status": self.steps[s].status}
                for s in parent.substeps
            ]

        return {
            "breadcrumb": breadcrumb,
            "active_step": {
                "id": current.id,
                "description": current.description,
                "substeps": [
                    {"id": s, "description": self.steps[s].description, "status": self.steps[s].status}
                    for s in current.substeps
                ],
            },
            "siblings": siblings,
            "has_active_plan": True,
        }

    def _get_breadcrumb(self) -> str:
        """Get the current plan hierarchy as a breadcrumb path."""
        if self.current_step_id is None:
            return "(no active plan)"

        parts = []
        step_id: str | None = self.current_step_id
        while step_id is not None:
            step = self.steps.get(step_id)
            if step is None:
                break
            parts.append(step.description)
            step_id = step.parent_id

        parts.reverse()
        return " > ".join(parts)

    def _has_active_plan(self) -> bool:
        return any(s.status == "active" for s in self.steps.values())
