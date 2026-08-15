#!/usr/bin/env python3
"""Install the bundled sender into Codex while preserving unrelated settings."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preserve-existing", action="store_true")
    group.add_argument("--replace-existing", action="store_true")
    parser.add_argument("--codex-home", default="~/.codex")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser().resolve()
    config = codex_home / "config.toml"
    source_dir = Path(__file__).resolve().parent
    scripts_dir = codex_home / "scripts"
    sender = scripts_dir / "ai-agent-notify.py"
    dispatcher = scripts_dir / "ai-agent-notify-dispatcher.py"
    previous_file = codex_home / "ai-agent-notify-previous.json"
    backup = codex_home / "config.toml.ai-agent-notify.bak"

    text = config.read_text(encoding="utf-8") if config.exists() else ""
    notify_pattern = re.compile(r"(?m)^notify\s*=\s*(\[[^\n]*\])\s*$")
    notify_match = notify_pattern.search(text)
    if re.search(r"(?m)^notify\s*=", text) and not notify_match:
        print(json.dumps({"ok": False, "error": "top-level notify must be a one-line string array"}), file=sys.stderr)
        return 2
    try:
        current = json.loads(notify_match.group(1)) if notify_match else []
    except json.JSONDecodeError as exc:
        print(json.dumps({"ok": False, "error": f"invalid notify array: {exc}"}), file=sys.stderr)
        return 2
    if not isinstance(current, list) or not all(isinstance(item, str) for item in current):
        print(json.dumps({"ok": False, "error": "top-level notify must contain strings"}), file=sys.stderr)
        return 2

    already_installed = any("ai-agent-notify-dispatcher.py" in item for item in current)
    if args.replace_existing:
        previous = []
    elif already_installed:
        try:
            saved_previous = json.loads(previous_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            saved_previous = []
        previous = saved_previous if isinstance(saved_previous, list) and all(isinstance(item, str) for item in saved_previous) else []
    else:
        previous = current
    new_notify = [sys.executable, str(dispatcher)]

    if args.dry_run:
        print(json.dumps({"ok": True, "dryRun": True, "preserveExisting": bool(previous), "alreadyInstalled": already_installed}))
        return 0

    codex_home.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    if config.exists() and not backup.exists():
        shutil.copy2(config, backup)

    shutil.copy2(source_dir / "notify.py", sender)
    shutil.copy2(source_dir / "notify_dispatcher.py", dispatcher)
    try:
        os.chmod(sender, 0o700)
        os.chmod(dispatcher, 0o700)
    except OSError:
        pass
    previous_file.write_text(json.dumps(previous, ensure_ascii=False), encoding="utf-8")
    try:
        os.chmod(previous_file, 0o600)
    except OSError:
        pass

    rendered = json.dumps(new_notify, ensure_ascii=False)
    line = f"notify = {rendered}"
    pattern = re.compile(r"(?m)^notify\s*=\s*\[[^\n]*\]\s*$")
    if pattern.search(text):
        updated = pattern.sub(line, text, count=1)
    else:
        updated = line + "\n" + text
    temporary = config.with_suffix(".toml.tmp")
    temporary.write_text(updated, encoding="utf-8")
    os.replace(temporary, config)

    print(json.dumps({"ok": True, "installed": str(sender), "preservedPrevious": bool(previous), "backup": str(backup) if backup.exists() else None}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
