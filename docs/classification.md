# Component classification（组件分类）

基于实际配置（2026-08-19 盘点）的五类划分。**本仓库只发布 CORE**；
其余类别留在个人完整配置中，不进入公开仓库。

## CORE — 进本仓库（换领域 / 换模型 / 换 Harness 仍成立）

| 类别 | 组件 |
|---|---|
| Project OS | `PROJECT.md` `STATE.md` `PLAN.md` `DECISIONS.md` `HANDOFF.md` `EXPERIMENT_GATE.json`（→ `core/project/`） |
| Core Rules | 工作流、委托协议、HANDOFF 规则、科学不变量、Review 触发、安全升级（→ `core/policies/CORE.md`） |
| Skills (9) | agent-workflow-optimizer · experiment-scientist · experiment-reviewer · compute-budget · reproducibility · evidence-synthesizer · failure-triage · code-reviewer(+references) · repo-architecture |
| Roles (5) | research-lead · scout · runner · reviewer · auditor（只定义职责，不绑模型） |
| Runtime | continuity（compaction 连续性）· research-guard（实验 gate）· Trusted Mode 权限基线 |

## OPTIONAL（通用但本版不公开，可留待未来选装）

- knowledge-retrieval、find-skills：通用工具类，非 Core 必要
- ui-review：前端审查流程
- vision、research-reviewer、image-server：视觉/仲裁/本地图像服务（依赖具体能力与本地环境）
- code-minimalism：**许可证受限**（CC BY-NC-SA 衍生），为保持 Core 许可干净（MIT）而排除

## DOMAIN-SPECIFIC（领域专用，排除）

- scheduling-experiment-design：GPU/Agent 调度研究领域专用（含 GPU 调度专属规则），换领域不适用

## HARNESS-SPECIFIC（执行器专属 → `adapters/<harness>/`）

- OpenCode 的 agent front-matter 语法、permission 矩阵、plugin（API hook）、`.jsonc` 配置结构
- 以及完整清单如 `opencode.jsonc`、MCP、server 配置
- 规则：Core 永不出现这些；执行器细节只进 adapter

## PRIVATE（个人环境，绝不公开）

- 个人 Provider：千帆 Token Plan（含明文 apiKey）、sensenova、OpenAI 专属端点
- SSH MCP：远程主机 / 端口 / 用户名 / 私钥路径
- 个人模型选择（role→model 映射、reasoning 档位）
- 本机绝对路径（`~` 下的目录偏好）、oh-my-openagent.json
- GPU 资金配置与内部运行细节

## 排除对照（用户明确不要公开的项 → 归类）

| 排除项 | 归类 |
|---|---|
| code-minimalism | OPTIONAL（许可受限） |
| scheduling-experimentation | DOMAIN-SPECIFIC |
| find-skills / knowledge-retrieval | OPTIONAL |
| paper-figure-generator / office-docs / ui-review / openai-docs | OPTIONAL（通用但排除）/ 其中 openai-docs 同时是 OpenAI HARNESS 关联 |
| vision / research-reviewer / image-server | OPTIONAL（依赖具体能力） |
| 我的 Provider / OpenAI / 千帆 / SSH / server / 私有路径 | PRIVATE |
| GPU scheduling 落地规则 | DOMAIN-SPECIFIC |