import type { Plugin } from "@opencode-ai/plugin"
import { existsSync, readFileSync } from "node:fs"
import { join } from "node:path"

export const ContinuityPlugin: Plugin = async ({ worktree, directory }) => {
  const root = worktree || directory

  return {
    "experimental.session.compacting": async (_input, output) => {
      const handoffPath = join(root, ".project", "HANDOFF.md")
      const statePath = join(root, ".project", "STATE.md")

      let source = ""
      let label = ""

      if (existsSync(handoffPath)) {
        source = readFileSync(handoffPath, "utf8").trim()
        label = ".project/HANDOFF.md"
      } else if (existsSync(statePath)) {
        source = readFileSync(statePath, "utf8").trim()
        label = ".project/STATE.md"
      }

      if (!source) return

      // HANDOFF 应保持短小（目标 ≤4KB）。超过 6KB 说明它退化成了日志：
      // 同时保留开头的 Goal/Verified 与结尾的 Open/Next，避免整段历史进入压缩上下文。
      const clipped = source.length <= 6000
        ? source
        : `${source.slice(0, 3000)}\n\n... [middle clipped] ...\n\n${source.slice(-3000)}`

      output.context.push(`
## Project continuity (${label})
Use this as authoritative continuation state when generating the compaction summary.
Preserve Goal, Done, Verified, Rejected, Open, Active, Next, and blockers when present.
Do not restart completed investigations without new evidence.

${clipped}
      `.trim())
    },
  }
}
