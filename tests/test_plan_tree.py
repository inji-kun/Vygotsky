from pathlib import Path


def test_create_plan_step(tmp_path):
    from server.plan_tree import PlanTree
    tree = PlanTree(tmp_path / "plans")
    result = tree.plan_step("Add user authentication")
    assert "step_id" in result
    assert "breadcrumb" in result
    assert "plan_id" in result
    assert (tmp_path / "plans" / result["plan_id"]).is_dir()


def test_step_creates_markdown_file(tmp_path):
    from server.plan_tree import PlanTree
    tree = PlanTree(tmp_path / "plans")
    result = tree.plan_step("Add user authentication", reasoning="JWT for stateless API")
    plan_dir = tmp_path / "plans" / result["plan_id"]
    step_files = list(plan_dir.glob("step_*.md"))
    # Filter out summary files
    step_files = [f for f in step_files if "_summary" not in f.name]
    assert len(step_files) == 1
    content = step_files[0].read_text()
    assert "Add user authentication" in content
    assert "JWT" in content


def test_nested_steps(tmp_path):
    from server.plan_tree import PlanTree
    tree = PlanTree(tmp_path / "plans")
    parent = tree.plan_step("Add auth")
    child = tree.plan_step("Design schema", parent_id=parent["step_id"])
    assert "Add auth" in child["breadcrumb"]
    assert "Design schema" in child["breadcrumb"]


def test_complete_step_writes_summary(tmp_path):
    from server.plan_tree import PlanTree
    tree = PlanTree(tmp_path / "plans")
    step = tree.plan_step("Add auth")
    tree.complete_step(step["step_id"], "User chose JWT with bcrypt")
    plan_dir = tmp_path / "plans" / step["plan_id"]
    summary_files = list(plan_dir.glob("*_summary.md"))
    assert len(summary_files) == 1
    content = summary_files[0].read_text()
    assert "JWT" in content


def test_get_plan_state_compact(tmp_path):
    from server.plan_tree import PlanTree
    tree = PlanTree(tmp_path / "plans")
    step1 = tree.plan_step("Add auth")
    tree.plan_step("Design schema", parent_id=step1["step_id"])
    state = tree.get_plan_state()
    assert "breadcrumb" in state
    assert "active_step" in state
    assert "siblings" in state


def test_tree_json_persisted(tmp_path):
    from server.plan_tree import PlanTree
    tree = PlanTree(tmp_path / "plans")
    result = tree.plan_step("Add auth")
    plan_dir = tmp_path / "plans" / result["plan_id"]
    assert (plan_dir / "tree.json").exists()


def test_no_active_plan(tmp_path):
    from server.plan_tree import PlanTree
    tree = PlanTree(tmp_path / "plans")
    state = tree.get_plan_state()
    assert state["breadcrumb"] == "(no active plan)"


def test_invalid_parent_id_returns_error(tmp_path):
    from server.plan_tree import PlanTree
    tree = PlanTree(tmp_path / "plans")
    result = tree.plan_step("Child step", parent_id="nonexistent_step")
    assert "error" in result
    assert "nonexistent_step" in result["error"]
    assert "suggestion" in result
    # Should NOT have created a step
    assert len(tree.steps) == 0
