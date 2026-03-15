"""End-to-end integration tests: full session flows through all components."""


def test_full_session_flow(tmp_path):
    """Simulate a session: theory check -> diary entry -> verify state."""
    from server.session import Session

    session = Session(state_dir=tmp_path)

    # Check concept — no diary entries yet
    check = session.get_concept_summary("authentication")
    assert check["has_diary_entries"] is False

    # Claude observes the human demonstrating understanding
    session.diary.record("authentication",
        "Explained JWT vs session tokens clearly. Chose JWT because the "
        "API is stateless. Understands the trade-off with token revocation. "
        "See also [[session-management]].",
        evidence_type="explanation")

    # Now the concept has diary entries
    check2 = session.get_concept_summary("authentication")
    assert check2["has_diary_entries"] is True
    assert "explanation" in check2["evidence_summary"]

    # Links are tracked
    links = session.diary.get_links("authentication")
    assert "session-management" in links

    # Full state should reflect diary and engagement
    state = session.get_state()
    assert "JWT" in state["diary"]  # narrative, not scores
    # Note: quadrant lives in Claude's reasoning; plan lives in .claude/plans/ files


def test_engagement_influences_session(tmp_path):
    """Passive responses show up in session state."""
    from server.session import Session

    session = Session(state_dir=tmp_path)
    session.engagement.record_prompt("ok")
    session.engagement.record_prompt("sure")
    session.engagement.record_prompt("yes")

    state = session.get_state()
    assert state["engagement"]["is_passive_alarm"] is True
    assert state["engagement"]["consecutive_passive"] >= 3
    assert "recent_signals" in state["engagement"]
    assert "current_score" not in state["engagement"]


def test_diary_persists_across_sessions(tmp_path):
    """Diary survives session recreation (same state_dir)."""
    from server.session import Session

    session1 = Session(state_dir=tmp_path)
    session1.diary.record("async_programming",
        "First encounter. Asked good questions about the event loop "
        "but got confused about error propagation in promise chains.",
        evidence_type="question")

    # New session, same directory
    session2 = Session(state_dir=tmp_path)
    entries = session2.diary.read("async_programming")
    assert len(entries) == 1
    assert "event loop" in entries[0]["observation"]

    context = session2.diary.get_context()
    assert "async_programming" in context or "async-programming" in context


def test_scaffolding_loop_with_evidence(tmp_path):
    """Full loop: record with evidence -> check summary -> verify quality."""
    from server.session import Session

    session = Session(state_dir=tmp_path)

    # Record diverse evidence including calibration
    session.diary.record("database_migrations",
        "Predicted rollback would restore previous schema version",
        evidence_type="prediction")
    session.diary.record("database_migrations",
        "Explained why up/down migrations need to be idempotent",
        evidence_type="explanation")
    session.diary.record("database_migrations",
        "Said ok to adding an index. See [[sql-indexes]].",
        evidence_type="acknowledgment")

    # Summary should reflect evidence quality
    summary = session.get_concept_summary("database_migrations")
    assert summary["has_diary_entries"] is True
    assert "3 entries" in summary["evidence_summary"]
    assert "prediction" in summary["evidence_summary"]

    # Linked concept should be surfaced
    assert any(lc["concept"] == "sql-indexes" for lc in summary["linked_concepts"])

    # Gap in prerequisite should be visible
    sql_link = [lc for lc in summary["linked_concepts"] if lc["concept"] == "sql-indexes"][0]
    assert sql_link["entries"] == 0
    assert sql_link["strongest_evidence"] == "none"
