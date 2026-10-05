---
name: agent-workflow-optimizer
description: Coordinate long-running or multi-agent work and maintain Project OS state through bounded delegation, context filtering, checkpoints, and focused verification. Use for multi-stage projects, large context, repeated failures, or Project OS state/plan/handoff maintenance and consolidation. Core rules define storage and growth budgets.
---

# Agent Workflow Optimizer

Use for long or multi-agent work and Project OS maintenance. Follow the installed Core rules for Project State, HANDOFF, and control-plane growth; project instructions and explicit user boundaries take precedence.

## Startup

1. Follow the Core Project OS read order and inspect relevant task evidence. Resolve conflicting progress/environment claims before rewriting state; a newer heading is not proof.
2. If the control plane is absent, report it and request initialization when needed. Reuse legacy state as read-only context; do not create a competing state schema.
3. Establish a concise boundary: goal, environment, allowed scope, forbidden actions, acceptance criteria, escalation conditions.
4. Split work by evidence boundary, not arbitrary file count. Prefer parallel read-only discovery when independent questions and delegation permission allow it.

## Delegation protocol

Send structured `TASK` packets with ID, goal, inputs, scope, allowed/forbidden actions, optional procedure Skill, expected output, and acceptance criteria. Accept `RESULT`, `REVIEW`, or `ESCALATION` packets.

Use a read-only agent as a context filter for large logs, directories, and repetitive evidence. Pass paths, line numbers, run IDs, observed facts, uncertainty, and minimum excerpts rather than full raw output.

Keep the coordinator responsible for ordering, integration, decisions, and acceptance. Subagents do not start further delegation unless explicitly permitted.

## Control-plane maintenance

1. Locate current sections, still-effective constraints, authorization boundaries, retractions, pending verification, and blockers before selecting excerpts or proposing consolidation. Read more evidence when needed to resolve ambiguity.
2. Measure the startup bundle using the method and advisory budgets in Core rules. Report excess and justified exceptions; budget targets do not authorize content removal.
3. Within the approved boundary, update stable current sections and reference existing durable records. Preserve append-only decisions and the gate's reader/schema contract; seek the required authorization before archival, migration, or formal-result replacement.
4. Verify changed STATE/PLAN/HANDOFF for agreement, one current recovery snapshot, evidence paths, budget excess, and recoverability of the next action and acceptance condition. Existing structural checkers can assist but do not establish semantic consistency. Preserve full gate parsing and validation when filtering model-facing context.

## Checkpoints

Project OS defines persistence and the regular HANDOFF cadence. This Skill adds immediate checkpoints after a material stage, before/after costly or irreversible work, and after failure/interruption, within the task's authorization boundary.

Update the existing HANDOFF snapshot under Core rules. With no state change, refresh only necessary current metadata and next action. Reference durable evidence instead of copying full logs or prior snapshots.
