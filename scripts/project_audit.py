#!/usr/bin/env python3
"""Project OS audit (read-only).

Checks layout, control-plane budgets, duplicate control planes, parallel
canonical files, backups, scratch/output growth, and archive usage.

Usage:
  python3 project_audit.py [PATH ...] [--discover DIR ...] [--json]

PATH may be a project root or its .project directory.
--discover scans each DIR (maxdepth 4) for .project control planes.
--json prints machine-readable results.

Exit codes: 0 clean, 1 warnings, 2 failures.
"""
from __future__ import annotations

import json
import os
import re
import sys

# ---------------------------------------------------------------- budgets (bytes)
BUDGETS = {
    "PROJECT.md": 6 * 1024,
    "STATE.md": 8 * 1024,
    "PLAN.md": 6 * 1024,
    "HANDOFF.md": 4 * 1024,
    "DECISIONS.md": 40 * 1024,
}
STARTUP_WARN = 20 * 1024
STARTUP_FAIL = 40 * 1024
CONTROL_FILES = ["PROJECT.md", "STATE.md", "PLAN.md", "DECISIONS.md", "HANDOFF.md"]

ALLOWED_ROOT = {
    "AGENTS.md", "README.md", "README", "LICENSE", "LICENSE.txt", "LICENSE.md",
    "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md",
    ".gitignore", ".gitattributes", ".editorconfig", ".project", ".scratch",
    ".github", ".vscode", ".idea", ".venv", "node_modules", "__pycache__",
    "docs", "experiments", "data", "paper", "outputs",
    "src", "scripts", "tests", "test", "config", "configs", "assets", "public",
    "notebooks", "web", "app", "api", "server", "client", "backend", "frontend",
    "dist", "build", "android", "ios", "evals", "proxy", "templates", "packages",
    "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "requirements.txt", "requirements-dev.txt", "pyproject.toml", "setup.py",
    "setup.cfg", "tox.ini", "package.json", "package-lock.json", "pnpm-lock.yaml",
    "yarn.lock", "tsconfig.json", "tsconfig.node.json", "vite.config.ts",
    "vite.config.js", "vitest.config.ts", "eslint.config.js", "playwright.config.ts",
    "capacitor.config.ts", "index.html", "Cargo.toml", "go.mod", "go.sum",
    "Gemfile", "Pipfile", "environment.yml", "uv.lock", "VERSION", "MANIFEST.in",
    "test-results", "coverage", "tsconfig.tsbuildinfo", ".turbo", ".next",
}
ALLOWED_ROOT_RE = re.compile(r"^(?:README|LICENSE|CHANGELOG|CONTRIBUTING|SECURITY)(?:\.[A-Za-z0-9_.-]+)?$")
DELIVERABLE_EXT = {
    ".pptx": "docs/reports/", ".docx": "docs/reports/", ".pdf": "docs/reports/",
    ".xlsx": "docs/reports/", ".csv": "data/processed/", ".png": "outputs/figures/",
    ".jpg": "outputs/figures/", ".jpeg": "outputs/figures/", ".svg": "outputs/figures/",
    ".m4a": "data/raw/audio/", ".mp3": "data/raw/audio/", ".wav": "data/raw/audio/",
    ".zip": ".scratch/archives/",
    ".pt": "data/models/", ".pth": "data/models/", ".onnx": "data/models/",
    ".safetensors": "data/models/", ".ckpt": "data/models/",
}
PARALLEL_RE = re.compile(r"(?i)^(plan_v\d+|summary_final|analysis_new|final_report|最终版|.*_副本|.*_final|.*_final_report)$")
BACKUP_RE = re.compile(r"(?i)(\.bak|\.old|\.orig|备份|副本|_final|\.pre-)")
SKIP_DIRS = {"node_modules", ".git", ".venv", "__pycache__", "dist", "build", ".next", "target", ".cache"}
MODEL_DIR_RE = re.compile(r"(?i)^(qwen|llama|mistral|gemma|.*checkpoint|.*weights|grounded-video-llm)")
HANDOFF_SECTIONS = [
    ("Goal", "目标"), ("Done", "已完成", "完成"), ("Verified", "已验证"),
    ("Open", "待解决", "未解决"), ("Next", "下一步"),
]


