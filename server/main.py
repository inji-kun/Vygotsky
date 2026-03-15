#!/usr/bin/env python3
"""Vygotsky MCP Server — developer model store for Claude Code."""

import sys
import logging
from mcp.server.fastmcp import FastMCP

from server.session import Session

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("vygotsky")

mcp = FastMCP(name="vygotsky")
session = Session()


@mcp.tool()
def get_session_brief() -> str:
    """Generate the session brief — structured ~500 token developer model snapshot.
    Injected at session start by the hook. Only call this mid-session if context
    was lost (e.g. after compaction). Do not call on every turn."""
    return session.generate_brief()


@mcp.tool()
def get_concept(concept: str, detail: str = "summary") -> str:
    """Deep-dive into a concept's diary history. Use only when the session brief
    doesn't have enough detail — not as a routine mid-session check.
    detail="summary" for evidence overview, detail="full" for complete history."""
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
                parts.append(
                    f"  -> {lc['concept']} ({lc['entries']} entries, "
                    f"strongest: {lc['strongest_evidence']})"
                )
        if data["engagement_signals"]["is_passive_alarm"]:
            parts.append("WARNING: Passive alarm active — human may be rubber-stamping.")
        return "\n".join(parts)


@mcp.tool()
def record_observation(concept: str, observation: str, evidence_type: str = "acknowledgment") -> str:
    """Write a diary entry about the human's understanding of a concept.
    evidence_type: gap, acknowledgment, explanation, prediction, correction,
    connection, extension, directive, design_decision, disagreement, transfer,
    calibration.
    Use [[concept_name]] to link related concepts.
    Target 2-3 calls per session total — prefer high-confidence observations."""
    valid_types = {
        "gap", "acknowledgment", "explanation", "prediction", "correction",
        "connection", "extension", "directive", "design_decision",
        "disagreement", "transfer", "calibration",
    }
    if evidence_type not in valid_types:
        return f"Invalid evidence_type '{evidence_type}'. Valid: {', '.join(sorted(valid_types))}."

    session.record_observation(concept, observation, evidence_type=evidence_type)
    return "ok"


@mcp.tool()
def compact(concept: str, summary: str) -> str:
    """Store a synthesized concept summary written by Claude.
    Before calling: synthesize the diary entries for this concept in your response.
    Then call compact() with that synthesis.
    Only call when concept has 5+ entries — compaction is a considered act, not routine."""
    session.graph.store_compacted_summary(concept, summary)
    return "ok"


if __name__ == "__main__":
    logger.info("Vygotsky MCP server starting...")
    mcp.run(transport="stdio")
