# OpenCode adapter

把 Research Agent OS Core 装配到 [OpenCode](https://opencode.ai)。Core 本身与 harness 无关；
本目录是 OpenCode 专属实现（agent 文件语法、权限、插件 API）。

## 装配内容

| 路径 | 作用 | 安装到 |
|---|---|---|
| `agents/*.md`（5 个 Core 角色） | research-lead / scout / runner / reviewer / auditor | `~/.config/opencode/agents/` |
| `../core/skills/`（9 个） | 程序性技能 | `~/.config/opencode/skills/` |
| `plugins/`（continuity.ts, research-guard.js） | HANDOFF 连续性 + 安全 gate | `~/.config/opencode/plugins/`（自动加载） |
| `AGENTS.md.header` + `../core/policies/CORE.md` | 全局规则（install 装配） | `~/.config/opencode/AGENTS.md` |
| `permissions.example.jsonc` | Trusted Mode 权限基线 | merge 进你的 `opencode.json` |

## 角色与模型

- 5 个角色**只定义职责**，front-matter 不含 `model` / `variant`。
- 主代理模型由你配置（OpenCode：`opencode.json` 顶层 `"model": "<provider>/<model>"`）。
- 子代理未指定模型时继承调用它的主代理模型；按角色覆盖：

```jsonc
{ "agent": { "scout": { "model": "<provider>/<your-fast-model>" } } }
```

### 关闭某个子代理（可选）

不需要某角色时，在 `opencode.json` 里禁用即可，角色定义保持默认：

```jsonc
{ "agent": { "runner": { "disable": true } } }
```

其它角色不受影响。

## Trusted Mode

`permissions.example.jsonc` 是权限基线：普通工作区命令自动放行；`sudo` / `rm -rf` /
`git reset --hard` / `git clean` / force push / env 泄露读取 / `.env`·`.pem`·`.key` 写入全部
拒绝或询问。把它 merge 到 `opencode.json` 的 `"permission"` 字段（或运行 install 时按提示合并）。

## Continuity & gate

- `plugins/continuity.ts`：上下文压缩时自动注入 `.project/HANDOFF.md`（回退 `.project/STATE.md`）。
- `plugins/research-guard.js`：正式实验前校验 `.project/EXPERIMENT_GATE.json` 的
  `smoke_passed` / `ledger_registered` / `commit` 契约；拦截破坏性命令与密钥读取。

## Quick Start

```bash
./scripts/install.sh          # 安装 agents/skills/plugins/AGENTS.md（幂等，--dry-run 预览）
python3 scripts/doctor.py     # 验证安装：READY / READY WITH WARNINGS / NOT READY
python3 scripts/init-project.py --dir <your-project>   # 生成 Project OS 控制面
```