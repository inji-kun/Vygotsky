"""Shared utilities for Vygotsky server."""

import os
import shutil
import tempfile
from pathlib import Path


def atomic_write(path: Path, content: str) -> None:
    """Write content to file atomically via temp file + rename.

    Creates a .bak copy of the existing file before overwriting.
    On POSIX, os.rename() is atomic within the same filesystem.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing file
    if path.exists():
        bak = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, bak)

    # Write to temp file in same directory, then atomic rename
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.rename(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
