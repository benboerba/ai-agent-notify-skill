#!/usr/bin/env python3
"""Cross-platform Bark and WeChat completion notifier."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


VALID_MODES = {"bark", "wechat", "both"}
IGNORED_EVENT_ARGS = {"turn-ended", "task-complete", "manual-test", "test", "test-run", "--dry-run", ""}


def config_path() -> Path:
    raw = os.environ.get("AI_AGENT_NOTIFY_CONFIG", "~/.config/ai-agent-notify/config.env")
    return Path(raw).expanduser()


def state_dir() -> Path:
    raw = os.environ.get("AI_AGENT_NOTIFY_STATE_DIR", "~/.local/state/ai-agent-notify")
    return Path(raw).expanduser()


def decode_env_value(raw: str) -> str:
    try:
        parts = shlex.split(raw, posix=True)
    except ValueError:
        parts = []
    if len(parts) == 1:
        return parts[0]
    return raw.strip().strip("'\"")


def load_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return values
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, raw = stripped.split("=", 1)
        key = key.strip()
        if key and all(char.isalnum() or char == "_" for char in key):
            values[key] = decode_env_value(raw.strip())
    return values


def event_name(args: list[str]) -> str:
    for arg in args:
        if arg in IGNORED_EVENT_ARGS:
            continue
        if arg.lstrip().startswith("{"):
            try:
                payload = json.loads(arg)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                for key in ("thread_name", "session_name", "conversation_name", "title", "name"):
                    value = payload.get(key)
                    if isinstance(value, str) and value.strip():
                        return value.strip()[:100]
            continue
        return arg[:100]
    return "当前 AI Agent 任务"


def bark_url(endpoint: str, title: str, body: str, config: dict[str, str]) -> str:
    parts = urlsplit(endpoint)
    query = parse_qsl(parts.query, keep_blank_values=True)
    query.extend(
        [
            ("title", title),
            ("body", body),
            ("group", config.get("BARK_GROUP", "AI Agent")),
            ("sound", config.get("BARK_SOUND", "bell")),
        ]
    )
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def send_bark(endpoint: str, title: str, body: str, config: dict[str, str]) -> bool:
    request = Request(bark_url(endpoint, title, body, config), method="GET")
    try:
        with urlopen(request, timeout=12) as response:
            return 200 <= int(response.status) < 300
    except Exception:
        return False


def openclaw_command(executable: str, account: str, target: str, message: str) -> list[str]:
    arguments = [
        "message",
        "send",
        "--channel",
        "openclaw-weixin",
        "--account",
        account,
        "--target",
        target,
        "--message",
        message,
        "--json",
    ]
    if os.name == "nt" and executable.lower().endswith((".cmd", ".bat")):
        return [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/s", "/c", executable, *arguments]
    return [executable, *arguments]


def decode_output(value: bytes | None) -> str:
    return (value or b"").decode("utf-8", errors="replace")


def extract_json(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    decoder = json.JSONDecoder()
    objects: list[dict[str, Any]] = []
    for index, character in enumerate(cleaned):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(cleaned[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            objects.append(value)
    for value in reversed(objects):
        if isinstance(value.get("payload"), dict):
            return value
    return objects[-1] if objects else None


def receipt_is_sent(data: dict[str, Any] | None) -> bool:
    if not data:
        return False
    payload = data.get("payload")
    if not isinstance(payload, dict) or payload.get("deliveryStatus") != "sent":
        return False
    outcomes = payload.get("payloadOutcomes")
    return isinstance(outcomes, list) and bool(outcomes) and all(
        isinstance(item, dict) and item.get("status") == "sent" for item in outcomes
    )


def send_wechat(executable: str, account: str, target: str, message: str) -> bool:
    try:
        result = subprocess.run(
            openclaw_command(executable, account, target, message),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    combined = decode_output(result.stdout) + "\n" + decode_output(result.stderr)
    return result.returncode == 0 and receipt_is_sent(extract_json(combined))


def append_log(directory: Path, mode: str, bark: str, wechat: str, name: str) -> None:
    try:
        directory.mkdir(parents=True, exist_ok=True)
        log = directory / "notify.log"
        with log.open("a", encoding="utf-8") as handle:
            handle.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"mode={mode} bark={bark} wechat={wechat} event={name}\n"
            )
    except OSError:
        pass


def main() -> int:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    config = load_config(config_path())
    mode = config.get("NOTIFY_MODE", "")
    if mode not in VALID_MODES:
        return 2

    name = event_name(args)
    title = config.get("NOTIFY_TITLE", f"AI Agent 已完成：{name}")
    body = config.get("NOTIFY_BODY", f"任务「{name}」已经结束，可以回来查看结果了。")
    if dry_run:
        print(json.dumps({"ok": True, "dryRun": True, "mode": mode}, ensure_ascii=False))
        return 0

    bark_status = "skipped"
    wechat_status = "skipped"
    failed = False

    if mode in {"bark", "both"}:
        endpoint = config.get("BARK_ENDPOINT", "")
        if not endpoint:
            bark_status, failed = "missing-config", True
        elif send_bark(endpoint, title, body, config):
            bark_status = "sent"
        else:
            bark_status, failed = "failed", True

    if mode in {"wechat", "both"}:
        executable = config.get("OPENCLAW_BIN", "")
        account = config.get("OPENCLAW_WEIXIN_ACCOUNT", "")
        target = config.get("OPENCLAW_WEIXIN_TARGET", "")
        if not executable or not account or not target:
            wechat_status, failed = "missing-config", True
        elif send_wechat(executable, account, target, f"✅ {title}\n\n{body}"):
            wechat_status = "sent"
        else:
            wechat_status, failed = "failed", True

    append_log(state_dir(), mode, bark_status, wechat_status, name)
    print(
        json.dumps(
            {"ok": not failed, "mode": mode, "bark": bark_status, "wechat": wechat_status},
            ensure_ascii=False,
        )
    )
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
