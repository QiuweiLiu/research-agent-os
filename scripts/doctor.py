#!/usr/bin/env python3
"""
doctor.py — diagnostics for a Research Agent OS Core installation / repo.

Checks (read-only, no repairs):
  [A] OpenCode   : installed, version recognizable
  [B] Core       : AGENTS.md assembled, 5 roles, 9 skills, 2 plugins, gate contract
  [C] Project OS : core/project templates; HANDOFF schema; EXPERIMENT_GATE.json contract
  [D] Decoupling : core/ has no harness-specific terms; roles not model-bound;
                   no excluded terms (Luna/Sol/vision/research-reviewer/scheduler) in public files
  [E] Security   : no secrets/personal leftovers; Trusted Mode denies; gitignore
  [F] Installer  : additive pattern (not rm -rf whole dirs); agent routing valid;
                   opencode.minimal.json valid (exists, parseable, default_agent, permission)
  [G] Continuity : continuity + research-guard hooks wired

Exit codes: 0 = READY, 1 = READY WITH WARNINGS, 2 = NOT READY

Usage:
  python3 scripts/doctor.py                         # check repo
  python3 scripts/doctor.py --check-installed        # also check ~/.config/opencode/ installation
  python3 scripts/doctor.py --repo /path             # check a different repo
  python3 scripts/doctor.py --check-installed --repo /path
"""

import json
import os
import re
import shutil
import subprocess
import sys

EXPECTED_ROLES = ["research-lead.md", "scout.md", "runner.md", "reviewer.md", "auditor.md"]
EXPECTED_SKILLS = [
    "agent-workflow-optimizer", "experiment-scientist", "experiment-reviewer",
    "compute-budget", "reproducibility", "evidence-synthesizer",
    "failure-triage", "code-reviewer", "repo-architecture",
]
EXPECTED_PLUGINS = ["continuity.ts", "research-guard.js"]
PROJECT_TEMPLATE_FILES = [
    "PROJECT.md", "STATE.md", "PLAN.md", "DECISIONS.md",
    "HANDOFF.md", "EXPERIMENT_GATE.json",
]
HANDOFF_SECTIONS = ["Goal", "Done", "Verified", "Rejected", "Open", "Active", "Next"]
GATE_KEYS = {"smoke_passed", "ledger_registered", "commit"}
TRUSTED_DENY_RULES = [
    "sudo *", "rm -rf *", "rm -fr *",
    "git reset --hard*", "git clean*",
    "git push --force*", "git push -f*",
]
HARNESS_TERMS = re.compile(r"opencode|openai|anthropic|claude|gpt-|mcp", re.I)
# 公开版排除的私人/领域词（出现在公开文件内容中即违规，README 等显式说明除外）
EXCLUDED_TERMS = re.compile(
    r"\bluna\b|\bsol\b|\bdeepseek\b|\bvision\b|\bresearch-reviewer\b"
    r"|\bscheduler\b|\bscheduling\b|\bimage-server\b|\bpaper-figure\b|\boffice-docs\b|\bui-review\b"
    r"|\bopenai-docs\b|\bfind-skills\b|\bknowledge-retrieval\b|\bcode-minimalism\b",
    re.I,
)
EXCLUDED_SCAN_SKIP = {"README.md", "classification.md", "doctor.py", "install.sh"}
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.I),
    re.compile(r"(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|secret|password)\s*[:=]\s*[\"'][^\"']{12,}[\"']", re.I),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bbce-v3/ALTAK[A-Za-z0-9/_-]{8,}\b"),
]
PERSONAL_PATTERNS = [
    re.compile(r"westc|seetacloud", re.I),
    re.compile(r"token\.sensenova|qianfan\.baidubce", re.I),
    re.compile(r"ALTAKSP|bce-v3|sk-", re.I),
    re.compile(r"id_ed25519", re.I),
    re.compile(r"\.ssh/", re.I),
]
SKIP_DIRS = {"node_modules", "backups", ".git", "archive", "__pycache__"}


