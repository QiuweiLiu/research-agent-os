---
name: repo-architecture
description: Inspect repository architecture before changing core code by tracing entrypoints, call graphs, data flow, module responsibilities, interfaces, invariants, and existing abstractions. Use for cross-module changes, task or prediction logic, data pipelines, refactors, and unfamiliar repositories.
---

# Repository Architecture

Understand the smallest coherent path before editing. Start from real entrypoints, tests, configs, and call sites rather than a desired architecture.

## Pre-edit inspection

Identify:

- entrypoints and command paths;
- call graph and data flow;
- module responsibilities and public interfaces;
- invariants, serialization, shape, time, seed, and version contracts;
- existing helpers, adapters, baseline implementations, and test seams;
- configuration ownership and protected scientific definitions.

## Change rules

- Reuse an existing abstraction before creating a parallel helper.
- Keep one production path and one source of truth.
- Prefer a minimal coherent change over scattered patches or benchmark-specific hacks.
- Do not change metrics, baselines, data semantics, or external interfaces implicitly.
- Add or update the narrowest test that can fail before the fix.

Return an architecture map, affected files and callers, invariants, proposed change boundary, and verification plan. Escalate if the requested change crosses module ownership or protected scientific logic.

---
