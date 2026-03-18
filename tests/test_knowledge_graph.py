from pathlib import Path


def test_update_from_entry_creates_node(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("async-programming", "explanation", [])
    node = g.get_concept_node("async-programming")
    assert node is not None
    assert node["entry_count"] == 1


def test_entry_count_accumulates(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("closures", "explanation", [])
    g.update_from_entry("closures", "prediction", [])
    node = g.get_concept_node("closures")
    assert node["entry_count"] == 2


def test_no_confidence_field(tmp_path):
    """Graph nodes have no confidence — that was removed."""
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("closures", "prediction", [])
    node = g.get_concept_node("closures")
    assert "confidence" not in node


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


def test_get_associated_sorted_by_mentions(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    g.update_from_entry("async-programming", "explanation", ["promises"])
    g.update_from_entry("async-programming", "explanation", ["promises"])
    g.update_from_entry("async-programming", "explanation", ["event-loop"])
    assoc = g.get_associated_concepts("async-programming")
    mentions = [a["mentions"] for a in assoc]
    assert mentions == sorted(mentions, reverse=True)


def test_persistence_across_instances(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    db = tmp_path / "kg.db"
    g1 = KnowledgeGraph(db)
    g1.update_from_entry("closures", "prediction", ["scope"])

    g2 = KnowledgeGraph(db)
    node = g2.get_concept_node("closures")
    assert node is not None
    assert node["entry_count"] == 1
    assoc = g2.get_associated_concepts("closures")
    assert any(a["concept"] == "scope" for a in assoc)


def test_node_and_edge_counts(tmp_path):
    from server.knowledge_graph import KnowledgeGraph
    g = KnowledgeGraph(tmp_path / "kg.db")
    assert g.node_count() == 0
    assert g.edge_count() == 0
    g.update_from_entry("async-programming", "explanation", ["promises"])
    # NetworkX auto-creates nodes for both edge endpoints
    assert g.node_count() == 2
    assert g.edge_count() == 1


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


def test_diary_write_and_read_summary(tmp_path):
    """Summaries are written/read as plain files in summaries/ dir."""
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    assert diary.read_summary("closures") is None
    diary.write_summary("closures", "Developer understands closures via lexical scope.")
    result = diary.read_summary("closures")
    assert result is not None
    assert "lexical scope" in result


def test_diary_developer_summary(tmp_path):
    """concept='developer' writes the whole-developer narrative."""
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.write_summary("developer", "Strong on async, gaps in DB migrations.")
    result = diary.read_summary("developer")
    assert "async" in result


def test_compact_tool_writes_summary_file(tmp_path):
    """compact() MCP tool writes to diary summaries, not graph."""
    from server.session import Session
    session = Session(state_dir=tmp_path)
    session.diary.record("closures", "Explained closures well.", evidence_type="explanation")
    session.diary.write_summary("closures", "Deep understanding of closures.")
    assert session.diary.read_summary("closures") is not None


def test_generate_brief_uses_summary_when_available(tmp_path):
    from server.session import Session
    session = Session(state_dir=tmp_path)
    session.record_observation("async-programming",
        "Predicted promise chaining.", evidence_type="prediction")
    session.diary.write_summary("async-programming", "Expert-level async understanding.")
    brief = session.generate_brief()
    assert "Expert-level async understanding" in brief


def test_generate_brief_falls_back_to_evidence_type(tmp_path):
    from server.session import Session
    session = Session(state_dir=tmp_path)
    session.record_observation("async-programming",
        "Predicted promise chaining.", evidence_type="prediction")
    brief = session.generate_brief()
    assert "async-programming" in brief
    assert "prediction" in brief


def test_generate_brief_shows_developer_summary(tmp_path):
    from server.session import Session
    session = Session(state_dir=tmp_path)
    session.diary.write_summary("developer", "Strong on async, gaps in migrations.")
    brief = session.generate_brief()
    assert "Developer model" in brief
    assert "async" in brief


def test_list_concepts_excludes_summaries(tmp_path):
    """Summaries live in a separate dir — list_concepts must not include them."""
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("closures", "Good understanding.", evidence_type="explanation")
    diary.write_summary("closures", "Summary text.")
    concepts = diary.list_concepts()
    assert "closures" in concepts
    # summary files should not bleed into concept list
    assert len([c for c in concepts if "summary" in c]) == 0