def read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def project_root(path: str) -> str | None:
    path = os.path.abspath(path)
    if os.path.basename(path) == ".project" and os.path.isdir(path):
        return os.path.dirname(path)
    if os.path.isdir(os.path.join(path, ".project")):
        return path
    return None


def discover(directory: str) -> list[str]:
    found = []
    base = os.path.abspath(directory)
    for dirpath, dirnames, _filenames in os.walk(base):
        depth = dirpath[len(base):].count(os.sep)
        if depth > 4:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if ".project" in dirnames:
            found.append(dirpath)
            dirnames.remove(".project")
    return found


def count_files(path: str, depth_limit: int = 6, prune_models: bool = True) -> tuple[int, int]:
    """Return (file_count, total_bytes) with bounded depth and pruning."""
    if not os.path.isdir(path):
        return 0, 0
    count = 0
    total = 0
    base = os.path.abspath(path)
    for dirpath, dirnames, filenames in os.walk(base):
        depth = dirpath[len(base):].count(os.sep)
        if depth >= depth_limit:
            dirnames[:] = []
        pruned = []
        for d in dirnames:
            if d in SKIP_DIRS:
                continue
            if prune_models and depth == 0 and MODEL_DIR_RE.match(d):
                continue
            pruned.append(d)
        dirnames[:] = pruned
        for name in filenames:
            try:
                total += os.path.getsize(os.path.join(dirpath, name))
            except OSError:
                pass
            count += 1
    return count, total


def human(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.1f}MB"
    if n >= 1024:
        return f"{n / 1024:.1f}KB"
    return f"{n}B"


