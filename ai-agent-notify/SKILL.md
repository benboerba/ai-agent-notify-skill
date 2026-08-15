---
name: ai-agent-notify
description: Set up AI-agent task-completion notifications through Bark, a dedicated WeChat chat, or both. Use when a user asks to receive completion alerts on their phone, install or switch Bark notifications, bind WeChat by QR code, configure dual-channel alerts, test delivery, migrate notification channels while retaining old credentials, or connect another local AI agent's completion hook to mobile notifications.
---

# AI Agent Notify

Give ordinary users one simple choice and complete the technical setup for them.

## Start with one choice

Ask exactly one question before making changes:

1. `Bark 通知` — the user installs Bark and provides the notification URL shown by the app.
2. `微信通知` — the user scans a QR code and receives alerts in a dedicated WeChat chat.
3. `两种都安装` — send every completion alert to both channels.

Use a structured choice UI when available. Do not ask the user about CLIs, tokens, account IDs, hooks, configuration paths, or implementation details.

## Safety rules

- Read the selected channel references completely before acting: [Bark](references/bark.md), [WeChat](references/wechat.md), or both.
- Read [Agent integration](references/agent-integration.md) before editing any completion hook.
- Treat Bark URLs, WeChat QR URLs, credentials, account IDs, target IDs, context tokens, and message bodies as sensitive.
- Never print a complete Bark URL or WeChat credential in logs or final replies.
- Generate WeChat QR images locally. Never send binding URLs to third-party QR services.
- Preserve unrelated integrations. Never delete an old URL, credential, script, QR image, log, or backup without explicit user approval.
- When replacing Bark, stop invoking it but retain the Bark URL file unchanged.
- Do not call setup successful until each selected channel returns a verified test delivery.

## Workflow

1. Ask the three-option question and record the choice.
2. Inspect the host agent, its completion hook, and existing notification chain without exposing secrets.
3. Configure Bark, WeChat, or both according to the selected references.
4. Use `scripts/configure.py` to create a private channel configuration. Pass secrets through stdin JSON; do not place them in command arguments.
5. Install `scripts/notify.sh` as the stable sender.
6. For Codex, use `scripts/install_codex.py` to preserve or replace the existing `notify` chain intentionally. For other agents, follow their official completion-hook mechanism.
7. Run `notify.sh --dry-run` to confirm the selected routing without sending.
8. Run a uniquely named live test. Validate Bark’s HTTP success and WeChat’s structured delivery receipt independently.
9. Report only the channels enabled, the test result for each, and whether previous configuration was retained.

## Channel result rules

- `bark`: require Bark test success.
- `wechat`: require `payload.deliveryStatus=sent` and every payload outcome `status=sent`.
- `both`: require both tests. If one succeeds and one fails, report partial completion and repair only the failed channel.

## Reconfiguration

- Switching mode must update the active mode without deleting saved credentials for the inactive channel.
- Rebinding WeChat must identify the new account by comparing account sets before and after scanning; never assume the default account changed.
- Replacing a host hook must preserve a backup and avoid broad rewrites of the agent configuration.
