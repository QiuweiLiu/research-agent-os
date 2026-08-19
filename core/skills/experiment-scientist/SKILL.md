---
name: experiment-scientist
description: Design or revise research experiments before implementation or execution by making hypotheses, variables, controls, baselines, metrics, expected outcomes, falsification criteria, and confounders explicit. Use for experiment plans, ablations, hypothesis changes, and formal runs.
---

# Experiment Scientist

Use before a formal experiment, ablation, hypothesis revision, or causal interpretation. Inspect the project's existing definitions first; do not invent project metrics or baselines.

## Required experiment specification

Record:

```text
Hypothesis:
Independent variable:
Dependent variable(s):
Control variables:
Treatment:
Control / baseline:
Optional upper bound or oracle:
Expected outcome:
Falsification criterion:
Potential confounders:
Data / workload scope:
Seeds / repetitions:
Analysis plan:
```

Use the repository, paper, and existing ledger to fill each field. Mark unknowns explicitly. Keep data/workload identity, hardware, software, commit, config, seeds, objective, and data version fixed unless the variable is intentionally being studied.

## Decision rules

- Separate implementation verification from hypothesis testing.
- Include a negative control or oracle when it is needed to distinguish mechanism from correlation.
- Do not call a negative result a bug without passing failure triage.
- Do not change metrics, filters, baselines, or success criteria after seeing results without recording an approved decision and its reason.
- Stop before execution if the control, denominator, independent unit, or falsification criterion is undefined.

Return a compact design, unresolved questions, required evidence, and the next review gate. Once the design is stable, request an independent `reviewer` task using the `experiment-reviewer` procedure for a falsification pass.

---
