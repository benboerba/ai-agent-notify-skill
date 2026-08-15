# WeChat setup

## Connector check

Use the local `openclaw` executable and the official `@tencent-weixin/openclaw-weixin` channel package. If OpenClaw is missing, explain that a local WeChat connector is required and obtain approval before installing it from current official instructions. Do not invent an installer URL.

Check without exposing credentials:

```bash
openclaw --version
openclaw plugins list
openclaw channels status --probe --json
```

If the WeChat channel is missing, install and enable the official package, then restart the OpenClaw gateway.

## QR binding

1. Record the currently configured WeChat account IDs.
2. Start `openclaw channels login --channel openclaw-weixin` in a live interactive session.
3. Keep that process alive while the user scans.
4. Extract its current `liteapp.weixin.qq.com` URL and render it locally with an installed QR renderer.
5. Show only the current QR image. A QR becomes invalid when the login process exits.
6. If it expires, render the refreshed URL from the still-running process. If the process exhausts refreshes, start a new login before displaying another image.
7. After success, compare account sets to identify the newly added account. Do not use the default-account field as proof.

Read only the new account’s public routing fields from local metadata. Never print the whole account file.

## Conversation activation

Ask the user to open the new dedicated WeChat chat and send `测试`. Verify the new account has a non-null inbound timestamp newer than the login. A running channel alone does not mean proactive delivery is prepared.

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
