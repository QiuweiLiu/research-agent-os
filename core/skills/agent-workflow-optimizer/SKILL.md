---
name: agent-workflow-optimizer
description: Coordinate long-running or multi-agent work and keep Project OS healthy — bounded delegation, context filtering, control-plane budgets, placement rules, audit/compaction/migration, and checkpoints. Use for multi-stage projects, large or growing context, repeated failures, new projects, or whenever Project OS state/plan/handoff needs maintenance or consolidation.
---

# Agent Workflow Optimizer

Use for long or multi-agent work and for Project OS hygiene. Follow the global CORE rules; project instructions and explicit user boundaries take precedence. This Skill provides the **procedures** behind the CORE budgets and placement rules.

## Startup

1. Required startup bundle: `.project/PROJECT.md` + `.project/HANDOFF.md` + `.project/STATE.md`. Read `.project/PLAN.md` before changing plans; consult `.project/DECISIONS.md` through its index.
2. Budget for the startup bundle (~6k tokens total): project `AGENTS.md` 800, `PROJECT.md` 1000, `STATE.md` 1500, `PLAN.md` 1500, `HANDOFF.md` 700. Prefer a local tokenizer; otherwise label UTF-8 bytes / 4 as a rough estimate. Exceeding a budget needs justification, not truncation.
3. The old "read all five files in full" habit is intentionally retired: it is what makes context grow. Read deeper only when the task needs it.
4. Resolve conflicting progress/environment claims before rewriting state; a newer heading is not proof.
5. If `.project/` is missing, report and request initialization; if it exists but is empty, treat it as **not initialized**. Reuse legacy state as read-only (`PROJECT_STATE.md`, `OPEN_QUESTIONS.md`, `EXPERIMENT_LEDGER.jsonl`); do not create a competing schema.
6. Establish a concise boundary: goal, environment, allowed scope, forbidden actions, acceptance criteria, escalation conditions.
7. Split work by evidence boundary, not arbitrary file count; prefer parallel read-only discovery when questions are independent and delegation permission allows it.

## Placement: root whitelist and artifact ownership

Project root may contain only:

```text
AGENTS.md  README*  LICENSE  .gitignore  .project/  docs/  experiments/
data/  paper/  outputs/  .scratch/  src|scripts|tests|config/  build manifests
```

Everything else must be placed or archived:

| Artifact | Destination |
|---|---|
| Reports / slides / PDFs (`.docx/.pptx/.pdf/.xlsx`) | `docs/reports/` |
| Figures | `outputs/figures/` (paper figures → `paper/figures/`) |
| Recordings / audio | `data/raw/audio/` |
| Datasets | `data/raw/` (read-only) or `data/processed/` |
| Model weights | `data/models/` (gitignored) or an external cache |
| One-off scripts | `scripts/` or `experiments/<id>/code/` |
| Logs | `experiments/<id>/logs/` or `outputs/logs/` |
| Backups (`.bak/.old/副本`) | `.scratch/backups/` with 30-day TTL |
| Archives (`.zip`) | `.scratch/archives/` (or `outputs/` if a deliverable) |

When a new artifact type appears, extend this table instead of dropping the file at the project root.

## Growth budgets and retention

- `PROJECT.md` ≤ 6KB · `STATE.md` ≤ 8KB · `PLAN.md` ≤ 6KB · `HANDOFF.md` ≤ 4KB.
- Startup bundle (AGENTS + PROJECT + STATE + PLAN + HANDOFF) ≤ 20KB.
- `STATE.md` holds current stage, verified facts with evidence pointers, open problems, risks, retractions, pending verification. No dated history.
- `PLAN.md` holds the current objective, executable steps, dependencies, acceptance criteria. No completed-step log.
- `HANDOFF.md` holds exactly one recovery snapshot in the fixed sections. No date-stamped append log, no `NEW` markers.
- `DECISIONS.md` is append-only; mark superseded decisions and link the replacement instead of deleting them. Keep each entry ~100–200 tokens: choice, reason, impact, status, evidence link. No daily progress, full reviews, or reports.
- Above ~40KB or ~40 entries, split into an index (`DECISIONS.md`: date | id | one-line | shard link) plus `decisions/YYYY-MM.md`, and read the index by default.
- Numeric facts live in the experiment's `metrics.csv/json`; interpretation lives in `RESULT.md`. Control files reference paths instead of copying values.
- `EXPERIMENT_GATE.json` holds only execution-check state and evidence references. Migrating existing fields requires checking every reader, explicit migration authorization, and contract verification; never change gate behavior merely to shrink the file.
- Keep one stable working copy per deliverable. Archive only on a real stage/route change or an approved cleanup — not every turn. Keep still-valid constraints, retractions, and unresolved items in the current file.
- Numeric facts live in experiment `metrics` files; control files reference paths instead of copying tables.
- Never create per-turn backups or duplicate summaries; archive only on a real stage/route change or an approved cleanup.

