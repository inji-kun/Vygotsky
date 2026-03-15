"""Plan tree tests — retained as documentation of the removed MCP approach.

The PlanTree MCP server was replaced in v1 Phase 1 with file-based planning
(.claude/plans/ convention). These tests are now skipped. The planning logic
lives in the writing-plans and executing-plans skills.
"""
import pytest


@pytest.mark.skip(reason="PlanTree MCP removed in v1 Phase 1 — planning is now file-based (.claude/plans/)")
def test_create_plan_step():
    pass


@pytest.mark.skip(reason="PlanTree MCP removed in v1 Phase 1")
def test_step_creates_markdown_file():
    pass


@pytest.mark.skip(reason="PlanTree MCP removed in v1 Phase 1")
def test_nested_steps():
    pass


@pytest.mark.skip(reason="PlanTree MCP removed in v1 Phase 1")
def test_complete_step_writes_summary():
    pass


@pytest.mark.skip(reason="PlanTree MCP removed in v1 Phase 1")
def test_get_plan_state_compact():
    pass


@pytest.mark.skip(reason="PlanTree MCP removed in v1 Phase 1")
def test_tree_json_persisted():
    pass


@pytest.mark.skip(reason="PlanTree MCP removed in v1 Phase 1")
def test_no_active_plan():
    pass


@pytest.mark.skip(reason="PlanTree MCP removed in v1 Phase 1")
def test_invalid_parent_id_returns_error():
    pass
