#!/usr/bin/env bash
# =====================================================================
# Research Agent OS — OpenCode adapter installer（最小版）
#
# 安装到 ~/.config/opencode：AGENTS.md（CORE.md 装配）、agents/(5)、
# skills/(9)、plugins/(2)。幂等；备份有差异的旧文件；不覆盖已有 opencode.json*；
# 不写入任何 secret；--dry-run 零副作用。
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

echo "== Research Agent OS installer (OpenCode adapter) =="
echo "repo:   $REPO_DIR"
echo "target: $CONFIG_DIR"
[[ "$DRY_RUN" == "1" ]] && echo "mode:   dry-run (no changes will be made)"
echo

if command -v opencode >/dev/null 2>&1; then
  echo "✔ opencode: $(opencode --version 2>/dev/null | head -n 1 || echo present)"
else
  echo "⚠ opencode not found in PATH — install it first (https://opencode.ai). Files below are still installed."
fi
echo

log() { printf '%-10s %s\n' "$1" "$2"; }

same_content() {
  local src="$1" dst="$2"
  [[ -e "$dst" ]] || return 1
  if [[ -d "$src" ]]; then
    diff -r -q "$src" "$dst" >/dev/null 2>&1
  else
    diff -q "$src" "$dst" >/dev/null 2>&1
  fi
}

# install_item <name> <src> <dst> —— 文件/目录幂等安装
install_item() {
  local name="$1" src="$2" dst="$3"
  if [[ -z "$src" || -z "$dst" || "$src" == "/" || "$dst" == "/" || "$src" == "$dst" ]]; then
    echo "internal error: refusing src='$src' dst='$dst'" >&2
    exit 1
  fi
  if same_content "$src" "$dst"; then
    log "SKIP" "$name already installed and identical"
    return
  fi
  if [[ -e "$dst" ]]; then
    if [[ "$DRY_RUN" == "1" ]]; then
      log "BACKUP" "$name -> $BACKUP_DIR/$(basename "$dst")"
    else
      mkdir -p "$BACKUP_DIR"
      cp -R "$dst" "$BACKUP_DIR/$(basename "$dst")"
      log "BACKUP" "$name (previous version backed up)"
    fi
  fi
  if [[ -d "$src" ]]; then
    [[ "$DRY_RUN" == "1" ]] && { log "INSTALL" "$name/"; return; }
    rm -rf -- "$dst"
    mkdir -p "$(dirname "$dst")"
    cp -R "$src" "$dst"
    log "INSTALL" "$name/"
  else
    [[ "$DRY_RUN" == "1" ]] && { log "INSTALL" "$name"; return; }
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    log "INSTALL" "$name"
  fi
}

echo "== Core components =="
[[ "$DRY_RUN" == "1" ]] || mkdir -p "$CONFIG_DIR"

# AGENTS.md := header + CORE.md（单一事实源装配）
work_agents="$(mktemp)"
trap 'rm -f "$work_agents"' EXIT
cat "$ADAPTER/AGENTS.md.header" > "$work_agents"
cat "$CORE_MD" >> "$work_agents"
if [[ -f "$CONFIG_DIR/AGENTS.md" ]] && diff -q "$work_agents" "$CONFIG_DIR/AGENTS.md" >/dev/null 2>&1; then
  log "SKIP" "AGENTS.md (assembled from core/policies/CORE.md) identical"
elif [[ "$DRY_RUN" == "1" ]]; then
  log "INSTALL" "AGENTS.md (assembled from core/policies/CORE.md)"
else
  if [[ -e "$CONFIG_DIR/AGENTS.md" ]]; then
    mkdir -p "$BACKUP_DIR"
    cp "$CONFIG_DIR/AGENTS.md" "$BACKUP_DIR/AGENTS.md"
    log "BACKUP" "AGENTS.md (previous version backed up)"
  fi
  cp "$work_agents" "$CONFIG_DIR/AGENTS.md"
  log "INSTALL" "AGENTS.md (assembled from core/policies/CORE.md)"
fi

install_item "agents/"  "$ADAPTER/agents"  "$CONFIG_DIR/agents"
install_item "skills/"  "$REPO_DIR/core/skills" "$CONFIG_DIR/skills"
install_item "plugins/" "$ADAPTER/plugins" "$CONFIG_DIR/plugins"

echo
echo "== Global config =="
if [[ -e "$CONFIG_DIR/opencode.json" || -e "$CONFIG_DIR/opencode.jsonc" ]]; then
  log "KEEP" "existing opencode.json* untouched (user config)"
  log "HINT" "merge Trusted Mode permissions from adapters/opencode/permissions.example.jsonc manually"
else
  if [[ "$DRY_RUN" == "1" ]]; then
    log "INSTALL" "opencode.json (would copy Trusted Mode baseline)"
  else
    cp "$ADAPTER/permissions.example.jsonc" "$CONFIG_DIR/opencode.json"
    log "INSTALL" "opencode.json (Trusted Mode baseline; add your provider/model)"
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