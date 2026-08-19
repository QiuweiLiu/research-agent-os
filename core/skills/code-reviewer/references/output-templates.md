# Output Templates

## Standard Review

```markdown
**Findings**
[P1] Title
[/absolute/path/file.ext:123](/absolute/path/file.ext:123)
Concrete failure mode, trigger, impact, and expected fix direction.

**Open Questions**
- Question or assumption, if any.

**Verification**
- `command`: result
- Not run: reason

**Summary**
One or two sentences only.
```

## No Findings

```markdown
No blocking issues found in the reviewed scope.

Verification:
- `command`: result

Residual risk:
- Areas not exercised or assumptions that still matter.
```

## Remote Audit Snapshot

```markdown
**Scope**
- Host:
- Project root:
- Branch / commit:
- Review target:

**Findings**
...

**Verification**
...

**Next Checks**
- Short list of high-value follow-up commands or files.
```

## Inline Comment Directive

When the environment supports inline comments and the user asks for review comments, emit tight comments:

```text
::code-comment{title="[P1] Wrong threshold source" body="This selects the threshold on test labels, so the reported F1 is optimistic and will not reproduce in production. Use a validation split or normal holdout calibration instead." file="/abs/path/eval.py" start=87 end=91 priority=1}
```
