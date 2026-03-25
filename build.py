#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pyinfra>=3",
#   "tenacity>=8",
# ]
# ///
"""Local repo shim for `uv run build.py`.

For installed usage prefer:
- uvx wagov-devcontainer
- pipx run --spec wagov-devcontainer wagov-devcontainer
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from wagov_devcontainer.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