def dedup_keys(text: str):
    """检测 JSONC 文本中的重复 key（忽略注释中的字符串，忽略跨对象的 `*` 通配符）。
    返回造成真实重复语义的 key 列表。"""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] not in "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i = min(i + 2, n)
            continue
        out.append(c)
        i += 1
    clean = "".join(out)
    keys = re.findall(r'"([^"]+)"\s*:', clean)
    # 跨对象重复的 `*` 通配符是合法的（每个对象有自己的 `*`）
    allowed_cross = {"*", "read", "bash", "edit", "git", "env", "rm"}
    dups = set()
    for k in sorted(set(keys)):
        if keys.count(k) > 1 and k not in allowed_cross:
            dups.add(k)
    # 特殊检查：`"read"` 同时作为对象和标量值出现才是真重复
    if "read" in keys:
        scalar_read = re.findall(r'"read"\s*:\s*"(?:allow|ask|deny)"', clean)
        obj_read = re.findall(r'"read"\s*:\s*\{', clean)
        if len(scalar_read) > 0 and len(obj_read) > 0:
            dups.add("read")
    return sorted(dups)


def jsonc_load(path: str):
    text = open(path, encoding="utf-8").read()
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] not in "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i = min(i + 2, n)
            continue
        out.append(c)
        i += 1
    s = "".join(out)
    s = re.sub(r",(\s*[}\]])", r"\1", s)
    return json.loads(s)


def walk_text_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            p = os.path.join(dirpath, f)
            if os.path.basename(p) in ("doctor.py", "install.sh"):
                continue
            try:
                with open(p, "rb") as fh:
                    raw = fh.read(4096)
            except OSError:
                continue
            if b"\x00" in raw:
                continue
            yield p


def file_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


