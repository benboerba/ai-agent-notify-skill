#!/usr/bin/env python3
"""Run the previous Codex notifier and ai-agent-notify without recursion."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


CODEX_HOME = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
PREVIOUS_FILE = CODEX_HOME / "ai-agent-notify-previous.json"
SENDER = CODEX_HOME / "scripts" / "ai-agent-notify.py"


def load_previous() -> list[str]:
    try:
        value = json.loads(PREVIOUS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return []
    joined = " ".join(value)
    if "notify_dispatcher.py" in joined or "ai-agent-notify.py" in joined or "ai-agent-notify.sh" in joined:
        return []
    return value


def launch(command: list[str]) -> None:
    if not command:
        return
    try:
        subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
        )
    except OSError:
        pass


def main() -> int:
    args = sys.argv[1:]
    previous = load_previous()
    if previous:
        launch(previous + args)
    if SENDER.exists():
        launch([sys.executable, str(SENDER), *args])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
