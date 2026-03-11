#!/usr/bin/env python3
"""Vygotsky MCP Server — theory-building tools for Claude Code."""

import sys
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from server.session import Session
from server.quadrants import get_quadrant_guidance

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("vygotsky")

mcp = FastMCP(name="vygotsky")
session = Session()


# --- Theory-Building Tools (Diary Model) ---

@mcp.tool()
def get_concept(concept: str, detail: str = "summary") -> str:
    """Read diary entries for a concept. detail="summary" for overview with
    evidence quality and linked concepts. detail="full" for complete history.
    Use summary for pre-flight checks, full when you need the whole story."""
    if detail == "full":
        data = session.get_concept_full(concept)
        if not data["entries"]:
            return f"No diary entries for '{concept}'. This is new territory."
        parts = [f"# {concept} — Full History"]
        for e in data["entries"]:
            etype = e.get("evidence_type", "acknowledgment")
            parts.append(f"\n### {e['timestamp']} [{etype}]\n\n{e['observation']}")
        if data["linked_concepts"]:
            links = ", ".join(
                f"{c['concept']} ({c['entries']} entries, strongest: {c['strongest_evidence']})"
                for c in data["linked_concepts"]
            )
            parts.append(f"\nLinked: {links}")
        return "\n".join(parts)
    else:
        data = session.get_concept_summary(concept)
        if not data["has_diary_entries"]:
            return f"No diary entries for '{concept}'. New territory — theory check recommended."
        parts = [f"{concept}: {data['evidence_summary']}"]
        if data["linked_concepts"]:
            for lc in data["linked_concepts"]:
                parts.append(f"  -> {lc['concept']} ({lc['entries']} entries, strongest: {lc['strongest_evidence']})")
        if data["engagement_signals"]["is_passive_alarm"]:
            parts.append("WARNING: Passive alarm active — user may be rubber-stamping.")
        return "\n".join(parts)


@mcp.tool()
def record_observation(concept: str, observation: str, evidence_type: str = "acknowledgment") -> str:
    """Write a diary entry about the human's understanding of a concept.
    evidence_type: prediction, explanation, question, application, transfer,
    correction, disagreement, directive, design_decision, gap, acknowledgment.
    Use [[concept_name]] to link related concepts."""
    valid_types = {
        "prediction", "explanation", "question", "application", "transfer",
        "correction", "disagreement", "directive", "design_decision",
        "gap", "acknowledgment",
    }
    if evidence_type not in valid_types:
        return f"Invalid evidence_type '{evidence_type}'. Valid: {', '.join(sorted(valid_types))}."

    session.diary.record(concept, observation, evidence_type=evidence_type)
    entries = session.diary.read(concept)
    return f"Recorded on {concept} ({len(entries)} entries, evidence: {evidence_type})"


@mcp.tool()
def set_quadrant(quadrant: str) -> str:
    """Set the current interaction quadrant based on your reading of the
    diary and engagement signals. One of: extension, sparring, senior_peer,
    brake_pedal."""
    result = session.set_quadrant(quadrant)
    if "error" in result:
        return f"{result['error']} Read the diary first to judge."
    parts = [f"Quadrant: {quadrant}. {result['posture']}"]
    if result.get("transition"):
        parts.insert(0, result["transition"])
    return " ".join(parts)


# --- Recursive Planning Tools ---

@mcp.tool()
def plan_step(description: str, parent_id: str = "", reasoning: str = "") -> dict:
    """Declare a new step in the plan hierarchy.
    No parent_id = top-level step. With parent_id = decomposition of existing step.
    Returns step_id, breadcrumb, and whether a theory check is recommended."""
    return session.plan_tree.plan_step(
        description, parent_id=parent_id or None, reasoning=reasoning)


@mcp.tool()
def complete_step(step_id: str, summary: str) -> str:
    """Mark a plan step complete with a summary of what was done."""
    result = session.plan_tree.complete_step(step_id, summary)
    if "error" in result:
        return f"{result['error']} Call get_plan_state() to see existing steps."
    parts = [f"Completed {step_id}."]
    parts.append(f"Breadcrumb: {result['breadcrumb']}")
    if result.get("next_step"):
        next_s = session.plan_tree.steps.get(result["next_step"])
        desc = next_s.description if next_s else result["next_step"]
        parts.append(f"Next: {result['next_step']} ({desc})")
    if result.get("theory_check_recommended"):
        parts.append("Theory check recommended at this boundary.")
    return " ".join(parts)


@mcp.tool()
def get_plan_state() -> dict:
    """Get current position in the plan tree — breadcrumb, active step, siblings."""
    return session.plan_tree.get_plan_state()


# --- Session Tools ---

@mcp.tool()
def get_session_state() -> dict:
    """Get everything: learner diary context, plan position, engagement signals,
    current quadrant. Call this at session start to orient yourself."""
    return session.get_state()


if __name__ == "__main__":
    logger.info("Vygotsky MCP server starting...")
    mcp.run(transport="stdio")
