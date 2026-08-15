# AI Agent 完成通知 Skill

仓库地址：[https://github.com/benboerba/ai-agent-notify-skill](https://github.com/benboerba/ai-agent-notify-skill)

让AI Agent完成任务后主动通知手机。安装时让用户选择：

1. Bark通知
2. 微信通知
3. Bark和微信同时通知

用户不需要理解Webhook、账号ID或消息网关。AI Agent会引导用户安装Bark并填写通知URL，或通过OpenClaw二维码完成微信绑定，然后接入任务完成通知并测试。

支持 macOS、Linux 和 Windows。Windows 使用跨平台 Python 发送器，不依赖 Bash；如果 Agent 无法提供真实交互终端，会明确引导用户在 PowerShell 中完成扫码，不会把后台登录进程卡死。

## 安装给 Codex

把仓库中的 `ai-agent-notify` 文件夹复制到：

```text
~/.codex/skills/ai-agent-notify
```

也可以直接让Codex执行：

```text
请从 https://github.com/benboerba/ai-agent-notify-skill 安装 ai-agent-notify Skill。安装后使用它，帮我选择并配置 Bark、微信或双通道任务完成通知。
```

安装后可这样使用：

```text
使用 $ai-agent-notify 帮我安装AI任务完成通知。
```

## 交给其他 AI Agent 安装

将下面这段话发给具备本地文件和命令执行能力的AI Agent：

```text
请安装 https://github.com/benboerba/ai-agent-notify-skill 中的 ai-agent-notify Skill：
1. 将完整的 ai-agent-notify 目录复制到你的用户级 Skills 目录；
2. 完整读取 SKILL.md，不要只复制脚本；
3. 保留 scripts、references 和 agents 子目录；
4. 验证 SKILL.md 能被发现；
5. 安装后立即使用该 Skill，引导我选择 Bark、微信或两者同时通知；
6. 不要在回复或日志里展示我的 Bark URL、微信二维码链接或登录凭据。
```

如果目标AI Agent没有Skills机制，也可以完整读取 `ai-agent-notify/SKILL.md`，并按其中流程执行。目标Agent必须具备本地命令执行能力；纯云端、无法访问用户电脑的Agent不能自动接入本地任务完成钩子。

## 隐私与安全

- Bark URL和微信凭据只保存在用户本机；Unix限制为仅用户可读，Windows采用系统允许的最佳保护并避开仓库和共享目录。
- 微信二维码优先由OpenClaw在本地终端直接显示，不经过第三方二维码网站。
- 切换通知方式不会自动删除旧URL、凭据、日志或备份。
- 仓库不包含任何用户密钥、Bark地址或微信账号信息。

## 仓库结构

```text
ai-agent-notify/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/
```

Skill支持Codex的自动接入，并为其他Agent提供通用完成钩子接入规则。对于没有完成钩子的Agent，会明确说明只能使用会话级主动调用或外部包装，不会假装已经获得全局自动通知能力。
