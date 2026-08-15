# Agent completion-hook integration

## General rule

Connect the bundled `notify.sh` to the host agent’s official “turn complete”, “task complete”, or equivalent hook. Inspect the installed agent and current configuration first. Do not guess a hook name or overwrite an existing hook blindly.

If the host has an existing notifier, preserve it through a dispatcher unless the user explicitly asks to replace that channel. Avoid duplicate entries.

## Codex

Codex uses the top-level `notify` command array in `~/.codex/config.toml`. Use `scripts/install_codex.py` rather than rewriting the full TOML file.

The installer:

- copies the bundled sender and dispatcher into `~/.codex/scripts/`;
- stores the previous notify command in a private JSON file when preservation is requested;
- changes only the top-level `notify` assignment;
- keeps one backup of the original Codex config;
- is idempotent when run again.

Use preserve mode by default:

```bash
python3 scripts/install_codex.py --preserve-existing
```

Use replacement only when the user explicitly asks to stop the existing delivery channel:

```bash
python3 scripts/install_codex.py --replace-existing
```

Replacement disables the previous command but does not delete its scripts, URLs, environment files, or logs.

## Other AI agents

Identify the agent’s official completion-hook mechanism from its installed documentation or current official documentation. Configure the hook to execute the installed absolute path of `notify.sh` with the completion payload as arguments or stdin, as supported by that agent.

If the agent has no completion hook, do not simulate one by polling private databases without telling the user. Offer a wrapper command or explain the limitation.

After integration, trigger one harmless, short agent task and verify exactly one notification per selected channel.
