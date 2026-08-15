# Windows setup

## Platform discovery

Before installing, discover rather than assume:

- available Python launcher: prefer `py -3`, otherwise `python`;
- OpenClaw path: use `where openclaw`; npm commonly returns `%APPDATA%\\npm\\openclaw.cmd`;
- host agent and its real completion-hook capability;
- gateway service state.

Do not require Bash, `curl`, `python3`, systemd, `~/.codex`, or Unix executable bits.

## Sender and configuration

Use `scripts/notify.py` directly. Pass its absolute path together with the discovered Python executable to the host hook. The Python sender handles `.cmd` and `.bat` OpenClaw launchers through `cmd.exe`, decodes UTF-8 output defensively, and tolerates wrapper text around JSON.

Use the same configuration path, expanded through the user profile:

```text
~/.config/ai-agent-notify/config.env
```

`chmod` is best-effort on Windows and is not equivalent to a Unix mode-600 ACL. Keep the file outside repositories and shared folders, do not print it, and do not claim stronger protection than the host provides.

## WeChat gateway and login

OpenClaw may install the gateway as a Windows Scheduled Task through `schtasks`; do not look for systemd. Verify it using OpenClaw’s own gateway and channel status commands.

Run WeChat login in the user’s visible PowerShell or Windows Terminal when the agent lacks a real TTY:

```powershell
openclaw channels login --channel openclaw-weixin
```

Let OpenClaw display its ASCII QR. Do not launch this command as a hidden background task, and do not run the package installer again merely to obtain another QR.

## Verification

Run a routing dry-run with the discovered Python command, then a live test. Chinese output must not be decoded with the Windows locale default. Require Bark HTTP success and the structured WeChat receipt independently.
