# Agent completion-hook integration

## General rule

Connect the bundled `notify.py` to the host agent’s official “turn complete”, “task complete”, or equivalent hook. Inspect the operating system, installed agent, Python interpreter, and current configuration first. Do not guess a hook name or overwrite an existing hook blindly.

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

On Windows, invoke the same file with the discovered Python launcher, commonly `py` or `python`.

Use replacement only when the user explicitly asks to stop the existing delivery channel:

```bash
python3 scripts/install_codex.py --replace-existing
```

Replacement disables the previous command but does not delete its scripts, URLs, environment files, or logs.

## Other AI agents

Identify the agent’s official completion-hook mechanism from its installed documentation or current official documentation. Configure the hook to execute the detected Python interpreter plus the installed absolute path of `notify.py`, with the completion payload as arguments or stdin as supported by that agent. Never point a Windows hook at `notify.sh`.

If the agent has no completion hook:

1. Do not simulate one by polling private databases.
2. If its Skill or rules system can reliably require a tool call immediately before the final response, offer active invocation as a session-level fallback.
3. Otherwise offer a wrapper command or explain the limitation.
4. State clearly that active invocation is not a persistent global completion hook and may not cover tasks that do not load this Skill.

For Doubao, Claude Desktop, and similar hosts, inspect the installed product rather than assuming Codex paths exist. Do not create `~/.codex/config.toml` for another agent.

After integration, trigger one harmless, short agent task and verify exactly one notification per selected channel.
