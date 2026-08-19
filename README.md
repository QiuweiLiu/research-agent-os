# Research Agent OS

A small, generic, self-contained, installable **Research Agent OS Core** for long-running
AI-assisted research and engineering — distilled from a personal harness, published without
any private configuration.

The Core is **harness-agnostic**: the rules, skills, and project state schema stay useful if
you change domain, change models, or switch to another agent harness.

> License: **MIT** — see [LICENSE](LICENSE).

## What you get

```
research-agent-os/
├── core/                     # harness-agnostic (no OpenCode/OpenAI terms inside)
│   ├── policies/CORE.md      # single rule source: workflow, delegation, HANDOFF,
│   │                         #   scientific invariants, review gates, escalation
│   ├── project/              # Project OS templates: 6 control files + archive/
│   └── skills/               # 9 procedure skills
├── adapters/
│   └── opencode/             # OpenCode implementation: agents(5), plugins(2),
│   │                         #   Trusted Mode permissions, AGENTS.md assembly
├── scripts/                  # install.sh · doctor.py · init-project.py
├── examples/                 # (how to bootstrap your first project)
└── docs/                     # classification, model choice
```

### Core Skills (9)

agent-workflow-optimizer · experiment-scientist · experiment-reviewer · compute-budget ·
reproducibility · evidence-synthesizer · failure-triage · code-reviewer · repo-architecture

### Core Roles (5) — duties only, no model binding

`research-lead` (coordinator) · `scout` (read-only recon) · `runner` (bounded executor) ·
`reviewer` (independent review) · `auditor` (factual verification)

You choose the model; subagents inherit the primary model and can be overridden or disabled
per role (see `adapters/opencode/README.md`).

### Core runtime

- **continuity** — injects `.project/HANDOFF.md` into every context compaction
- **research-guard** — blocks destructive/secret-exposing actions; gates formal experiments
  on `EXPERIMENT_GATE.json` (`smoke_passed` / `ledger_registered` / `commit`)
- **Trusted Mode** — auto-allow ordinary workspace work; explicitly deny `sudo`,
  `rm -rf`, `git reset --hard`, `git clean`, force-push, env dumps, and key-file access

## Quick Start

```bash
git clone <this-repo> research-agent-os
cd research-agent-os
./scripts/install.sh              # installs the OpenCode adapter (idempotent; --dry-run to preview)
python3 scripts/doctor.py         # READY / READY WITH WARNINGS / NOT READY
python3 scripts/init-project.py --dir ~/my-research   # bootstrap a Project OS control plane
opencode                          # start with research-lead as your default agent
```

Documents:
- [adapters/opencode/README.md](adapters/opencode/README.md) — adapter details, model choice, disabling roles
- [docs/classification.md](docs/classification.md) — CORE / OPTIONAL / PRIVATE / DOMAIN / HARNESS matrix
- [core/policies/CORE.md](core/policies/CORE.md) — the actual ruleset (single source, harness-agnostic)

## Not included (deliberately)

code-minimalism (license-restricted), scheduling-experiment-design (GPU scheduler domain),
find-skills, knowledge-retrieval, paper-figure-generator, office-docs, ui-review, openai-docs,
vision, research-reviewer, image-server, and **all personal configuration** (providers,
SSH/MCP endpoints, key files, personal model choices, local paths). The complete personal
harness stays private — this repo is the distilled Core only.