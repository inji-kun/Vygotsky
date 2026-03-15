from pathlib import Path
import pytest


def test_update_from_entry_creates_node(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("async-programming", "explanation", [])
    node = g.get_concept_node("async-programming")
    assert node is not None
    assert node["entry_count"] == 1
    assert node["confidence"] > 0.0


def test_mastery_evidence_boosts_confidence_more(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("concept-a", "prediction", [])   # mastery type
    g.update_from_entry("concept-b", "acknowledgment", [])  # low signal
    node_a = g.get_concept_node("concept-a")
    node_b = g.get_concept_node("concept-b")
    assert node_a["confidence"] > node_b["confidence"]


def test_confidence_accumulates_with_entries(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("closures", "explanation", [])
    first_conf = g.get_concept_node("closures")["confidence"]
    g.update_from_entry("closures", "transfer", [])
    second_conf = g.get_concept_node("closures")["confidence"]
    assert second_conf > first_conf


def test_confidence_capped_at_one(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    for _ in range(20):
        g.update_from_entry("closures", "transfer", [])
    node = g.get_concept_node("closures")
    assert node["confidence"] <= 1.0


def test_linked_concepts_create_edges(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("async-programming", "explanation", ["promises", "event-loop"])
    assoc = g.get_associated_concepts("async-programming")
    concepts = [a["concept"] for a in assoc]
    assert "promises" in concepts
    assert "event-loop" in concepts


def test_edge_mention_count_increments(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("async-programming", "explanation", ["promises"])
    g.update_from_entry("async-programming", "prediction", ["promises"])
    assoc = g.get_associated_concepts("async-programming")
    promises = next(a for a in assoc if a["concept"] == "promises")
    assert promises["mentions"] == 2


def test_get_strong_concepts_filters_by_confidence(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    # Low-confidence concept (1 acknowledgment = 0.03)
    g.update_from_entry("weak-concept", "acknowledgment", [])
    # Higher-confidence concept (1 prediction = 0.1, 1 explanation = 0.1 => 0.2)
    g.update_from_entry("strong-concept", "prediction", [])
    g.update_from_entry("strong-concept", "explanation", [])
    g.update_from_entry("strong-concept", "transfer", [])  # 0.3

    strong = g.get_strong_concepts(min_confidence=0.3)
    names = [n["concept"] for n in strong]
    assert "strong-concept" in names
    assert "weak-concept" not in names


def test_get_strong_concepts_sorted_by_confidence(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("concept-a", "prediction", [])  # 0.1
    g.update_from_entry("concept-b", "prediction", [])
    g.update_from_entry("concept-b", "explanation", [])  # 0.2
    strong = g.get_strong_concepts(min_confidence=0.05)
    confidences = [n["confidence"] for n in strong]
    assert confidences == sorted(confidences, reverse=True)


def test_store_compacted_summary(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("closures", "explanation", [])
    g.store_compacted_summary("closures", "Developer understands closures deeply via lexical scope.")
    node = g.get_concept_node("closures")
    assert node["compacted"] is True
    assert "lexical scope" in node["summary"]


def test_store_compacted_summary_for_new_concept(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    # Concept doesn't exist yet — compact() should still work
    g.store_compacted_summary("brand-new", "Summary of a brand-new concept.")
    node = g.get_concept_node("brand-new")
    assert node is not None
    assert node["compacted"] is True


def test_persistence_across_instances(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    db = tmp_path / "kg.db"
    g1 = KnowledgeGraph(db)
    g1.update_from_entry("closures", "prediction", ["scope"])
    g1.store_compacted_summary("closures", "Persistent summary.")

    g2 = KnowledgeGraph(db)
    node = g2.get_concept_node("closures")
    assert node is not None
    assert node["compacted"] is True
    assert "Persistent summary" in node["summary"]
    assoc = g2.get_associated_concepts("closures")
    assert any(a["concept"] == "scope" for a in assoc)


def test_node_and_edge_counts(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    assert g.node_count() == 0
    assert g.edge_count() == 0
    g.update_from_entry("async-programming", "explanation", ["promises"])
    # NetworkX auto-creates nodes for edge endpoints, so both concept + linked are nodes
    assert g.node_count() == 2
    assert g.edge_count() == 1


def test_calibration_type_updates_graph(tmp_path):
    """calibration entries still update graph node (entry count) but with low boost."""
    from server.knowledge_graph import KnowledgeGraph, MASTERY_TYPES
    g = KnowledgeGraph(tmp_path / "kg.db")
    assert "calibration" not in MASTERY_TYPES
    g.update_from_entry("async-programming", "calibration", [])
    node = g.get_concept_node("async-programming")
    assert node["entry_count"] == 1
    assert node["confidence"] == pytest.approx(0.03)


def test_session_record_observation_updates_graph(tmp_path):
    """Session.record_observation writes diary AND updates graph atomically."""
    from server.session import Session
    session = Session(state_dir=tmp_path)
    session.record_observation(
        "async-programming",
        "Predicted promise chaining correctly. See [[event-loop]].",
        evidence_type="prediction",
    )
    node = session.graph.get_concept_node("async-programming")
    assert node is not None
    assert node["entry_count"] == 1
    assoc = session.graph.get_associated_concepts("async-programming")
    assert any(a["concept"] == "event-loop" for a in assoc)
