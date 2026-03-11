import pytest
from pathlib import Path


def test_record_creates_concept_file(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("async_programming", "First encounter. Asked good questions about the event loop.")
    concept_file = tmp_path / "diary" / "async-programming.md"
    assert concept_file.exists()
    content = concept_file.read_text()
    assert "event loop" in content


def test_record_appends_to_existing(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("async_programming", "First encounter. Confused about promises.")
    diary.record("async_programming", "Came back to this. Explained await clearly.")
    content = (tmp_path / "diary" / "async-programming.md").read_text()
    assert "Confused about promises" in content
    assert "Explained await clearly" in content


def test_read_returns_entries(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("async_programming", "Strong understanding of event loop.")
    entries = diary.read("async_programming")
    assert len(entries) == 1
    assert "event loop" in entries[0]["observation"]


def test_read_nonexistent_returns_empty(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    entries = diary.read("never_seen_this")
    assert entries == []


def test_list_concepts(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("async_programming", "Good.")
    diary.record("database_migrations", "New territory.")
    concepts = diary.list_concepts()
    assert set(concepts) == {"async-programming", "database-migrations"}


def test_get_context_returns_recent(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("async_programming", "Strong understanding.")
    diary.record("database_migrations", "Totally new.")
    ctx = diary.get_context()
    assert "async_programming" in ctx or "async-programming" in ctx
    assert "database_migrations" in ctx or "database-migrations" in ctx


def test_related_concepts_linked(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("async_programming", "This connects to [[error_handling]] — they struggled with try/catch in async.")
    diary.record("error_handling", "Weak on this. See [[async_programming]].")
    links = diary.get_links("async_programming")
    assert "error_handling" in links


def test_get_context_empty_diary(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    ctx = diary.get_context()
    assert "no observations" in ctx.lower() or "new learner" in ctx.lower()


def test_observation_with_markdown_headers(tmp_path):
    """Observations containing ### should not break parsing."""
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    obs = "User showed code with:\n### My Heading\nsome content"
    diary.record("markdown_test", obs)
    entries = diary.read("markdown_test")
    assert len(entries) == 1
    assert "### My Heading" in entries[0]["observation"]


def test_utc_timestamp_format(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("time_test", "Test observation")
    entries = diary.read("time_test")
    assert entries[0]["timestamp"].endswith("Z")
    assert "T" in entries[0]["timestamp"]


def test_concept_name_hyphen_slugification(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("API Gateway", "First encounter")
    assert (tmp_path / "diary" / "api-gateway.md").exists()
    entries = diary.read("API Gateway")
    assert len(entries) == 1


def test_evidence_type_stored_and_retrieved(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("auth", "Explained JWT flow clearly", evidence_type="explanation")
    entries = diary.read("auth")
    assert len(entries) == 1
    assert entries[0]["evidence_type"] == "explanation"


def test_evidence_type_defaults_to_acknowledgment(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("auth", "User said ok")
    entries = diary.read("auth")
    assert entries[0]["evidence_type"] == "acknowledgment"


def test_evidence_summary(tmp_path):
    from server.learner_diary import LearnerDiary
    diary = LearnerDiary(tmp_path / "diary")
    diary.record("auth", "Predicted JWT expiry behaviour", evidence_type="prediction")
    diary.record("auth", "Explained token refresh", evidence_type="explanation")
    diary.record("auth", "Said ok", evidence_type="acknowledgment")
    summary = diary.get_evidence_summary("auth")
    assert "3 entries" in summary
    assert "prediction" in summary
    assert "explanation" in summary
