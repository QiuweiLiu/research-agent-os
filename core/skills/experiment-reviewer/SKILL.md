---
name: experiment-reviewer
description: Falsify research experiment designs and interpretations by checking leakage, unfair baselines, confounders, compute inequality, workload bias, metric bias, statistical uncertainty, and claims that exceed evidence. Use after an important experiment plan or result.
---

# Experiment Reviewer

This is an **experiment-review procedure Skill**, normally executed by the `reviewer` Agent. Do not run a duplicate second pass if the same reviewer task is already using this procedure.

Act as a falsifier, not a co-author trying to make the result look better. Read the actual design, configs, raw summaries, and project definitions.

## Review checklist

- Is the hypothesis stated before the result and is the independent unit clear?
- Is treatment compared with a fair control and, where needed, a negative control or oracle?
- Could future information, preprocessing, caching, trace reuse, or workload construction leak the answer?
- Are data, workload, hardware, seeds, model checkpoints, scheduler objective, and compute budget comparable?
- Are all relevant workloads, loads, heterogeneity levels, and failure cases represented rather than cherry-picked?
- Are denominator, uncertainty, effect size, confidence interval, and multiple-comparison choices visible?
- Does the proposed claim stay within the tested boundary?

## Mandatory data/statistics invariants

The following items are **mandatory** when the reviewed object involves data splitting, preprocessing, metrics, baselines, or statistical testing. Missing any of these is a blocking finding (P0/P1), not a style suggestion.

### Data split and temporal isolation

- Training/validation/test splits are time- or group-isolated (date-blocked / chronicle); no future information leaks into any earlier stage.
- The **primary metric is reported date-blocked** (or per-group), never only as a pooled aggregate.
- **Pooled metrics must not be the sole main conclusion**; they must be presented alongside group/date-blocked metrics.

### Feature leakage

- No feature contains target information.
- Normalization/preprocessing is fitted **only inside the training fold** (no pipeline leakage).
- Provenance / identifier fields (paths, IDs, timestamps) are not mixed into model inputs.
- Trace reuse, caching, and workload construction do not leak the answer.

### Statistical rigor

- Multiple-comparison corrections applied when relevant.
- Effect size / confidence interval reported alongside point estimates.
- Independent repetition unit is clear; random seeds recorded.
- Conclusion is supported by the data; no self-deception (e.g., pooled metric hiding date leakage).

### Reproducibility

- Seeds, dependency/weight versions, and data snapshot are recorded and traceable.

## Output

```text
REVIEW
Verdict: PASS / CONDITIONAL PASS / REJECT
Main concern:
Evidence required:
Supported claim:
Unsupported claim:
Confounders / alternative explanations:
```

Do not silently repair the design or rewrite a negative result. Escalate hypothesis changes and high-cost decisions to `research-reviewer`.

---
