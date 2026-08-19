---
name: code-reviewer
description: Review codebases, diffs, pull requests, experiment pipelines, scripts, and configuration changes for correctness, regressions, security, maintainability, architecture fit, test gaps, and reproducibility. Use when the user asks for code review, audit, bug/risk analysis, PR review, refactor review, security review, or wants a project checked before running or merging.
---

# Code Reviewer

This is a **review procedure Skill**, normally executed by the `reviewer` Agent or used when the user explicitly requests a direct review. Loading this Skill does not create an additional mandatory review pass.

## Review Stance

Start from evidence. Read the relevant files, call graph, tests, configs, and recent diffs before judging. Do not guess interfaces or invent missing business rules.

Lead with findings, ordered by severity. Focus on defects, behavioral regressions, security risks, data leakage, missing validation, and architecture mismatches. Keep style nits out unless they hide a real maintenance risk.

Do not modify code during a review unless the user explicitly asks for fixes after the review. If the user asks for both review and fix, review first, then make a concise fix plan before editing.

## Workflow

1. Identify the review target:
   - For a diff/PR:inspect changed files and nearby unchanged code.
   - For a repo audit:map entry points, build/test commands, configs, data paths, and generated artifacts.
   - For ML/data code:trace train/validation/test splits, metric calculation, randomness, caching, and output writing.
2. Gather context with fast local tools:
   - Use `git status`, `git diff`, `git log`, `rg`, `rg --files`, and targeted file reads.
   - Read tests and fixtures related to changed behavior.
   - Prefer primary project docs over assumptions.
3. Check the highest-risk dimensions:
   - Correctness and edge cases.
   - Security and secrets handling.
   - Data integrity, data leakage, and reproducibility.
   - API contracts, backward compatibility, and migrations.
   - Error handling, resource cleanup, concurrency, and idempotency.
   - Test coverage and whether tests would fail before the fix.
   - Fit with existing architecture and conventions.
4. Verify without violating reviewer read-only boundaries:
   - Inspect existing test/static-check evidence when available.
   - If fresh execution is needed, specify the **smallest exact test or static check** to the lead; the lead may delegate it to `runner` and return the observed result.
   - If execution is unavailable or expensive, state the exact check not run and the residual risk.
5. Report clearly:
   - Findings first, with severity and file/line references.
   - Then open questions or assumptions.
   - Then verification performed.
   - Then a brief summary.

## Severity

按对结论有效性的影响分级(与全局审查门禁一致):

- **P0**:改变主结论或阻断发布——数据泄漏、错误统计检验影响结论、安全漏洞、数据丢失、生产中断、损坏的已发布结果。
- **P1**:影响结果可信度但结论方向可能不变——未校正多重比较、样本量不足、用户可见 bug、错误指标/结果、主流程破坏、严重回归、远程-本地一致性。
- **P2**:建议——边界 bug、可维护性风险、缺失重要测试、低影响清理。

## Finding Format

使用与全局审查门禁一致的形状:

```text
[P0-01] 严重:简短标题 | 位置:文件路径:行号
```

规则:

- 每条问题一行,ID 连续编号(P0-01、P1-02…),严重度前缀 + 中文标签(严重/应改/建议)
- 位置必须精确到文件:行(无法定位行时写文件路径)
- 标题后另起一段解释具体失败模式、影响和触发条件
- 末尾给总结:共 N 个问题,P0 x 个、P1 y 个
- Describe the observable failure, not just the code smell.
- Include a minimal reproduction or scenario when useful.
- Avoid vague phrases like "might be bad"; name the risk.
- If no issues are found, say so and list remaining test gaps.

## Review Checklists

Load `references/checklists.md` when the target is broad, security-sensitive, ML/data-heavy, or when you need a structured pass.

Use `references/output-templates.md` when preparing a formal review report, PR comment batch, or executive-friendly audit summary.

## Special Cases

For remote SSH work, first confirm the target directory, then perform a read-only scan unless the user explicitly asks for edits. Avoid leaving long-running processes unless the user requested it or a `tmux` workflow is agreed.

For generated reports, notebooks, or experiment results, review both code and artifacts. Check whether reported numbers are traceable to scripts, inputs, seeds, and saved outputs.

For security review, look for secrets, auth bypass, injection, unsafe deserialization, path traversal, insecure file permissions, and dependency or container exposure. Do not exploit systems; demonstrate risk with safe reasoning or local minimal examples.

---
