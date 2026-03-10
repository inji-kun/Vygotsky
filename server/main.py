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

mcp = FastMCP(name="vygotsky", json_response=True)
session = Session()


# --- Theory-Building Tools (Diary Model) ---

@mcp.tool()
def get_learner_context() -> str:
    """Read the learner diary — narrative observations about what this human
    understands. Returns readable text, like reading a colleague's notes.
    Use this to calibrate your explanations and decide what needs checking."""
    return session.diary.get_context()


@mcp.tool()
def read_concept(concept: str) -> dict:
    """Read all diary entries for a specific concept.
    Returns the full history of observations about this person's understanding
    of this concept, or empty if we've never seen them work with it."""
    return {
        "concept": concept,
        "entries": session.diary.read(concept),
        "linked_concepts": session.diary.get_links(concept),
    }


@mcp.tool()
def record_observation(concept: str, observation: str) -> dict:
    """Write a diary entry about the human's understanding of a concept.
    Write what you observed — how they engaged, what they understood or
    struggled with, what they said. Use [[concept_name]] to link to
    related concepts. This is a diary, not a grade book."""
    session.diary.record(concept, observation)
    return {
        "recorded": True,
        "concept": concept,
        "total_entries": len(session.diary.read(concept)),
    }


@mcp.tool()
def check_concept(concept: str) -> dict:
    """Before proceeding with something that touches this concept, check
    what we know about the human's understanding. Returns diary entries
    and engagement signals so you can decide whether to theory-check."""
    return session.should_theory_check(concept)


@mcp.tool()
def set_quadrant(quadrant: str) -> dict:
    """Set the current interaction quadrant based on your reading of the
    diary and engagement signals. One of: extension, sparring, senior_peer,
    brake_pedal."""
    return session.set_quadrant(quadrant)


# --- Recursive Planning Tools ---

@mcp.tool()
def plan_step(description: str, parent_id: str = "", reasoning: str = "") -> dict:
    """Declare a new step in the plan hierarchy.
    No parent_id = top-level step. With parent_id = decomposition of existing step.
    Returns step_id, breadcrumb, and whether a theory check is recommended."""
    return session.plan_tree.plan_step(
        description, parent_id=parent_id or None, reasoning=reasoning)


@mcp.tool()
def complete_step(step_id: str, summary: str) -> dict:
    """Mark a plan step complete with a summary of what was done.
    Returns next step suggestion and current plan state."""
    return session.plan_tree.complete_step(step_id, summary)


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
