---
name: evidence-synthesizer
description: Convert auditable research results into bounded claims by linking claims to evidence, experiments, raw artifacts, figures, and tables while preserving workload, baseline, uncertainty, denominator, and failure boundaries. Use for reports, papers, result summaries, and experiment handoffs.
---

# Evidence Synthesizer

Build an explicit chain:

```text
CLAIM -> EVIDENCE -> EXPERIMENT -> FIGURE/TABLE -> RAW ARTIFACT
```

## Synthesis rules

For each claim, list experiment IDs, workload/load cells, baselines, seeds, metric definition, denominator, uncertainty, and artifact paths. State what is supported, what is not supported, and the boundary where the result changes or is unknown.

Use the project's formal metric and aggregation rules. Report negative, missing, and anomalous runs rather than silently excluding them. Distinguish measured values from inference and from proposed future work.

Reject wording that exceeds evidence, such as "consistently outperforms all baselines," when only a subset of workloads or conditions was tested. If the evidence chain cannot be reconstructed from the ledger and artifacts, report the gap instead of filling it from memory.

---