class Doctor:
    def __init__(self, repo: str, check_installed: bool = False):
        self.repo = repo
        self.check_installed = check_installed
        self.fails = 0
        self.warns = 0

    def emit(self, status, section, name, ok, detail=""):
        if status == "FAIL":
            self.fails += 1
        elif status == "WARN":
            self.warns += 1
        mark = {"PASS": " ✔", "WARN": " △", "FAIL": " ✘"}[status]
        print(f"{mark} [{section}] {name}" + (f" — {detail}" if detail else ""))
        return ok

    def run(self) -> int:
        repo = self.repo
        core = os.path.join(repo, "core")
        core_skills = os.path.join(core, "skills")
        core_project = os.path.join(core, "project")
        policies = os.path.join(core, "policies")
        adapters = os.path.join(repo, "adapters", "opencode")
        agents = os.path.join(adapters, "agents")
        plugins = os.path.join(adapters, "plugins")
        perms = os.path.join(adapters, "permissions.example.jsonc")
        agheader = os.path.join(adapters, "AGENTS.md.header")
        install_sh = os.path.join(repo, "scripts", "install.sh")

        # ============ [A] OpenCode ============
        print("== [A] OpenCode ==")
        bin_path = shutil.which("opencode")
        version = ""
        if bin_path:
            try:
                r = subprocess.run(["opencode", "--version"], capture_output=True, text=True, timeout=15)
                version = (r.stdout or r.stderr or "").strip()
            except Exception:
                pass
        ok = bool(bin_path and re.search(r"\d+(\.\d+)+", version))
        self.emit("PASS" if ok else ("WARN" if bin_path else "FAIL"), "A", "opencode installed & version",
                  ok, f"v{version}" if ok else ("found, version unparsed" if bin_path else "not in PATH (install first)"))

        # ============ [B] Core components ============
        print("== [B] Core components ==")
        have_core_md = os.path.isfile(os.path.join(policies, "CORE.md"))
        self.emit("FAIL" if not have_core_md else "PASS", "B", "core/policies/CORE.md", have_core_md)
        have_header = os.path.isfile(agheader)
        self.emit("FAIL" if not have_header else "PASS", "B", "adapter AGENTS.md.header", have_header,
                  "" if have_header else "install cannot assemble AGENTS.md")

        missing_roles = [f for f in EXPECTED_ROLES if not os.path.isfile(os.path.join(agents, f))]
        self.emit("FAIL" if missing_roles else "PASS", "B", "adapter roles (5)",
                  not missing_roles, f"missing: {missing_roles}" if missing_roles else "research-lead/scout/runner/reviewer/auditor")

        skills = []
        if os.path.isdir(core_skills):
            skills = sorted(d for d in os.listdir(core_skills)
                            if os.path.isdir(os.path.join(core_skills, d)) and not d.startswith("."))
        missing_skills = [s for s in EXPECTED_SKILLS if s not in skills]
        self.emit("FAIL" if missing_skills else "PASS", "B", "core skills (9)",
                  not missing_skills, f"missing: {missing_skills}" if missing_skills else f"{len(skills)} found (expected 9)")
        no_skillmd = [s for s in skills if not os.path.isfile(os.path.join(core_skills, s, "SKILL.md"))]
        self.emit("FAIL" if no_skillmd else "PASS", "B", "every skill has SKILL.md", not no_skillmd,
                  f"missing: {no_skillmd}" if no_skillmd else f"{len(skills)}/{len(skills)}")

        plugins_found = sorted(os.listdir(plugins)) if os.path.isdir(plugins) else []
        missing_plugins = [p for p in EXPECTED_PLUGINS if p not in plugins_found]
        self.emit("FAIL" if missing_plugins else "PASS", "B", "adapter plugins (2)",
                  not missing_plugins, f"missing: {missing_plugins}" if missing_plugins else "continuity.ts + research-guard.js")

        # ============ [C] Project OS ============
        print("== [C] Project OS ==")
        missing_tpl = [f for f in PROJECT_TEMPLATE_FILES
                       if not os.path.isfile(os.path.join(core_project, f))]
        self.emit("FAIL" if missing_tpl else "PASS", "C", "core/project templates (6)",
                  not missing_tpl, f"missing: {missing_tpl}" if missing_tpl else "6/6 present")

        ht = file_text(os.path.join(core_project, "HANDOFF.md"))
        missing_sec = [s for s in HANDOFF_SECTIONS if not re.search(rf"^##\s*{re.escape(s)}\b", ht, re.M)]
        self.emit("FAIL" if missing_sec else "PASS", "C", "HANDOFF template schema", not missing_sec,
                  f"missing: {missing_sec}" if missing_sec else "Goal/Done/Verified/Rejected/Open/Active/Next")

        gate = os.path.join(core_project, "EXPERIMENT_GATE.json")
        if os.path.isfile(gate):
            try:
                gate_data = json.load(open(gate, encoding="utf-8"))
                missing_keys = sorted(GATE_KEYS - gate_data.keys())
                self.emit("FAIL" if missing_keys else "PASS", "C", "EXPERIMENT_GATE.json contract",
                          not missing_keys, f"missing keys: {missing_keys}" if missing_keys else "smoke_passed/ledger_registered/commit")
            except Exception as e:
                self.emit("FAIL", "C", "EXPERIMENT_GATE.json valid JSON", False, str(e))
        else:
            self.emit("FAIL", "C", "EXPERIMENT_GATE.json present", False)

        # ============ [D] Decoupling ============
        print("== [D] Decoupling ==")
        leaks = []
        for f in walk_text_files(core):
            if HARNESS_TERMS.search(file_text(f)):
                leaks.append(os.path.relpath(f, repo))
        self.emit("WARN" if leaks else "PASS", "D", "core/ has no harness-specific terms",
                  not leaks, "; ".join(leaks[:4]) if leaks else "core/ is harness-agnostic")

        # 排除词检查：公开文件不应包含旧私人/领域词
        excluded_hits = []
        for f in walk_text_files(repo):
            base = os.path.basename(f)
            if base in EXCLUDED_SCAN_SKIP:
                continue
            content = file_text(f)
            if EXCLUDED_TERMS.search(content):
                excluded_hits.append(f"{os.path.relpath(f, repo)}")
        self.emit("FAIL" if excluded_hits else "PASS", "D", "no excluded terms in public files",
                  not excluded_hits, "; ".join(excluded_hits[:5]) if excluded_hits else "Luna/Sol/vision/research-reviewer/scheduler absent")

        # roles not model-bound
        bound = []
        for f in EXPECTED_ROLES:
            txt = file_text(os.path.join(agents, f))
            m = re.search(r"^(?:model|variant):\s*(\S+)", txt, re.M)
            if m:
                bound.append(f"{f} -> {m.group(1)}")
        self.emit("FAIL" if bound else "PASS", "D", "roles not model-bound", not bound,
                  "; ".join(bound) if bound else "model/variant absent (models chosen by user)")

        # ============ [E] Security ============
        print("== [E] Security ==")
        secrets = []
        for f in walk_text_files(repo):
            if os.path.basename(f).startswith("permissions.example"):
                continue
            content = file_text(f)
            for p in SECRET_PATTERNS + PERSONAL_PATTERNS:
                if p.search(content):
                    secrets.append(f"{os.path.relpath(f, repo)} ({p.pattern[:30]})")
                    break
        self.emit("FAIL" if secrets else "PASS", "E", "no secrets / personal leftovers",
                  not secrets, "; ".join(secrets[:5]) if secrets else "clean")

        # JSONC duplicate keys
        dup_keys = []
        for jc_file in [perms, os.path.join(repo, "core", "project", "EXPERIMENT_GATE.json")]:
            if os.path.isfile(jc_file):
                try:
                    dk = dedup_keys(open(jc_file, encoding="utf-8").read())
                    if dk:
                        dup_keys.append(f"{os.path.basename(jc_file)}: {dk}")
                except Exception:
                    pass
        self.emit("FAIL" if dup_keys else "PASS", "E", "JSONC no duplicate keys", not dup_keys,
                  "; ".join(dup_keys) if dup_keys else "all JSONC files clean")

        deny_rules = set()
        if os.path.isfile(perms):
            try:
                deny_rules = {k for k, v in jsonc_load(perms).get("bash", {}).items() if v == "deny"}
            except Exception as e:
                self.emit("FAIL", "E", "permissions.example.jsonc parseable", False, str(e))
        missing_deny = [r for r in TRUSTED_DENY_RULES if r not in deny_rules]
        self.emit("FAIL" if missing_deny else "PASS", "E", "Trusted Mode destructive denies",
                  not missing_deny, f"missing: {missing_deny}" if missing_deny else f"{len(deny_rules)} deny rules")

        gi = file_text(os.path.join(repo, ".gitignore"))
        gi_ok = ".env" in gi and "*.pem" in gi and "node_modules" in gi
        self.emit("WARN" if not gi_ok else "PASS", "E", ".gitignore covers secrets", gi_ok,
                  "" if gi_ok else "add .env / *.pem / node_modules")

        # ============ [F] Installer ============
        print("== [F] Installer ==")
        # Check additive pattern (no rm -rf in install.sh for directories)
        install_txt = file_text(install_sh)
        has_rm_rf = "rm -rf" in install_txt
        has_additive = "dir_install_items" in install_txt
        additive_ok = not has_rm_rf or has_additive
        self.emit("FAIL" if not additive_ok else "PASS", "F", "additive directory install (no rm -rf whole dirs)",
                  additive_ok, "uses dir_install_items (additive)" if has_additive else "uses rm -rf (replaces whole dirs)")

        # Agent routing: research-lead should not reference non-existent agents
        lead_txt = file_text(os.path.join(agents, "research-lead.md"))
        for bad_ref in ["vision", "research-reviewer"]:
            if bad_ref in lead_txt:
                self.emit("FAIL", "F", f"agent routing to non-existent '{bad_ref}'", False,
                          "research-lead.md still references excluded agent")
                break
        else:
            self.emit("PASS", "F", "agent routing to existing agents only", True,
                      "no references to vision/research-reviewer")

        # Fresh config default_agent check
        fresh_cfg = os.path.join(repo, "adapters", "opencode", "opencode.minimal.json")
        if os.path.isfile(fresh_cfg):
            try:
                with open(fresh_cfg, encoding="utf-8") as fh:
                    fc = json.load(fh)
                fc_ok = True
                fc_issues = []
                if fc.get("default_agent") != "research-lead":
                    fc_issues.append("default_agent != 'research-lead'")
                if "permission" not in fc:
                    fc_issues.append("missing 'permission' key")
                self.emit("FAIL" if fc_issues else "PASS", "F", "opencode.minimal.json valid",
                          not fc_issues, "; ".join(fc_issues) if fc_issues else
                          "exists, parseable, default_agent=research-lead, permission present")
            except Exception as e:
                self.emit("FAIL", "F", "opencode.minimal.json parseable", False, str(e))
        else:
            self.emit("FAIL", "F", "opencode.minimal.json exists", False)

        # ============ [G] Continuity ============
        print("== [G] Continuity ==")
        cont = file_text(os.path.join(plugins, "continuity.ts"))
        guard = file_text(os.path.join(plugins, "research-guard.js"))
        ok_cont = "experimental.session.compacting" in cont
        ok_guard = "tool.execute.before" in guard and "EXPERIMENT_GATE" in guard
        self.emit("FAIL" if not ok_cont else "PASS", "G", "continuity hook", ok_cont,
                  "experimental.session.compacting" if ok_cont else "hook NOT found")
        self.emit("FAIL" if not ok_guard else "PASS", "G", "research-guard hook", ok_guard,
                  "tool.execute.before + gate contract" if ok_guard else "hook NOT found")

        # ============ [H] Installation (--check-installed) ============
        if self.check_installed:
            print("== [H] Installation ==")
            install_dir = os.path.expanduser("~/.config/opencode")
            if not os.path.isdir(install_dir):
                self.emit("FAIL", "H", "opencode config directory", False, f"{install_dir} not found — adapter not installed")
            else:
                # AGENTS.md
                agents_md_inst = os.path.join(install_dir, "AGENTS.md")
                has_ag = os.path.isfile(agents_md_inst)
                self.emit("FAIL" if not has_ag else "PASS", "H", "AGENTS.md installed",
                          has_ag, "" if has_ag else "missing")

                # 5 roles
                inst_agents = os.path.join(install_dir, "agents")
                installed_roles = sorted(os.listdir(inst_agents)) if os.path.isdir(inst_agents) else []
                missing_roles = [f for f in EXPECTED_ROLES if f not in installed_roles]
                self.emit("FAIL" if missing_roles else "PASS", "H", "Research Agent OS roles (5)",
                          not missing_roles,
                          f"missing: {missing_roles}" if missing_roles else f"{len(EXPECTED_ROLES)-len(missing_roles)}/5 present")

                # 9 skills
                inst_skills = os.path.join(install_dir, "skills")
                installed_skills = set(os.listdir(inst_skills)) if os.path.isdir(inst_skills) else set()
                missing_skills = [s for s in EXPECTED_SKILLS if s not in installed_skills]
                self.emit("FAIL" if missing_skills else "PASS", "H", "Core Skills (9)",
                          not missing_skills,
                          f"missing: {missing_skills}" if missing_skills else f"{len(EXPECTED_SKILLS)-len(missing_skills)}/9 present")

                # 2 plugins
                inst_plugins = os.path.join(install_dir, "plugins")
                installed_plugins = set(os.listdir(inst_plugins)) if os.path.isdir(inst_plugins) else set()
                missing_plugins = [p for p in EXPECTED_PLUGINS if p not in installed_plugins]
                self.emit("FAIL" if missing_plugins else "PASS", "H", "Core plugins (2)",
                          not missing_plugins,
                          f"missing: {missing_plugins}" if missing_plugins else "continuity.ts + research-guard.js present")

                # opencode.json/jsonc
                cfg_json = os.path.join(install_dir, "opencode.json")
                cfg_jsonc = os.path.join(install_dir, "opencode.jsonc")
                if os.path.isfile(cfg_json):
                    try:
                        cfg = json.load(open(cfg_json, encoding="utf-8"))
                        da_ok = cfg.get("default_agent") == "research-lead"
                        perm_ok = "permission" in cfg
                        self.emit("FAIL" if not (da_ok and perm_ok) else "PASS", "H",
                                  "opencode.json: default_agent + permission",
                                  da_ok and perm_ok,
                                  ("default_agent=" + str(cfg.get("default_agent")) if not da_ok else "") +
                                  ("; " if not da_ok and not perm_ok else "") +
                                  ("missing permission" if not perm_ok else ""))
                    except Exception as e:
                        self.emit("FAIL", "H", "opencode.json parseable", False, str(e))
                elif os.path.isfile(cfg_jsonc):
                    try:
                        cfg = jsonc_load(cfg_jsonc)
                        da_ok = cfg.get("default_agent") == "research-lead"
                        perm_ok = "permission" in cfg
                        self.emit("FAIL" if not (da_ok and perm_ok) else "PASS", "H",
                                  "opencode.jsonc: default_agent + permission",
                                  da_ok and perm_ok,
                                  ("default_agent=" + str(cfg.get("default_agent")) if not da_ok else "") +
                                  ("; " if not da_ok and not perm_ok else "") +
                                  ("missing permission" if not perm_ok else ""))
                    except Exception as e:
                        self.emit("FAIL", "H", "opencode.jsonc parseable", False, str(e))
                else:
                    self.emit("WARN", "H", "opencode.json/jsonc", False, "not found — install with scripts/install.sh first")

        print()
        if self.fails:
            print(f"NOT READY — {self.fails} failing check(s), {self.warns} warning(s)")
            return 2
        if self.warns:
            print("READY WITH WARNINGS")
            return 1
        print("READY")
        return 0


def main() -> int:
    repo = None
    check_installed = False
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__)
        return 0
    i = 0
    while i < len(args):
        if args[i] == "--repo" and i + 1 < len(args):
            repo = os.path.abspath(args[i + 1])
            i += 2
        elif args[i] == "--check-installed":
            check_installed = True
            i += 1
        else:
            print(f"unknown argument: {args[i]}")
            return 2
    if repo is None:
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"doctor: {repo}\n")
    return Doctor(repo, check_installed).run()


if __name__ == "__main__":
    sys.exit(main())