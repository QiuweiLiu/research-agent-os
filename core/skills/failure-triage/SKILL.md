---
name: failure-triage
description: Diagnose failed, anomalous, or negative experiments with evidence-directed triage before changing code or rerunning jobs. Use for crashes, metric regressions, contradictory results, missing artifacts, unexpected reversals, and hypothesis-disconfirming outcomes.
---

# Failure Triage

Do not respond to an unattractive result by tuning until it looks better. Preserve the original run and diagnose the smallest plausible failure path first.

## Classification

Keep the existing classes:

```text
A Implementation failure
B Environment failure
C Configuration failure
D Experimental-design failure
E Hypothesis or algorithm limitation
```

## Evidence-directed workflow

1. State the **observed failure** precisely:what changed, where it appears, which run/artifact shows it, and what was expected.
2. From current evidence, select only the 1-2 most plausible classes. Do not mechanically inspect every class.
3. Choose the smallest check that can distinguish those classes.
4. Update the hypothesis after each check. Do not repeat the same search/check without new evidence.
5. Inspect environment/hardware/dependencies only when logs, reproduction differences, recent environment changes, missing checkpoints, or remote/local mismatch make class B plausible.
6. Inspect config/commit/seed/data/metric only when evidence makes class C or data-path inconsistency plausible.
7. Inspect implementation against intended design when class A remains plausible; use `repo-architecture` only if the relevant path crosses modules or core logic.
8. If implementation, environment, configuration, metric parsing, and experiment design are sufficiently supported as sound, preserve the negative result and classify it as a possible hypothesis/algorithm limitation instead of forcing a code fix.

Return:

```text
Observed failure:
Primary class:
Evidence:
Ruled-out classes:
Remaining uncertainty:
Smallest next check:
Rerun needed: yes/no + what would change
```

Never delete or overwrite the original result. A rerun must state what changed and why.
