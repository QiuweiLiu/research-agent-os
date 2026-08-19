# Code Review Checklists

Use only the sections that match the target. Do not turn the checklist into a long report; use it to find high-signal issues.

## Correctness

- Does the code implement the intended behavior under normal and boundary inputs?
- Are units, shapes, tensor dimensions, time zones, path conventions, and encodings consistent?
- Are errors handled where callers can recover or where failure should be explicit?
- Are defaults safe, documented, and compatible with existing behavior?
- Are migrations, schema changes, config changes, or CLI argument changes backward-compatible?

## Tests And Verification

- Is there a test that fails on the bug or regression being reviewed?
- Do tests cover edge cases, error paths, and representative real inputs?
- Are mocks faithful enough to catch integration issues?
- Are expensive tests separated from fast checks?
- Did the reviewer run the smallest relevant command? If not, is the gap stated?

## Security

Inspired by OWASP-style review passes:

- Secrets: hard-coded tokens, passwords, private keys, credentials in logs or artifacts.
- Authentication and authorization: bypasses, missing ownership checks, confused roles.
- Input handling: injection, path traversal, unsafe shell construction, unsafe template rendering.
- File and network: uncontrolled downloads/uploads, SSRF, unsafe permissions, symlink issues.
- Serialization: unsafe pickle/yaml loading, arbitrary code execution, untrusted archive extraction.
- Crypto: custom crypto, weak randomness, missing TLS verification.
- Dependencies and containers: unpinned risky dependencies, root execution where avoidable, exposed ports.

## Data, ML, And Experiment Pipelines

- Train/validation/test leakage, especially shared cycles, dates, subjects, devices, or cached transforms.
- Metric bugs: wrong denominator, threshold selected on test data, averaging hides failed days/classes.
- Randomness: missing seed control, unstable split generation, repeat aggregation not reported.
- Artifacts: outputs overwritten silently, figures not traceable to data/script/version.
- Baselines: compare against meaningful negative and simple baselines.
- Deployment: thresholds calibrated on normal holdout, false positive rate reported, drift monitored.

## Maintainability And Architecture

- Does the change reuse existing helpers and conventions?
- Is new abstraction justified by real duplication or complexity?
- Are ownership boundaries respected?
- Are names precise enough to prevent misuse?
- Is logging actionable without leaking sensitive data?
- Is resource cleanup explicit for files, sockets, GPUs, subprocesses, and temporary directories?

## Performance And Reliability

- Avoid accidental O(n^2), repeated I/O, full dataset loads, or GPU/CPU transfers in loops.
- Check timeout, retry, cancellation, and idempotency behavior.
- Check concurrent writes, race conditions, and partial-output cleanup.
- Confirm memory use for large arrays, videos, images, model checkpoints, and PDFs.

## Remote Server Review

- Capture `pwd`, project root, git status, active env, and relevant process list.
- Avoid destructive commands.
- Prefer read-only inspection first.
- Use `tmux` for long-running verification only after user approval.
- Summarize commands run and outputs that matter; do not paste secrets.

## Online Sources This Skill Was Modeled After

- Google Engineering Practices: Code Review Developer Guide, especially review standards and what to look for: https://google.github.io/eng-practices/
- OWASP Code Review Guide and Secure Coding Practices Checklist: https://owasp.org/www-project-code-review-guide/ and https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/
- GitHub Pull Request Review docs, especially line-specific comments and review outcomes: https://docs.github.com/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews
