---
name: compute-budget
description: Gate costly research computation with static checks, unit tests, tiny smoke tests, small-scale runs, known GPU cost, trace reuse, seed selection, parallelism, and explicit approval thresholds. Use before full-scale GPU or long remote experiments.
---

# Compute Budget

Use a staged gate. Thresholds come from the project or user; do not invent a universal GPU-hour limit.

```text
static check -> unit test -> tiny smoke -> small run -> full run
```

## Full-run checklist

Before launch, verify:

- hypothesis, matrix, config, commit, metric, and baseline are fixed;
- smoke and small-scale checks passed;
- expected GPU-hours, wall time, and output path are known;
- an equivalent existing experiment or reusable trace has been checked;
- required seeds and parallelization are justified;
- the project's ledger/gate entry exists;
- any project or user approval threshold is satisfied.

If a check is missing, stop at the smallest safe stage and return the missing evidence. Never use a cheaper run as silent evidence for a full-scale claim.

---
