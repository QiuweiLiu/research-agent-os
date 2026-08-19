#!/usr/bin/env python3
"""
init-project.py — bootstrap a research project with the Project OS control plane.

Creates in the target directory:
  .project/{PROJECT,STATE,PLAN,DECISIONS,HANDOFF}.md
  .project/EXPERIMENT_GATE.json
  .project/archive/
  docs/ experiments/ outputs/ .scratch/

Safety:
  - never touches .project/ that already has content (unless --force)
  - --dry-run prints a plan, changes nothing
  - refuses to follow symlinks; pre-checks that all templates exist
  - never deletes unrelated files

Usage:
  python3 scripts/init-project.py [--dir PATH] [--name NAME] [--force] [--dry-run]
"""

import argparse
import os
import re
import sys

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "project")
TEMPLATE_FILES = [
    "PROJECT.md", "STATE.md", "PLAN.md", "DECISIONS.md",
    "HANDOFF.md", "EXPERIMENT_GATE.json",
]
EXTRA_DIRS = ["docs", "experiments", "outputs", ".scratch"]


def render(text: str, name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.\- ]", "", name or "").strip() or "my-project"
    return text.replace("__PROJECT_NAME__", safe)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=".", help="target directory (default: current)")
    ap.add_argument("--name", default=None, help="project name used in templates")
    ap.add_argument("--force", action="store_true", help="overwrite existing .project/ template files")
    ap.add_argument("--dry-run", action="store_true", help="print actions without executing")
    args = ap.parse_args()

    target = os.path.abspath(args.dir)
    name = args.name or os.path.basename(target.rstrip(os.sep)) or "project"
    proj_dir = os.path.join(target, ".project")

    if not os.path.isdir(target):
        print(f"E target directory does not exist: {target}")
        return 2
    if os.path.isdir(proj_dir) and any(os.scandir(proj_dir)):
        if not args.force:
            print(f"E {proj_dir} already exists and is not empty. Use --force to overwrite template files.")
            return 1

    # 模板预检:任何写入之前确认全部模板可读
    missing = [f for f in TEMPLATE_FILES if not os.path.isfile(os.path.join(TEMPLATE_DIR, f))]
    if missing:
        print(f"E templates missing under {TEMPLATE_DIR}: {missing}")
        return 2
    templates = {}
    for f in TEMPLATE_FILES:
        with open(os.path.join(TEMPLATE_DIR, f), encoding="utf-8") as fh:
            templates[f] = fh.read()

    planned = [f"mkdir -p {proj_dir}/archive"] + [
        f"write {proj_dir}/{f}" for f in TEMPLATE_FILES
    ] + [f"mkdir -p {target}/{d} (if missing)" for d in EXTRA_DIRS]
    if args.dry_run:
        print("dry-run — would do:")
        for p in planned:
            print(f"  {p}")
        return 0

    os.makedirs(os.path.join(proj_dir, "archive"), exist_ok=True)
    for f in TEMPLATE_FILES:
        dst = os.path.join(proj_dir, f)
        if os.path.islink(dst) or os.path.islink(proj_dir):
            print(f"E refusing to follow symlink: {dst}")
            return 2
        if os.path.exists(dst) and not args.force:
            print(f"  keep {dst} (exists, no --force)")
            continue
        text = render(templates[f], name) if f.endswith(".md") else templates[f]
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"  write {dst}")
    for d in EXTRA_DIRS:
        existed = os.path.isdir(os.path.join(target, d))
        os.makedirs(os.path.join(target, d), exist_ok=True)
        print(f"  keep {target}/{d}" if existed else f"  mkdir {target}/{d}")

    print("Done. Read .project/PROJECT.md and record your goals there.")
    return 0


if __name__ == "__main__":
    sys.exit(main())