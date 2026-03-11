from pathlib import Path


def test_atomic_write_creates_file(tmp_path):
    from server.util import atomic_write
    target = tmp_path / "test.txt"
    atomic_write(target, "hello")
    assert target.read_text() == "hello"


def test_atomic_write_creates_backup(tmp_path):
    from server.util import atomic_write
    target = tmp_path / "test.txt"
    target.write_text("original")
    atomic_write(target, "updated")
    assert target.read_text() == "updated"
    assert (tmp_path / "test.txt.bak").read_text() == "original"


def test_atomic_write_creates_parent_dirs(tmp_path):
    from server.util import atomic_write
    target = tmp_path / "a" / "b" / "test.txt"
    atomic_write(target, "deep")
    assert target.read_text() == "deep"


def test_atomic_write_overwrites_cleanly(tmp_path):
    from server.util import atomic_write
    target = tmp_path / "test.txt"
    target.write_text("original")
    atomic_write(target, "new content")
    assert target.read_text() == "new content"
