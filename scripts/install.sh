#!/usr/bin/env bash
# =====================================================================
# Research Agent OS — OpenCode adapter installer
#
# 幂等安装到 ~/.config/opencode（additive：只添加/更新本项目组件，保留用户已有组件）:
#   AGENTS.md（CORE.md 装配）、agents/(5)、skills/(9)、plugins/(2)
#
# 用法:
#   ./scripts/install.sh             # 正常安装
#   ./scripts/install.sh --dry-run   # 只预览，不修改任何文件
# =====================================================================
set -euo pipefail

DRY_RUN=0
case "${1:-}" in
  --dry-run) DRY_RUN=1 ;;
  "") ;;
  *) echo "usage: $0 [--dry-run]" >&2; exit 2 ;;
esac

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
BACKUP_DIR="${CONFIG_DIR}/backups/research-agent-os-$(date +%Y%m%d-%H%M%S)-$$"

ADAPTER="$REPO_DIR/adapters/opencode"
CORE_MD="$REPO_DIR/core/policies/CORE.md"
PERMS="$ADAPTER/permissions.example.jsonc"

echo "== Research Agent OS installer (OpenCode adapter) =="
echo "repo:   $REPO_DIR"
echo "target: $CONFIG_DIR"
[[ "$DRY_RUN" == "1" ]] && echo "mode:   dry-run (no changes will be made)"
echo

if command -v opencode >/dev/null 2>&1; then
  echo "✔ opencode: $(opencode --version 2>/dev/null | head -n 1 || echo present)"
else
  echo "⚠ opencode not found in PATH — install it first (https://opencode.ai)."
fi
echo

log() { local msg="${2:-}"; printf '%-10s %s\n' "$1" "$msg"; }

same_content() {
  local src="$1" dst="$2"
  [[ -e "$dst" ]] || return 1
  diff -q "$src" "$dst" >/dev/null 2>&1
}

# --- Additive file install: copies src to dst; backups only if diff exists.
file_install() {
  local name="$1" src="$2" dst="$3"
  if [[ -z "$src" || -z "$dst" || "$src" == "/" || "$dst" == "/" ]]; then
    echo "internal error: refusing src='$src' dst='$dst'" >&2; exit 1
  fi
  if same_content "$src" "$dst"; then
    log "SKIP" "$name (identical)"
    return
  fi
  if [[ -e "$dst" ]]; then
    [[ "$DRY_RUN" == "1" ]] && { log "BACKUP" "$name"; return; }
    mkdir -p "$BACKUP_DIR"
    cp "$dst" "$BACKUP_DIR/$(basename "$dst")"
    log "BACKUP" "$name"
  fi
  [[ "$DRY_RUN" == "1" ]] && { log "INSTALL" "$name"; return; }
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  log "INSTALL" "$name"
}

# --- Additive directory install: iterates over src files, installs each into dst.
#     Does NOT rm -rf dst; leaves any pre-existing files untouched.
dir_install_items() {
  local label="$1" srcdir="$2" dstdir="$3"
  if [[ ! -d "$srcdir" ]]; then
    echo "internal error: srcdir missing: $srcdir" >&2; exit 1
  fi
  shopt -s nullglob dotglob
  for item in "$srcdir"/*; do
    local base
    base="$(basename "$item")"
    [[ "$base" == "." || "$base" == ".." ]] && continue
    if [[ -d "$item" ]]; then
      # 子目录：递归复制（例如 code-reviewer/references/）
      # 用 rsync-like 方式：先备份目标子目录（如果不同）
      if [[ -d "$dstdir/$base" ]]; then
        if diff -r -q "$item" "$dstdir/$base" >/dev/null 2>&1; then
          log "SKIP" "$label/$base/ (identical)"
          continue
        fi
        if [[ "$DRY_RUN" == "1" ]]; then
          log "BACKUP" "$label/$base/"
        else
          mkdir -p "$BACKUP_DIR"
          cp -R "$dstdir/$base" "$BACKUP_DIR/${base}.bak"
          rm -rf "$dstdir/$base"
          cp -R "$item" "$dstdir/$base"
          log "INSTALL" "$label/$base/"
        fi
      else
        [[ "$DRY_RUN" == "1" ]] && { log "INSTALL" "$label/$base/"; continue; }
        mkdir -p "$dstdir"
        cp -R "$item" "$dstdir/$base"
        log "INSTALL" "$label/$base/"
      fi
    else
      file_install "$label/$base" "$item" "$dstdir/$base"
    fi
  done
  shopt -u nullglob dotglob
}

echo "== Core components =="
[[ "$DRY_RUN" == "1" ]] || mkdir -p "$CONFIG_DIR"

# --- AGENTS.md (assembled from CORE.md) ---
work_agents="$(mktemp)"
trap 'rm -f "$work_agents"' EXIT
cat "$ADAPTER/AGENTS.md.header" > "$work_agents"
cat "$CORE_MD" >> "$work_agents"
if [[ -f "$CONFIG_DIR/AGENTS.md" ]] && diff -q "$work_agents" "$CONFIG_DIR/AGENTS.md" >/dev/null 2>&1; then
  log "SKIP" "AGENTS.md (assembled) identical"
elif [[ "$DRY_RUN" == "1" ]]; then
  log "INSTALL" "AGENTS.md (assembled from core/policies/CORE.md)"
else
  if [[ -e "$CONFIG_DIR/AGENTS.md" ]]; then
    mkdir -p "$BACKUP_DIR"
    cp "$CONFIG_DIR/AGENTS.md" "$BACKUP_DIR/AGENTS.md"
    log "BACKUP" "AGENTS.md (previous)"
  fi
  cp "$work_agents" "$CONFIG_DIR/AGENTS.md"
  log "INSTALL" "AGENTS.md (assembled from core/policies/CORE.md)"
fi

# --- Additive installations (do NOT replace whole directories) ---
dir_install_items "agents"  "$ADAPTER/agents"  "$CONFIG_DIR/agents"
dir_install_items "skills"  "$REPO_DIR/core/skills" "$CONFIG_DIR/skills"
dir_install_items "plugins" "$ADAPTER/plugins" "$CONFIG_DIR/plugins"

echo
echo "== Global config =="
if [[ -e "$CONFIG_DIR/opencode.json" || -e "$CONFIG_DIR/opencode.jsonc" ]]; then
  log "KEEP" "existing opencode.json* untouched (user config)"
  log ""
  log "  ┌─ Manual merge needed ──────────────────────────────────────────┐"
  log "  │ 1. Ensure default_agent is set to \"research-lead\"              │"
  log "  │ 2. Merge Trusted Mode permissions from                         │"
  log "  │    $PERMS"
  log "  │    into the \"permission\" field of your opencode.json           │"
  log "  └────────────────────────────────────────────────────────────────┘"
else
  if [[ "$DRY_RUN" == "1" ]]; then
    log "INSTALL" "opencode.json (minimal config with Trusted Mode + default_agent: research-lead)"
  else
    cp "$REPO_DIR/adapters/opencode/opencode.minimal.json" "$CONFIG_DIR/opencode.json"
    log "INSTALL" "opencode.json (minimal with Trusted Mode + default_agent: research-lead)"
  fi
fi

echo
echo "== Result =="
if [[ "$DRY_RUN" == "1" ]]; then
  echo "dry-run complete: no files were modified."
else
  if [[ -d "$BACKUP_DIR" ]] && [[ -n "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]]; then
    echo "Backups: $BACKUP_DIR"
  else
    echo "No backups needed (fresh install or already up to date)."
  fi
  echo "Next: python3 scripts/doctor.py   |   python3 scripts/init-project.py --dir <project>"
fi