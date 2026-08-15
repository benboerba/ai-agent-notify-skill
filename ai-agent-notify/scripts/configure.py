#!/usr/bin/env python3
"""Write private ai-agent-notify configuration from JSON on stdin."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from pathlib import Path
from urllib.parse import urlparse


VALID_MODES = {"bark", "wechat", "both"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="~/.config/ai-agent-notify/config.env")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def require_text(data: dict[str, object], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value:
        raise ValueError(f"missing or invalid {key}")
    return value.strip()


def validate_bark(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Bark URL must be an http(s) URL with a host")
    if "替换" in value or "YOUR_" in value.upper():
        raise ValueError("Bark URL is still a placeholder")
    return value


def main() -> int:
    args = parse_args()
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        mode = require_text(data, "mode").lower()
        if mode not in VALID_MODES:
            raise ValueError("mode must be bark, wechat, or both")

        values: dict[str, str] = {"NOTIFY_MODE": mode}
        if mode in {"bark", "both"}:
            values["BARK_ENDPOINT"] = validate_bark(require_text(data, "bark_endpoint"))
        if mode in {"wechat", "both"}:
            values["OPENCLAW_WEIXIN_ACCOUNT"] = require_text(data, "wechat_account")
            values["OPENCLAW_WEIXIN_TARGET"] = require_text(data, "wechat_target")
            values["OPENCLAW_BIN"] = require_text(data, "openclaw_bin")

        rendered = "\n".join(f"{key}={shlex.quote(value)}" for key, value in values.items()) + "\n"
        if args.dry_run:
            channels = ["bark", "wechat"] if mode == "both" else [mode]
            print(json.dumps({"ok": True, "mode": mode, "channels": channels}, ensure_ascii=False))
            return 0

        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(rendered, encoding="utf-8")
        os.chmod(temporary, 0o600)
        os.replace(temporary, output)
        os.chmod(output, 0o600)
        print(json.dumps({"ok": True, "mode": mode, "config": str(output)}, ensure_ascii=False))
        return 0
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
