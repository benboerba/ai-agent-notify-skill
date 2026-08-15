# WeChat setup

## Connector check

Use the local `openclaw` executable and the official `@tencent-weixin/openclaw-weixin` channel package. Resolve its real path before configuration. On Windows, npm commonly installs `%APPDATA%\\npm\\openclaw.cmd`; do not write a Unix default into Windows configuration. If OpenClaw is missing, explain that a local WeChat connector is required and obtain approval before installing it from current official instructions. Do not invent an installer URL.

Check without exposing credentials:

```bash
openclaw --version
openclaw plugins list
openclaw channels status --probe --json
```

If the WeChat channel is missing, install and enable the official package, then restart the OpenClaw gateway.

## QR binding

1. Record the currently configured WeChat account IDs.
2. Run `openclaw channels login --channel openclaw-weixin` only in a real interactive TTY.
3. If the agent cannot provide a real TTY, do not start the command in the background: it may produce no output and hang. Give the user the exact command for their own Terminal or PowerShell, pause, and continue after they confirm scanning.
4. Prefer the ASCII QR code printed by OpenClaw. No extra QR dependency is required.
5. If the agent has a working interactive session and deliberately extracts the current `liteapp.weixin.qq.com` URL, render it only with a local QR tool. Never use a third-party QR website.
6. Keep the login process alive while the QR is displayed. A QR becomes invalid when the login process exits.
7. If it expires, use the refreshed QR from the live process. If the process ended, start a new login before showing another QR.
8. After success, compare account sets to identify the newly added account. Do not use the default-account field as proof.

Read only the new account’s public routing fields from local metadata. Never print the whole account file. Standard metadata locations are:

- account list: `~/.openclaw/openclaw-weixin/accounts.json`;
- account details: `~/.openclaw/openclaw-weixin/accounts/<accountId>.json`;
- active sessions: `~/.openclaw/agents/main/sessions/sessions.json`.

The account `userId` is not the recipient target. Derive the target from the activated session’s `origin.from` or `route.target.to`, and match it to the newly bound account and recent inbound message.

## Conversation activation

Ask the user to open the new dedicated WeChat chat and send `测试`. Verify `openclaw channels status --probe --json` reports a non-null `lastInboundAt` newer than the login, then locate the corresponding target in the session metadata. A running channel alone does not mean proactive delivery is prepared.

`sendMessage ret=-2` or `prepare failed` normally means this activation step is incomplete.

## Configuration

Pass values through stdin JSON:

```json
{
  "mode": "wechat",
  "wechat_account": "NEW_ACCOUNT_ID",
  "wechat_target": "NEW_USER_ID",
  "openclaw_bin": "/absolute/path/to/openclaw"
}
```

For dual mode use `mode=both` and include `bark_endpoint`.

## Verification

Send one unique test with JSON output. Require:

- process exit code zero;
- `payload.deliveryStatus` equals `sent`;
- `payload.payloadOutcomes` is non-empty;
- every outcome has `status=sent`.

Do not infer success merely because the gateway is running or stderr is empty.

The sender decodes subprocess output as UTF-8 with replacement and extracts a JSON object even when npm wrappers or ANSI output surround it. Keep the structured receipt requirements above; return code zero alone is not proof of delivery.
