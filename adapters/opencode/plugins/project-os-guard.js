import { existsSync } from "node:fs"
import path from "node:path"

const CONTROL_FILES = new Set([
  "PROJECT.md",
  "STATE.md",
  "PLAN.md",
  "DECISIONS.md",
  "HANDOFF.md",
])

// Parallel-canonical names that must never be created next to the canonical docs.
const PARALLEL_CANONICAL = /^(?:plan_v\d+|summary_final|analysis_new|final_report)(?:\.md)?$/i

function targetPath(args) {
  for (const key of ["filePath", "path", "file", "filename"]) {
    if (typeof args?.[key] === "string") return args[key]
  }
  return ""
}

export const ProjectOsGuard = async ({ directory, worktree }) => {
  const root = worktree || directory
  const controlDir = path.join(root, ".project")

  return {
    "tool.execute.before": async (input, output) => {
      if (process.env.OPENCODE_PROJECTOS_GUARD === "off") return
      const tool = input?.tool || ""
      if (!["edit", "write", "apply_patch"].includes(tool)) return

      const target = targetPath(output?.args || {})
      if (!target) return

      const abs = path.resolve(root, target)
      const rel = path.relative(root, abs)
      if (rel.startsWith("..") || path.isAbsolute(rel)) return

      const base = path.basename(abs)
      const isRootLevel = !rel.includes(path.sep)

      // 1) Root-level control files must not shadow .project/.
      if (isRootLevel && CONTROL_FILES.has(base) && existsSync(controlDir)) {
        throw new Error(
          `[project-os-guard] 根目录控制面副本被拒绝：${rel}。` +
            `控制面唯一真相源是 .project/${base}；旧副本请移入 .project/archive/`
        )
      }

      // 2) Never create parallel canonical documents.
      if (PARALLEL_CANONICAL.test(base)) {
        throw new Error(
          `[project-os-guard] 疑似平行 canonical：${rel}。` +
            `请更新现有文件，或归档到 .project/archive/（不要新建 plan_v2/summary_final/analysis_new）`
        )
      }
    },
  }
}
