---
name: reproducibility
description: Make formal research runs traceable and replayable by checking experiment IDs, commits, configs, seeds, workloads, checkpoints, hardware/software environments, commands, metrics, artifacts, and status. Use when registering, completing, comparing, or handing off experiments.
---

# Reproducibility

Treat a formal experiment as existing only when the project's ledger contains a traceable record. Reuse the project's existing ledger and schema; do not create a competing schema from this Skill.

## Minimum fields to verify

Check that the project record can identify:

```text
experiment_id
timestamp
git commit
config path and immutable identity
seed / repetitions
dataset or workload version
model checkpoint
GPU hardware
software environment
command
metrics and aggregation
artifact paths
status and anomalies
```

Before a run, register the planned identity and output location when the project workflow requires it. After a run, verify process status, parsed metrics, saved config, commit, seed, artifacts, and anomaly markers. Do not equate exit code 0 with scientific success.

At handoff, link each result to its raw artifacts and ledger record. Redact credentials and avoid copying large logs into persistent state.

---
