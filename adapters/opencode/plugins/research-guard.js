import { existsSync, readFileSync } from "node:fs"
import path from "node:path"

const SENSITIVE_PATH = /(?:^|\/)(?:\.env(?:\.[^/]+)?|credentials?|.*private.*key.*|.*cookies?)(?:\/|$)|\.(?:pem|key)$/i
const SECRET_CONTENT = /-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----|(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*["'][^"']{12,}["']/i
const DESTRUCTIVE_COMMAND = /(?:^|[;&|]\s*)(?:rm\s+-rf\b|git\s+reset\s+--hard\b|git\s+clean(?:\s|$)|git\s+push\b[^\n;&|]*(?:--force\b|-f(?:\s|$)))/i
const SECRET_READ_COMMAND = /\b(?:cat|less|more|head|tail|sed|awk|python|python3|node|ruby|perl|printenv|env)\b[^\n;&|]*(?:\.env(?:\b|\.)|credentials?|id_(?:rsa|ed25519)|\.(?:pem|key)\b|cookies?)/i
const FORMAL_RUN_COMMAND = /\b(?:sbatch|srun|qsub)\b|\b(?:full[-_ ]?scale|formal[-_ ]?(?:run|experiment))\b/i

function asText(value) {
  if (typeof value === "string") return value
  try {
    return JSON.stringify(value ?? "")
  } catch {
    return String(value ?? "")
  }
}

function targetPath(args) {
  for (const key of ["filePath", "path", "file", "filename"]) {
    if (typeof args?.[key] === "string") return args[key]
  }
  return ""
}

function fail(kind, message) {
  throw new Error(`[research-guard:${kind}] ${message}`)
}

function gatePath(root) {
  const configured = process.env.OPENCODE_RESEARCH_GATE
  return configured ? path.resolve(root, configured) : path.join(root, ".project", "EXPERIMENT_GATE.json")
}

function requireExperimentGate(root) {
  const file = gatePath(root)
  if (!existsSync(file)) {
    fail("formal-run", `formal experiment blocked: missing ${file}; register smoke_passed, ledger_registered, and commit first`)
  }

  let gate
  try {
    gate = JSON.parse(readFileSync(file, "utf8"))
  } catch (error) {
    fail("formal-run", `formal experiment blocked: cannot parse ${file} (${error.message})`)
  }

  if (gate?.smoke_passed !== true || gate?.ledger_registered !== true || typeof gate?.commit !== "string" || gate.commit.trim() === "") {
    fail("formal-run", `formal experiment blocked: ${file} must confirm smoke_passed=true, ledger_registered=true, and a non-empty commit`)
  }
}

export const ResearchGuard = async ({ directory, worktree }) => {
  const projectRoot = worktree || directory

  return {
    "tool.execute.before": async (input, output) => {
      const tool = input?.tool || ""
      const args = output?.args || {}
      const text = asText(args)
      const command = typeof args.command === "string" ? args.command : ""
      const target = targetPath(args)

      if (tool === "bash") {
        if (DESTRUCTIVE_COMMAND.test(command)) {
          fail("destructive", "destructive command reached execution; use an explicit user-approved path outside the agent boundary")
        }
        if (SECRET_READ_COMMAND.test(command)) {
          fail("secret", "command appears to read environment files, credentials, private keys, or cookies")
        }
        if (FORMAL_RUN_COMMAND.test(command)) {
          requireExperimentGate(projectRoot)
        }
      }

      if (["read", "edit", "write", "apply_patch"].includes(tool) && target && SENSITIVE_PATH.test(target) && !/\.env\.example$/i.test(target)) {
        fail("secret", `sensitive path is protected: ${target}`)
      }

      if (["edit", "write", "apply_patch"].includes(tool) && SECRET_CONTENT.test(text)) {
        fail("secret", "possible credential or private key detected in file content")
      }
    },
  }
}