def audit(root: str) -> tuple[list[tuple[str, str]], int]:
    results: list[tuple[str, str]] = []

    def add(level: str, message: str) -> None:
        results.append((level, message))

    control_dir = os.path.join(root, ".project")
    if not os.path.isdir(control_dir):
        add("FAIL", "missing .project/ control plane")
        return results, 2
    present = [f for f in CONTROL_FILES if os.path.isfile(os.path.join(control_dir, f))]
    if not present:
        add("FAIL", ".project/ exists but is empty (not initialized)")
    elif len(present) < len(CONTROL_FILES):
        missing = [f for f in CONTROL_FILES if f not in present]
        add("FAIL", f"control plane incomplete; missing {', '.join(missing)}")
    else:
        add("PASS", f"control plane complete ({len(present)}/{len(CONTROL_FILES)})")

    # ---- sizes / budgets
    startup_files = ["PROJECT.md", "STATE.md", "PLAN.md", "HANDOFF.md"]
    startup_total = 0
    agents_md = os.path.join(root, "AGENTS.md")
    if os.path.isfile(agents_md):
        startup_total += os.path.getsize(agents_md)
    for name in CONTROL_FILES:
        path = os.path.join(control_dir, name)
        if not os.path.isfile(path):
            continue
        size = os.path.getsize(path)
        if name in startup_files:
            startup_total += size
        budget = BUDGETS[name]
        if size > budget:
            add("WARN" if size <= budget * 2 else "FAIL",
                f"{name} {human(size)} exceeds budget {human(budget)}"
                + (" (2x+)" if size > budget * 2 else ""))
    if startup_total:
        level = "FAIL" if startup_total > STARTUP_FAIL else ("WARN" if startup_total > STARTUP_WARN else "PASS")
        add(level, f"startup read bundle {human(startup_total)} (warn>{human(STARTUP_WARN)}, fail>{human(STARTUP_FAIL)})")

    # ---- STATE log-style
    state = read_text(os.path.join(control_dir, "STATE.md"))
    if state:
        sections = re.findall(r"^##\s+(.*)$", state, re.M)
        dated = [s for s in sections if re.search(r"20\d{2}-\d{2}", s)]
        if len(dated) > 5:
            add("WARN", f"STATE has {len(dated)} dated sections (append-log style); compact to current state")
        elif len(sections) > 10:
            add("WARN", f"STATE has {len(sections)} sections; keep current state only")

    # ---- HANDOFF
    handoff = read_text(os.path.join(control_dir, "HANDOFF.md"))
    if handoff:
        stamps = re.findall(r"20\d{2}-\d{2}-\d{2}", handoff)
        if len(stamps) > 3:
            add("WARN", f"HANDOFF contains {len(stamps)} date stamps (should be one recovery snapshot, not a log)")
        missing = []
        for group in HANDOFF_SECTIONS:
            if not any(re.search(rf"^##\s*{re.escape(alias)}\b", handoff, re.M | re.I) for alias in group):
                missing.append(group[0])
        if missing:
            add("WARN", f"HANDOFF missing fixed sections: {', '.join(missing)}")

    # ---- DECISIONS
    decisions = os.path.join(control_dir, "DECISIONS.md")
    if os.path.isfile(decisions):
        text = read_text(decisions)
        entries = len(re.findall(r"^###\s+", text, re.M))
        size = os.path.getsize(decisions)
        if size > BUDGETS["DECISIONS.md"]:
            add("WARN", f"DECISIONS {human(size)} / {entries} entries; add an index and shard by month")
        if not os.path.isdir(os.path.join(control_dir, "decisions")) and entries > 40:
            add("WARN", "DECISIONS has no index/shards (consider DECISIONS.md index + decisions/YYYY-MM.md)")

    # ---- root whitelist + deliverables + duplicate control plane
    root_entries = sorted(os.listdir(root))
    unknown = []
    for name in root_entries:
        if name in ALLOWED_ROOT or ALLOWED_ROOT_RE.match(name):
            continue
        if name.startswith("."):
            continue
        unknown.append(name)
    if unknown:
        suggestions = []
        for name in unknown[:8]:
            ext = os.path.splitext(name)[1].lower()
            target = DELIVERABLE_EXT.get(ext)
            if target:
                suggestions.append(f"{name} -> {target}")
            elif os.path.isdir(os.path.join(root, name)) and MODEL_DIR_RE.match(name):
                suggestions.append(f"{name}/ -> data/models/ (gitignored) or external cache")
            elif os.path.isdir(os.path.join(root, name)):
                suggestions.append(f"{name}/ -> data/ or .scratch/ (or whitelist if it is project code)")
            else:
                suggestions.append(f"{name} -> docs/ or .scratch/")
        suffix = f" (+{len(unknown) - 8} more)" if len(unknown) > 8 else ""
        add("WARN", f"root entries outside whitelist ({len(unknown)}): " + "; ".join(suggestions) + suffix)

    duplicates = [f for f in CONTROL_FILES if os.path.isfile(os.path.join(root, f))]
    if duplicates:
        add("FAIL", "duplicate control plane at project root: " + ", ".join(duplicates)
            + " (use .project/, archive legacy copies)")

    if os.path.isfile(os.path.join(root, ".env")):
        add("WARN", ".env at project root (ensure it is gitignored; prefer data/ or secrets manager)")

    # ---- parallel canonical files (root + docs)
    parallel = []
    for base_dir in (root, os.path.join(root, "docs")):
        if not os.path.isdir(base_dir):
            continue
        for name in os.listdir(base_dir):
            if not name.lower().endswith((".md", ".markdown")):
                continue
            if PARALLEL_RE.match(os.path.splitext(name)[0]):
                parallel.append(os.path.relpath(os.path.join(base_dir, name), root))
    if parallel:
        add("WARN", "parallel canonical candidates: " + ", ".join(parallel[:8]))

    # ---- backups / scratch / outputs / archive
    backups = 0
    for dirpath, dirnames, filenames in os.walk(root):
        depth = dirpath[len(root):].count(os.sep)
        if depth >= 3:
            dirnames[:] = []
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not (depth == 0 and MODEL_DIR_RE.match(d))
        ]
        backups += sum(1 for f in filenames if BACKUP_RE.search(f))
    if backups > 20:
        add("WARN", f"{backups} backup-like files (>20); keep backups in .scratch/backups/ with TTL")

    scratch_count, _ = count_files(os.path.join(root, ".scratch"))
    if scratch_count > 2000:
        add("WARN", f".scratch has {scratch_count} files; add TTL/cleanup")
    out_count, _ = count_files(os.path.join(root, "outputs"), depth_limit=4)
    if out_count > 1000:
        add("WARN", f"outputs has {out_count} files; prune or archive finished runs")

    archive_files, _ = count_files(os.path.join(control_dir, "archive"), depth_limit=4)
    if archive_files == 0 and startup_total > STARTUP_WARN:
        add("WARN", "archive/ is empty while control files exceed budget; snapshot before compacting")

    # ---- legacy state files
    legacy = []
    for dirpath, dirnames, filenames in os.walk(root):
        depth = dirpath[len(root):].count(os.sep)
        if depth >= 3:
            dirnames[:] = []
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name == "PROJECT_STATE.md":
                legacy.append(os.path.relpath(os.path.join(dirpath, name), root))
    if legacy:
        add("WARN", "legacy state files present: " + ", ".join(legacy[:5]))

    fails = sum(1 for level, _ in results if level == "FAIL")
    return results, (2 if fails else (1 if any(l == "WARN" for l, _ in results) else 0))


