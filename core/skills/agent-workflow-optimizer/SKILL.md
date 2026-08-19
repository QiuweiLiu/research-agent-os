---
name: agent-workflow-optimizer
description: Coordinate long-running multi-agent research work with bounded delegation, context filtering, checkpoints, and explicit verification. Use for multi-stage projects, repeated failures, large context, or tasks involving several agents. Project state storage always follows Project OS; this Skill must not create a competing state schema.
---

# Agent Workflow Optimizer

Use this Skill only for long or multi-agent work. Do not load it for a simple one-step answer.

## Startup

1. If `.project/` exists, read `.project/STATE.md`, `.project/PLAN.md`, and `.project/HANDOFF.md` as the authoritative continuation state.
2. If `.project/` does not exist, reuse the repository's existing legacy state file if present; do not create a parallel state system.
3. Establish a concise boundary in working context:goal, environment, allowed scope, forbidden actions, acceptance criteria, escalation conditions.
4. Split work by evidence boundary, not arbitrary file count. Prefer parallel read-only discovery when questions are independent.

## Delegation protocol

Send only structured `TASK` packets with ID, goal, inputs, scope, allowed/forbidden actions, optional procedure Skill, expected output, and acceptance criteria. Accept only `RESULT`, `REVIEW`, or `ESCALATION` packets.

Use a cheap/read-only agent as a context filter for large logs, directories, and repetitive evidence. Pass the lead paths, line numbers, run IDs, observed facts, uncertainty, and the minimum required excerpts—not raw output by default.

Keep the coordinator responsible for ordering, integration, final decisions, and user-facing claims. Subagents do not start further delegation unless explicitly permitted.

## Checkpoints

Project OS defines what is persisted and where. This Skill only decides when an **extra immediate checkpoint** is useful:after a material stage, before/after costly or irreversible work, after a failure, or before handing control away.

At a checkpoint, update the existing `.project/HANDOFF.md` under the global HANDOFF rules. Do not invent another checkpoint file or duplicate full logs.
