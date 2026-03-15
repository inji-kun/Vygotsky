from pathlib import Path


def test_session_state_includes_diary_and_engagement(tmp_path):
    from server.session import Session
    session = Session(state_dir=tmp_path)
    state = session.get_state()
    assert "diary" in state
    assert "engagement" in state
    # quadrant and plan are no longer in server state — they live in
    # Claude's reasoning and .claude/plans/ files respectively


def test_diary_context_is_narrative(tmp_path):
    from server.session import Session
    session = Session(state_dir=tmp_path)
    session.diary.record("async_programming", "Strong understanding of event loop.")
    state = session.get_state()
    assert "event loop" in state["diary"]
    assert "score" not in state["diary"].lower()


def test_concept_summary_for_unknown(tmp_path):
    from server.session import Session
    session = Session(state_dir=tmp_path)
    rec = session.get_concept_summary("database_migrations")
    assert rec["has_diary_entries"] is False


def test_concept_summary_for_known(tmp_path):
    from server.session import Session
    session = Session(state_dir=tmp_path)
    session.diary.record("database_migrations", "Explained rollback strategy clearly.",
                         evidence_type="explanation")
    rec = session.get_concept_summary("database_migrations")
    assert rec["has_diary_entries"] is True
    assert "explanation" in rec["evidence_summary"]


def test_concept_full_returns_entries(tmp_path):
    from server.session import Session
    session = Session(state_dir=tmp_path)
    session.diary.record("auth", "Predicted JWT expiry", evidence_type="prediction")
    data = session.get_concept_full("auth")
    assert len(data["entries"]) == 1
    assert data["entries"][0]["evidence_type"] == "prediction"


def test_linked_concepts_with_evidence(tmp_path):
    from server.session import Session
    session = Session(state_dir=tmp_path)
    session.diary.record("async_programming",
        "Explained event loop clearly. See [[promises]].",
        evidence_type="explanation")
    session.diary.record("promises",
        "Predicted .then() chaining behaviour",
        evidence_type="prediction")

    data = session.get_concept_summary("async_programming")
    linked = data["linked_concepts"]
    assert len(linked) == 1
    assert linked[0]["concept"] == "promises"
    assert linked[0]["strongest_evidence"] == "prediction"
    assert linked[0]["entries"] == 1


def test_calibration_evidence_type_accepted(tmp_path):
    from server.session import Session
    session = Session(state_dir=tmp_path)
    # calibration is Claude's private voice — should be a valid evidence type
    session.diary.record("async_programming",
        "Three rubber-stamps. Shifting SP → Sparring.",
        evidence_type="calibration")
    entries = session.diary.read("async_programming")
    assert len(entries) == 1
    assert entries[0]["evidence_type"] == "calibration"
