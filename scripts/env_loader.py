#!/usr/bin/env python3
"""Load environment variables from a local .env file when present."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_env(path: str | None = None) -> None:
    if path is None:
        env_path = PROJECT_ROOT / ".env"
    else:
        env_path = Path(path)
        if not env_path.is_absolute():
            env_path = (Path.cwd() / env_path).resolve()

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())