## Audit (read-only)

```sh
# repo checkout:   python3 scripts/project_audit.py <project-root>
# installed copy:  python3 <config-dir>/scripts/project_audit.py <project-root>
# workspace scan:  add --discover <dir>
```

Interpretation:

- **FAIL** — broken hard rules: missing/empty control plane, root control-file copies, sizes ≥ 2× budget, startup bundle > 40KB.
- **WARN** — drift: over budget, misplaced root entries, parallel canonical candidates, backup/scratch/output growth, empty archive while over budget, legacy state files, duplicate project titles.
- Do not modify anything during the audit pass. Report faithfully.

## Compact (only when a budget is exceeded or STATE/HANDOFF reads like a log)

1. Snapshot **all** control files to `.project/archive/YYYY-MM-DD_pre_compact/`.
2. Rewrite `STATE.md` to current stage + verified facts + open problems + risks (≤ 8KB).
3. Rewrite `PLAN.md` to current objective/steps/acceptance/blockers (≤ 6KB).
4. Rewrite `HANDOFF.md` to one snapshot with the fixed sections (≤ 4KB).
5. Move durable history into `experiments/<id>/` or `docs/` by reference; append decisions to the index/shards instead of inlining.
6. Update `.project/archive/README.md`.
7. Re-run the audit and report remaining excess with justification.

Compaction requires the normal authorization boundary; never silently delete evidence.

## Migrate (duplicate control planes, legacy files, duplicate copies)

- Root copies of `PROJECT/STATE/PLAN/DECISIONS/HANDOFF` while `.project/` exists: report timestamps, confirm the authoritative copy, then move the root copies to `.project/archive/YYYY-MM-DD_legacy_root/`.
- Empty `.project/`: ask before creating content.
- Multiple worktrees of the same project (same title or git remote): list all copies with mtimes; archive stale copies only after explicit confirmation; never delete silently.
- `PROJECT_STATE.md` and other legacy files: read-only reference; archive when the migration closes.

## Delegation protocol

Send structured `TASK` packets with ID, goal, inputs, scope, allowed/forbidden actions, optional procedure Skill, expected output, and acceptance criteria. Accept `RESULT`, `REVIEW`, or `ESCALATION` packets.

Use a read-only agent as a context filter for large logs, directories, and repetitive evidence. Pass paths, line numbers, run IDs, observed facts, uncertainty, and minimum excerpts rather than full raw output.

Keep the coordinator responsible for ordering, integration, decisions, and acceptance. Subagents do not start further delegation unless explicitly permitted.

## Control-plane maintenance

1. Locate current sections, still-effective constraints, authorization boundaries, retractions, pending verification, and blockers before selecting excerpts or proposing consolidation. Read more evidence when needed to resolve ambiguity.
2. Measure the startup bundle; report excess and justified exceptions. Budget targets do not authorize content removal.
3. Within the approved boundary, update stable current sections and reference existing durable records. Preserve append-only decisions and the gate's reader/schema contract; seek the required authorization before archival, migration, or formal-result replacement.
4. Verify changed STATE/PLAN/HANDOFF for agreement, one current recovery snapshot, evidence paths, budget excess, and recoverability of the next action and acceptance condition. Structural checks do not establish semantic consistency. Preserve full gate parsing and validation when filtering model-facing context.

## Delivery check (before handing control back)

- Check that this turn's changes agree across STATE, PLAN, and HANDOFF; there is exactly one current snapshot; evidence paths still resolve; no budget overrun is left unexplained.
- Verify conflicts and current evidence before compacting a long file; a newer mtime is not proof of correctness.
- When a file is over budget, first locate current state, authorizations, valid constraints, retractions, pending verification, blockers, and the recovery path. Trim only inside the write/archive authorization; otherwise report concrete candidates.
- After compaction, confirm those items and the next acceptance condition are still recoverable. A structural check does not prove semantic consistency or that all history was reviewed.

## Checkpoints

Project OS defines persistence and the regular HANDOFF cadence. This Skill adds immediate checkpoints after a material stage, before/after costly or irreversible work, and after failure/interruption, within the task's authorization boundary.

Update the existing HANDOFF snapshot under the CORE rules. With no state change, refresh only necessary current metadata and next action. Reference durable evidence instead of copying full logs or prior snapshots.
