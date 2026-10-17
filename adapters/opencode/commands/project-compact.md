---
description: Project OS compaction — snapshot, rewrite STATE/PLAN/HANDOFF to budget, re-audit
---
按 `agent-workflow-optimizer` skill 的 "Project OS hygiene → Compact" 流程压缩指定项目。$ARGUMENTS

硬性顺序：
1. 先整包快照控制面到 `.project/archive/YYYY-MM-DD_pre_compact/`（不覆盖已有目录）
2. 重写 STATE/PLAN/HANDOFF 为当前状态（预算 8/6/4 KB），历史只留引用
3. 更新 `.project/archive/README.md` 索引
4. 复跑 `python3 ~/.config/opencode/scripts/project_audit.py <project>` 并报告残留

压缩前先展示将删除/改写的段落摘要，等用户确认后再写。
