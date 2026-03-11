from pathlib import Path


def test_passive_detection(tmp_path):
    from server.engagement import EngagementTracker
    tracker = EngagementTracker(tmp_path / "engagement.json")
    tracker.record_prompt("ok")
    tracker.record_prompt("sure")
    tracker.record_prompt("yes")
    assert tracker.consecutive_passive >= 3
    assert tracker.is_passive_alarm()


def test_engaged_response_resets_passive(tmp_path):
    from server.engagement import EngagementTracker
    tracker = EngagementTracker(tmp_path / "engagement.json")
    tracker.record_prompt("ok")
    tracker.record_prompt("ok")
    tracker.record_prompt("I think we should use a different approach because the current one doesn't handle edge cases well")
    assert tracker.consecutive_passive == 0


def test_get_signals_returns_qualitative_data(tmp_path):
    from server.engagement import EngagementTracker
    tracker = EngagementTracker(tmp_path / "engagement.json")
    tracker.record_prompt("Can you explain how the authentication middleware works?")
    signals = tracker.get_signals()
    assert "recent_signals" in signals
    assert "consecutive_passive" in signals
    assert "is_passive_alarm" in signals
    # No numeric score
    assert "current_score" not in signals


def test_deflection_tracked_separately(tmp_path):
    from server.engagement import EngagementTracker
    tracker = EngagementTracker(tmp_path / "engagement.json")
    tracker.record_prompt("whatever")
    tracker.record_prompt("just do it")
    tracker.record_prompt("idk")
    assert tracker.consecutive_deflection >= 3
    assert tracker.consecutive_passive >= 3  # deflection is also passive
    assert tracker.is_passive_alarm()


def test_recent_signals_returns_last_n(tmp_path):
    from server.engagement import EngagementTracker
    tracker = EngagementTracker(tmp_path / "engagement.json")
    for i in range(15):
        tracker.record_prompt(f"message {i}")
    signals = tracker.recent_signals(n=5)
    assert len(signals) == 5


def test_signal_log_persists(tmp_path):
    from server.engagement import EngagementTracker
    path = tmp_path / "engagement.json"
    tracker1 = EngagementTracker(path)
    tracker1.record_prompt("ok")
    tracker1.record_prompt("ok")

    tracker2 = EngagementTracker(path)
    assert tracker2.consecutive_passive == 2


def test_reset_session_clears_log(tmp_path):
    from server.engagement import EngagementTracker
    tracker = EngagementTracker(tmp_path / "engagement.json")
    tracker.record_prompt("ok")
    tracker.record_prompt("ok")
    tracker.reset_session()
    assert tracker.consecutive_passive == 0
    assert tracker.recent_signals() == []


def test_expanded_passive_patterns(tmp_path):
    from server.engagement import EngagementTracker
    tracker = EngagementTracker(tmp_path / "engagement.json")
    for pattern in ["ship it", "merge it", "+1", "looks good"]:
        tracker.record_prompt(pattern)
    assert tracker.consecutive_passive == 4