def title_of(root: str) -> str:
    text = read_text(os.path.join(root, ".project", "PROJECT.md"))
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return ""


def main() -> int:
    args = sys.argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    roots: list[str] = []
    discover_dirs: list[str] = []
    i = 0
    while i < len(args):
        if args[i] == "--discover" and i + 1 < len(args):
            discover_dirs.append(args[i + 1])
            i += 2
        else:
            roots.append(args[i])
            i += 1
    for directory in discover_dirs:
        roots.extend(discover(directory))
    if not roots:
        roots = [os.getcwd()]
    projects = []
    for path in roots:
        root = project_root(path)
        if root and root not in projects:
            projects.append(root)
    if not projects:
        print("no .project control plane found", file=sys.stderr)
        return 2

    report = []
    worst = 0
    titles: dict[str, list[str]] = {}
    for root in projects:
        results, code = audit(root)
        worst = max(worst, code)
        title = title_of(root)
        if title:
            titles.setdefault(title, []).append(root)
        report.append({"project": root, "title": title, "results": results, "exit": code})

    duplicate_titles = {t: paths for t, paths in titles.items() if len(paths) > 1}

    if as_json:
        print(json.dumps({"projects": report, "duplicate_titles": duplicate_titles}, ensure_ascii=False, indent=2))
    else:
        for entry in report:
            print(f"== {entry['project']}")
            for level, message in entry["results"]:
                print(f"  {level:4} {message}")
            print()
        for title, paths in duplicate_titles.items():
            print(f"DUPLICATE PROJECT ({title}): {len(paths)} copies")
            for path in paths:
                print(f"  - {path}")
        counts = {"FAIL": 0, "WARN": 0}
        for entry in report:
            for level, _ in entry["results"]:
                if level in counts:
                    counts[level] += 1
        print(f"SUMMARY: {counts['FAIL']} fail / {counts['WARN']} warn across {len(report)} project(s)")
        if duplicate_titles:
            print("NOTE: duplicate title detection is advisory; confirm which copy is authoritative.")
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
