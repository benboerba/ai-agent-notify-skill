# Bark setup

## User-facing steps

1. Ask the user to install and open Bark on the phone.
2. Ask the user to copy the notification URL displayed by Bark and paste it into the conversation.
3. Do not ask the user to split the URL into server and key.

## Validation

Accept `http://` or `https://` URLs so self-hosted Bark remains supported. Reject placeholders, whitespace-only input, embedded newlines, and URLs without a host. Treat the entire URL as a secret.

Do not display the complete URL after receiving it. Refer to it as “已保存的 Bark 地址”.

## Configuration

Pass the URL to `scripts/configure.py` through stdin JSON:

```json
{
  "mode": "bark",
  "bark_endpoint": "USER_VALUE"
}
```

For dual mode use `mode=both` and include the WeChat fields described in the WeChat reference.

The configurator writes a mode-600 environment file. Do not put the URL directly in the sender script, a public repository, shell history, or agent configuration.

## Verification

The bundled sender calls Bark with URL-encoded `title`, `body`, `group`, and `sound` parameters. A successful HTTP request is necessary. Ask the user whether the phone received the first test only when the endpoint returns success but receipt cannot otherwise be established.

If the user explicitly migrates away from Bark, remove Bark from the active notification chain but keep the prior Bark environment/configuration file unchanged.
