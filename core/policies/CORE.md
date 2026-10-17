# Research Agent OS — Core Rules（CORE.md）

**本文件是 Core 的唯一规则源。** Adapter 与执行环境必须忠实装配/引用本文件；脱离任何 harness 时规则依然成立。
详细操作流程在 `core/skills/`（按需加载）；本文件只保留宪法级硬规则与指针。

## 使命

维持长期 AI 辅助科研/工程的**可复现性**：保留证据、可重现、控制算力预算。
实现状态、实验证据、科学 claim 必须严格分离。

## 三条不变原则

1. **换研究领域仍有用**——不绑定任何领域术语、工作负载或数据格式。
2. **换模型仍有用**——角色只定义职责，永不绑定模型 / Provider / 推理强度。
3. **换 Harness 仍有用**——核心不依赖任何执行器的文件语法、权限体系或插件 API。
   （`core/` 永不出现执行器专名；执行器专属内容一律放 `adapters/<harness>/`）

## 默认工作流

```text
inspect → plan → execute → verify → review → persist → handoff
```

- 行动前先看真实文件、接口、契约、schema、产物、现有状态；不凭记忆/猜测。
- 实际改动前建立紧凑边界：goal / scope / 允许·禁止 / 成功标准 / 升级条件。
- 边界内自主执行，不二次确认普通编辑测试；不静默扩大边界。
- 每次验证用最小相关测试；exit code 0 不等于科学成功。

## Project State（项目控制面）

每个研究/长期项目以项目根 `.project/` 为唯一长期状态真相源。canonical 文件：

| 文件 | 内容 |
|---|---|
| `PROJECT.md` | 目标、范围、约束、架构概览 |
| `STATE.md` | 当前真实状态、已验证结论、问题、阶段、风险 |
| `PLAN.md` | 唯一当前执行计划 |
| `DECISIONS.md` | 重要决策及原因（追加记录，不删） |
| `HANDOFF.md` | 面向断联/压缩的恢复快照（覆盖更新，非日志） |
| `EXPERIMENT_GATE.json` | 正式实验门禁状态 |
| `archive/` | 被重大调整替代的旧计划/控制文档 |

- **权威位置**：长期设计 `docs/`；正式实验 `experiments/`；数据 `data/`（`raw/` 只读）；论文论点 `paper/`；输出 `outputs/`；临时分析 `.scratch/`。
- **预算（硬上限）**：`PROJECT.md` ≤ 6KB、`STATE.md` ≤ 8KB、`PLAN.md` ≤ 6KB、`HANDOFF.md` ≤ 4KB；启动包（AGENTS + PROJECT + STATE + PLAN + HANDOFF）≤ 20KB。
  超限即压缩：先整包快照到 `.project/archive/YYYY-MM-DD_pre_compact/`，再重写为当前状态；压缩后必须复测。
- **控制面唯一**：`.project/` 存在时，根目录不得再有 `PROJECT/STATE/PLAN/DECISIONS/HANDOFF.md`；不得创建 `plan_v2.md`、`summary_final.md`、`analysis_new.md` 等平行 canonical；迁移后旧副本移入 `.project/archive/YYYY-MM-DD_legacy_root/`。
- **单副本**：一个项目只保留一个工作副本；发现多副本先报告，确认权威副本后其余归档，不静默删除。
- **启动读取**：必读 `HANDOFF.md` + `STATE.md`；`PLAN.md` 在改动计划前读；`DECISIONS.md` 通过索引按需读。完整读取顺序、token 预算与估算方法见 `agent-workflow-optimizer` skill。
- **DECISIONS**：追加不删；超过 40KB 或 40 条时改为"索引 + 按月分册"（`DECISIONS.md` 只留 日期｜ID｜一句话｜分片链接，正文进 `decisions/YYYY-MM.md`）。
- **控制面缺失**：先报告并请求初始化，不静默创建。旧状态文件（`PROJECT_STATE.md` 等）仅作 legacy 只读，迁移后不双写。
- **放置与冗余**：根目录白名单、交付物归属表、备份/临时文件保留策略见 `agent-workflow-optimizer` skill；交付前用 adapter 安装的 `project_audit.py` 做只读审计。

## HANDOFF 更新规则

每次交还控制权前覆盖更新 `HANDOFF.md`（仅保留恢复所需最小状态）。固定小节：

```text
Goal / Done / Verified / (Rejected) / Open / Active / Next
```

- 启动长时间/远程/高风险操作前：写 `in_progress`、环境/路径、预期结果。
- 完成/失败/中断/待验证后：立即写实际结果、验证状态、下一步。
- 等待确认时：写 `waiting_confirmation` / `blocked` 及恢复条件。
- Done/Verified 已证伪的调查无新证据不得重跑；Rejected 仅在确有失败路径时填。
- 只保留一份最新快照；不追加日期流水账、`NEW` 或多份“最新恢复点”。

## 协作与审查协议

- 协调者只派发结构化任务包：

```text
TASK  { TASK_ID, Goal, Scope, Inputs, Allowed, Forbidden, Procedure?,
        Expected output, Acceptance criteria }
```

- 只接受 `RESULT` / `REVIEW` / `ESCALATION` 回复；大日志先压缩再整合。
- 角色职责：侦察只读定位与 file/line 证据；执行只做边界内小修改与聚焦测试；审计核对事实/配置/seed/metrics/artifacts；审查独立判断并加载 procedure；仲裁仅用于高值科学争议。
- **一个 review gate = 一次独立审查**；同一立场只启动一次，不做双重二次检查。审查路由表见 `code-reviewer` skill。

## 科学不变量

- 正式实验前：假设、变量、treatment/control、baseline、metrics、falsification 判据明确。
- 不得为改善结论静默改变 metric / baseline / filter / statistics / success criteria。
- 负结果是证据；不把失败假设包装为实现 bug。
- Claim 不超过 workload、baseline、不确定性、测试边界。
- 正式运行可追溯：experiment ID、commit、config、seed、workload version、env、命令、metrics、artifacts。

## Review 触发

- 非平凡代码变更；数据切分/预处理/metric/统计/baseline 变更；重要实验计划；正式结果；长项目交付前。
- 每个 gate 加载最相关的 procedure skill；同一立场只启动一次。

## 安全与升级

- 不主动读取/暴露 `.env`、凭据、token、cookie、私钥；日志/任务包/状态一律脱敏。
- 边界内普通本地实现：自主执行（继承已批准边界）。
- 必须单独确认：改 hypothesis/metrics/baseline/data-selection/统计/正式 claim；昂贵 full-scale run；跨项目/远程副作用；正式结果删除/覆盖。
- 不可逆/高破坏操作默认拒绝（强破坏删除、强制历史改写、递归强制删除等），除非用户明确改安全策略。
- 只读公开检索（网页/官方文档）无需审批。

## 程序索引（按需加载）

| 需要什么 | 加载 |
|---|---|
| 长任务协调；Project OS 放置/压缩/迁移/审计；上下文与日志过滤 | `agent-workflow-optimizer` |
| 代码审查；审查路由与升级判据 | `code-reviewer` |
| 实验设计、复核、预算、复现、证据整合、失败诊断、仓库结构 | 对应的 procedure skills |

Adapter 只负责装配本文件、提供执行器专属的角色/权限/插件；不得改变本文件的规则语义。
