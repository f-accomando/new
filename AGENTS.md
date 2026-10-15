# <PROJECT> — Agent Specifications and Routing

Governance, routing and operating constraints for every AI agent working on this repository. It mirrors
[`CLAUDE.md`](CLAUDE.md) section 3 for tools that read `AGENTS.md`; when the two differ, `CLAUDE.md` wins.

---

## 1. The principle: separate deciding from executing

- **Top-tier models**: high cost on output tokens, excellent at reasoning. They produce **few tokens**: decisions, schemas, concise Work Orders. **They do not write code.**
- **Fast, cheap models**: produce **many tokens**: implementation, constrained refactoring, rename, formatting. They receive locked-down specs and execute.
- **Router rule**: the agent depends on how rigorously the task is already specified, not on its apparent size.

---

## 2. Role table

| Agent | Claude engine | Gemini engine | Toolset | Primary responsibility | Absolute limits |
|---|---|---|---|---|---|
| **`planner`** | Opus medium | Pro | Read-only | Turns vague tasks into verifiable Work Orders | Writes no code |
| **`coder`** | Haiku high | Flash | Full | Writes code from a precise Work Order | No design, no open choices |
| **`mechanic`** | Haiku low | Flash-Lite | Full (atomic) | Rename, formatting, templates, ticks in `docs/progress/` | Zero decisions |
| **`light`** | Sonnet medium | Flash | Full | Judgment tasks, docs checked against the code, 1-2 file fixes | No long or vague tasks |
| **`deep`** | Opus xhigh | Pro | Full | One isolated critical problem with certain reproduction | Refuses tasks without reproduction |
| **`research`** | Haiku low | research subagent | Read-only | Symbol search, call flow across files, 5-10 line summaries | Touches no file |
| **`ops`** | Haiku low | Flash-Lite | Bash only | Already-decided shell commands, summarised in a few lines | Decides nothing, kills nothing |

---

## 3. The Readiness Gate

Before handing a task to `mechanic`, `coder` or `light`:

1. [ ] **Files and functions** to touch are named.
2. [ ] **Determinism**: two developers would write the same diff.
3. [ ] **Deterministic verification**: a command with an expected output exists.
4. [ ] **Contained scope**: 3 files or fewer.
5. [ ] **Zero pending dependencies**: no decision is still to be made.

- **5 out of 5 YES**: READY, assign it to `mechanic`, `coder` or `light`.
- **At least one NO**: NOT READY, assign it to `planner` to make it ready or split it.
- `deep` receives only an isolated bug with reproduction (section 4).

---

## 4. Binding rules for `deep`

`deep` works only on a tight problem statement with: a documented symptom; an exact reproduction (failing command or test); an isolated suspected area; the attempts already made (for example `FAILED x2`). Otherwise it replies `REJECTED` and the task goes back to `planner`.

---

## 5. Closure and escalation

- **`DONE`**: the verification command passed; a concise diff summary follows.
- **`BLOCKED: <reason>`**: ambiguous specification or missing decision; back to `planner`.
- **`FAILED x2`**: two failed attempts; the task moves up one level.

Every finished subagent run is logged in `docs/agents/ledger.txt` (one row, append only).

---

## 6. Standard Work Order format

```markdown
### WORK ORDER: [ID]
- **Objective**: [one clear sentence]
- **Files/functions to touch**: [exact paths and symbols]
- **Required change**: [unambiguous detail, no open design choice]
- **Verification command**: [command and expected return code or output]
- **Expected result**: [exit 0 / specific output]
- **Assigned agent**: [mechanic | coder | light]
```
