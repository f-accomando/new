# Scaffold Workflow Setup Prompt for Claude Code

> Instructions for Claude Code: Read this entire file carefully before taking any action. Then execute the setup steps in the exact sequence described below.

---

## 1. Purpose and How to Use This File

This file provides an automated, non-destructive procedure for Claude Code to configure a complete, neutral, AI-assisted development workflow in any repository (new or existing).

The workflow enforces context-aware engineering principles: separating deciding (high-level reasoning) from executing (code generation), surgical targeted information retrieval instead of full-file reads, positive instruction rules, verified Work Orders with a 5-point Readiness Gate, multi-agent role routing, and audit scripts that verify documentation, CI, and cross-file consistency.

**Core Instruction**: Read this prompt completely. Perform an initial read-only pre-scan of the repository workspace first. Present the initial configuration questions, git status, and any file conflicts to the user in a **single consolidated message** (one single turn). Resolve conflicts using non-destructive defaults, download the toolkit files from the public repository, adapt project placeholders on newly created files, and execute the verification suite.

---

## 2. Repository Pre-Scan and Consolidated Questions

**Execution Rule**: BEFORE creating or modifying any file, and BEFORE asking the user any questions, Claude must perform a read-only inspection of the repository workspace:
1. Check if the directory is a git repository (does `.git` exist?).
2. If it is a git repository, inspect `git status` to see if there are uncommitted changes or unstaged edits.
3. Check which target paths from Table 3 already exist in the repository (e.g., `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.claude/`, `.github/workflows/ci.yml`, `.gitignore`, `docs/`, `scripts/`, `tools/`, `SYNC.md`).

Claude then consolidates all findings and questions into a **single, consolidated message in one turn**:
- If not a git repository: state that git is not initialized and propose running `git init`.
- If git repository has uncommitted changes: advise the user to commit (`git commit`) or stash (`git stash`) changes before proceeding, ensuring a clean baseline.
- If pre-existing files exist: present the conflict summary and recommended non-destructive resolution for each (see Section 2b).
- Present the initial configuration questions (questions 1–7 below).

### Initial Configuration Questions

1. **Project Name**: What is the name of your project? (e.g., `MyProject` or `Taskly`)
2. **Short Description**: In 1–2 sentences, what does this project do and what is its core purpose?
3. **Language and Stack**: What programming languages, frameworks, and runtimes does the project use? (e.g., Python 3.12, Node.js / React, Go, Rust)
4. **Main Branch**: What is the default git branch name? (e.g., `main` or `master`)
5. **Build Command**: What exact command builds or checks the project? (e.g., `npm run build`, `make all`, `cargo build`, or `-` if interpreted/no build step)
6. **Test Command**: What exact command runs the test suite or unit tests? (e.g., `pytest`, `npm test`, `cargo test`, `python -m unittest`, or `-` if none yet)
7. **Concurrent Multi-Agent / Multi-Operator**: Will more than one agent or person work on this project at the same time? (default: `no`)
   - If `no` (default): The multi-operator synchronization subsystem is omitted. Skip copying `SYNC.md`, `sync/*` (`sync/_template.md`, `sync/operators.toml`, `sync/inbox/README.md`), `docs/progress/sync.md`, and `tools/sync_*.py` (`tools/sync_check.py`, `tools/sync_hdr.py`, `tools/sync_watch.py`).
   - If `yes`: Copy `SYNC.md`, `sync/*`, `docs/progress/sync.md`, and `tools/sync_*.py`. Configure the sync protocol and create a dedicated sync branch `sync/<project-name>` (Scaffold Guide Chapter 14, Step 9: `git branch sync/<project-name>`), never committing sync protocol state directly to the main branch.

Wait for the user's single consolidated response before writing any files.

---

## 2b. Handling Pre-existing Paths (Non-Destructive Conflict Protocol)

**Binding Rule**: Never overwrite, delete, or move an existing user file without explicit, informed confirmation.

When pre-existing files are detected during the pre-scan:
1. Read the existing file in the user's workspace.
2. Prepare a 3-line summary showing what the existing file contains.
3. In the initial consolidated message, propose ONE of the following options for each conflicting path:
   - **Option (a) - Section-by-Section Merge**: Keep the user's file and append missing template sections in a dedicated block. For `CLAUDE.md` and `AGENTS.md`, preserve all user instructions and add workflow sections that do not contradict them. Recommended default for `.gitignore`.
   - **Option (b) - Side-by-Side Reference (`.scaffold`)**: Keep the user's file completely untouched and write the scaffold template file alongside it with a `.scaffold` extension (e.g., `CLAUDE.md.scaffold`, `ci.yml.scaffold`). **Recommended default for `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.github/workflows/ci.yml`, and any existing files inside `docs/`, `scripts/`, `tools/`, and `.claude/`**.
   - **Option (c) - Backup and Replace**: Save an exact copy of the user's file into `.scaffold-backup/<YYYY-MM-DD-HHMMSS>/<path>` and replace the file with the template version. Only choose this with the user's explicit written approval.
4. **Existing Folders (`docs/`, `scripts/`, `tools/`, `.claude/`)**: Process conflicts file-by-file, never at the directory level. Never wipe or overwrite an existing directory.
5. **Existing Subagents in `.claude/agents/`**: If subagent files with matching names already exist, keep the user's versions intact and write template versions as `<name>.md.scaffold` (Option b).

Wait for the user's confirmation on conflicting paths before writing any files.

---

## 2c. Execution Summary and Reversibility

Once files have been written:
1. Output a clear summary table listing:
   - Files created fresh from template
   - Files merged with existing user files (Option a)
   - Files saved alongside as `<name>.scaffold` (Option b)
   - Files backed up into `.scaffold-backup/` (Option c)
2. Provide explicit undo instructions:
   - To review changes: `git status` or `git diff`
   - To revert created files: list the specific files created and delete them individually (e.g., `rm <path>` on Linux/macOS or `Remove-Item <path>` on PowerShell). **Never run `git clean -f`**, to prevent accidental deletion of untracked user files.
   - To restore modified files: `git checkout -- <paths>`
3. **No Automatic Commits**: Do not run `git commit` automatically. Leave all new files in the working directory for the user to review and commit.

---

## 3. Tree of Files to Create

The complete scaffold toolkit comprises 42 files across 8 areas.

| # | Path | Purpose | Primary Writer / Maintainer |
|---|---|---|---|
| 1 | `CLAUDE.md` | Always-loaded session briefing: targeted retrieval, rules of engagement, routing, closure checklist | Claude Code / Agents |
| 2 | `AGENTS.md` | Agent specifications, routing rules, Readiness Gate, and Work Order structure | Orchestrator / Agents |
| 3 | `GEMINI.md` | Session notes for Google Antigravity / Gemini: model mapping, branch naming rules | Antigravity / Gemini Agents |
| 4 | `.claude/agents/planner.md` | Planner subagent: turns vague tasks into verified Work Orders; writes no code | Orchestrator |
| 5 | `.claude/agents/coder.md` | Coder subagent: writes code exclusively from a precise Work Order | Planner / Orchestrator |
| 6 | `.claude/agents/mechanic.md` | Mechanic subagent: atomic, zero-risk edits (formatting, rename, progress ticks) | Planner / Orchestrator |
| 7 | `.claude/agents/light.md` | Light subagent: small fixes with judgment, verified docs against code, 1-2 files | Planner / Orchestrator |
| 8 | `.claude/agents/deep.md` | Deep subagent: tackles one isolated critical problem with reproduction | Planner / Orchestrator |
| 9 | `.claude/agents/research.md` | Research subagent: read-only symbol inspection and call flows across files | Orchestrator / Agents |
| 10 | `.claude/agents/ops.md` | Ops subagent: runs pre-decided shell commands and reports PASS/FAIL | Planner / Orchestrator |
| 11 | `.claude/skills/docs-loop/SKILL.md` | Skill: iterative documentation optimization loop (measure, keep or discard) | Claude Code / Agents |
| 12 | `.claude/skills/docs-map/SKILL.md` | Skill: repository documentation map and surgical retrieval guide | Claude Code / Agents |
| 13 | `.claude/skills/work-order/SKILL.md` | Skill: Work Order template generator and Readiness Gate validator | Planner / Claude Code |
| 14 | `SYNC.md` | Multi-operator sync protocol template: roles, file split, deliveries, log | Supervisor (SPV) |
| 15 | `sync/_template.md` | Template for operator status and heartbeat files (`sync/<ID>.md`) | Operator onboarding |
| 16 | `sync/operators.toml` | Registry of active operators, assigned branches, roles, and models | Supervisor (SPV) |
| 17 | `sync/inbox/README.md` | Operator task inbox conventions and documentation (`sync/inbox/<ID>.md`) | Supervisor / Operators |
| 18 | `docs/WORKFLOW.md` | One-page summary and reference index of the entire scaffold workflow | Maintainer / Agents |
| 19 | `docs/ROADMAP.md` | Roadmap grouped into levels, rows with ID, Pri, Status, Goal, Requirement, After | Maintainer / Planner |
| 20 | `docs/open-decisions.md` | Pending architectural and product decisions awaiting owner resolution | Maintainer / Planner |
| 21 | `docs/progress.md` | Single entry-point index of project progress, area sheets table, active milestones | Main Agent / Maintainer |
| 22 | `docs/progress/core.md` | Template area sheet: How it is today, Open work, Rules (do not break) | Area owners / Agents |
| 23 | `docs/progress/sync.md` | Area sheet for the multi-operator sync subsystem, protocol state, and rules | SPV / Operators |
| 24 | `docs/spec/CONSISTENCY.md` | Documentation for the specification and cross-file consistency subsystem | Maintainer / Agents |
| 25 | `docs/spec/config-keys.toml` | Registry of configuration keys read by code: scope, values, default, meaning | Maintainer / Agents |
| 26 | `docs/spec/divergences.toml` | Registry of known differences across platforms/clients: cause and status | Maintainer / Agents |
| 27 | `docs/spec/known.toml` | Registry of accepted temporary drift findings with kind, ID, and reason | Maintainer / Agents |
| 28 | `docs/spec/platforms.toml` | Registry of target platforms and actual hardware/runtime capability differences | Maintainer / Agents |
| 29 | `docs/spec/specs.toml` | Specification item registry: ID, since revision, status, file locations | Maintainer / Agents |
| 30 | `docs/agents/ledger.txt` | Append-only ledger of subagent runs (date, agent, model, task, gate, metrics) | Main Agent / Orchestrator |
| 31 | `scripts/agent_audit.py` | Audit script: analyzes ledger.txt, reports success rates, median metrics, gate calibration | CLI / CI / Maintainer |
| 32 | `scripts/ci_audit.py` | Audit script: inspects CI workflow for timeouts, concurrency, branch filters, wait bounds | CLI / CI / Maintainer |
| 33 | `scripts/consistency.py` | Audit script: checks code against spec registries and reports cross-file drift / release gate | CLI / CI / Maintainer |
| 34 | `scripts/docs_audit.py` | Audit script: computes docs health score, checks orphans/broken links, tracks repeat commands | CLI / CI / Maintainer |
| 35 | `scripts/selftest.py` | Test runner: runs all audit scripts on test fixtures and verifies mutation detection | CLI / CI / Maintainer |
| 36 | `tools/sync_check.py` | Monitoring tool: checks heartbeat timestamps, ETAs, unread messages, format anomalies | Supervisor (SPV) / CI |
| 37 | `tools/sync_hdr.py` | Header update tool: writes ISO 8601 status block in sync/<ID>.md and commits/pushes | Operators / Automation |
| 38 | `tools/sync_watch.py` | Background watcher daemon: monitors inbox changes and manages automatic heartbeats | Operator background daemon |
| 39 | `.github/workflows/ci.yml` | GitHub Actions CI workflow template with concurrency, timeouts, and ignored branches | CI maintainer |
| 40 | `.ci-audit.toml` | Configuration for ci_audit.py (workflow file, test globs, required runs, expected wait timeouts) | User / CI maintainer |
| 41 | `.gitignore` | Standard git ignore patterns for python, editor artifacts, temporary sync files | User / Maintainer |
| 42 | `examples/demo/` | Minimal demo fixture project: sample files for audit selftests (copy it if you want to run selftest) | Automated test fixture |

*Excluded from installation*: `video/`, `examples/` (except `examples/demo/` if selftest is desired), `.claude/skills/explainer-video/`, `scripts/build_workflow_pdf.py` (documentation builder script requiring ReportLab, specific to generating the guide PDF and not part of the project runtime toolkit), and `.pdf` files.

---

## 4. Downloading and Adapting Files

### Source Repository Configuration

```bash
SCAFFOLD_REPO="https://github.com/f-accomando/scaffold"
SCAFFOLD_REF="main"
```

### Download Procedure

1. Create a clean temporary directory outside the project (e.g., `<temp-dir>/scaffold-download`).
2. Clone the repository at the specified reference:
   ```bash
   git clone --depth 1 --branch "$SCAFFOLD_REF" "$SCAFFOLD_REPO" "<temp-dir>/scaffold-download"
   ```
   *Alternative without git*: Fetch individual raw files using:
   ```bash
   curl -fsSL "https://raw.githubusercontent.com/f-accomando/scaffold/$SCAFFOLD_REF/<path>" -o "<target-path>"
   ```
3. Copy the files listed in Table 3 to their designated relative paths in the workspace (include `examples/demo/` if running `scripts/selftest.py`). Never copy the `.git/` folder from the scaffold clone.

### File Adaptation Rules

**Binding Rule on Substitutions**:
- Placeholder substitutions apply **ONLY** to newly created template files written from the scaffold repository.
- Never apply substitutions to existing user files merged via Option (a) or to side-by-side `.scaffold` copies.

#### Distinguishing Placeholders: Real Project Configuration vs Generic Examples

1. **Real Project Configuration Placeholders** (replace these with user answers from Section 2):
   - `<PROJECT>`: Replaced with the project name.
   - `<main-branch>`: Replaced with the default git branch name (e.g., `main` or `master`).
   - `<build-cmd>`: Replaced with the project build/check command (or `-` if none).
   - `<test-cmd>`: Replaced with the project test runner command (or `-` if none).
   - *If multi-operator sync is enabled*:
     - `{name}` / `{owner/repo}`: Replaced with the project repository name / GitHub path.
     - `<sync-branch>`: Replaced with the sync branch name (e.g., `sync/<project-name>`).
     - `{supervisor}`: Replaced with the supervisor operator ID.
     - `{date}`: Replaced with the current setup date (ISO 8601).

2. **Generic Examples, Command Syntax, and Runtime Log Placeholders** (**DO NOT REPLACE**):
   - In `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and `.claude/agents/*.md`: placeholders such as `<area>`, `<file>`, `<symbol>`, `<name>`, `<branch>`, `<descriptive-name>`, `<ID>`, `<detail>`, `<reason>`, `<placeholder>` are command-line parameter examples (e.g., `grep -n -C 2 '<symbol>' docs/api/<area>.md` or `git checkout -b feat/<name>`). Do not replace them.
   - In `.claude/skills/*` (`docs-loop`, `docs-map`, `work-order`): placeholders such as `<area>`, `<name>`, `<score>`, `<theme>`, `<what>`, `<file>`, `<symbol>`, `<reason>` represent runtime skill inputs. Do not replace them.
   - In `SYNC.md` and `sync/`: log format tokens such as `{branch}`, `{command}`, `{commit}`, `{ISO}`, `{result}`, `{WO-ID}`, `{task}`, `{who}`, `{topic-a}`, `{topic-b}`, `{note}` are delivery and event schema definitions for future entries. Do not replace them.

#### Detailed File Adaptation Instructions

| File | Placeholders to Replace | Adaptation Instructions |
|---|---|---|
| `CLAUDE.md` | `<PROJECT>`, `<main-branch>`, `<build-cmd>`, `<test-cmd>` | Replace header with project name. Set main branch, build command, and test command. In Section 1 quick-lookup table, remove rows for unused tools. Keep positive instruction rules. Preserve all generic command syntax examples (`<area>`, `<file>`, `<symbol>`, `<name>`, `<branch>`, `<descriptive-name>`, `<ID>`, `<placeholder>`). |
| `AGENTS.md` | `<PROJECT>` | Replace `<PROJECT>` with project name. Keep `<reason>` as generic placeholder in Work Order template. Ensure role table and Readiness Gate match project architecture. |
| `GEMINI.md` | `<PROJECT>`, `<main-branch>`, `<build-cmd>`, `<test-cmd>` | Replace `<PROJECT>`, stack summary, build command, and test command. Preserve command parameter examples (`<area>`, `<file>`, `<symbol>`, `<name>`, `<branch>`, `<reason>`). |
| `.claude/agents/*.md` | `<PROJECT>`, `<test-cmd>` (light), `<build-cmd>` (ops) | In `.claude/agents/coder.md`, `deep.md`, `light.md`, `mechanic.md`, `ops.md`, `planner.md`, `research.md`, replace `<PROJECT>` with project name. Set `<test-cmd>` in `light.md` and `<build-cmd>` in `ops.md`. Preserve generic syntax placeholders (`<detail>`, `<reason>`, `<name>`, `<ID>`, `<branch>`). |
| `.claude/skills/work-order/SKILL.md` | `<test-cmd>` | Replace `<test-cmd>` with project test command. Preserve `<reason>`. |
| `SYNC.md` (if sync enabled) | `{name}`, `{owner/repo}`, `<main-branch>`, `<sync-branch>`, `{supervisor}`, `{date}` | Replace repository name, owner/repo, default branch, sync branch, supervisor ID, and date. Preserve all runtime event tokens (`{branch}`, `{command}`, `{commit}`, `{file}`, `{ID}`, `{ISO}`, `{note}`, `{place}`, `{placeholders}`, `{reason}`, `{result}`, `{task}`, `{topic-a}`, `{topic-b}`, `{who}`, `{WO-ID}`). |
| `docs/WORKFLOW.md` | `<PROJECT>`, `<build-cmd>`, `<test-cmd>` | Replace `<PROJECT>`, `<build-cmd>`, and `<test-cmd>`. Preserve `<area>` and `<name>`. |
| `docs/ROADMAP.md` | `<build-cmd>`, `<test-cmd>` | Replace `<build-cmd>` and `<test-cmd>` in initial milestone level 1 row (see Guide 14.4 below). |
| `docs/progress.md` | `<PROJECT>` | Replace `<PROJECT>` with project name. Set up the initial area table with at least one core area sheet. |
| `docs/progress/core.md` | (None) | Populate with real project module state (see Guide 14.3 below). Copy or rename for additional areas as needed. |
| `.ci-audit.toml` | (None) | Set `required_run` to include `python scripts/selftest.py` and the project test command. |
| `.github/workflows/ci.yml` | (None) | Ensure branch ignore includes `sync/**` and every job defines `timeout-minutes`. |
| `.gitignore` | (None) | If merging with existing `.gitignore`, append missing scaffold rules (`.scaffold-backup/`, `*.scaffold`, `__pycache__/`). |

#### Operational Guidance from Guide Chapters (Bootstrapping Step-by-Step)

1. **Populate Area Sheet (`docs/progress/core.md`, Guide 14.3)**:
   - `## How it is today`: Provide a 2–4 sentence factual description of the core module's architecture, entry points, and current implementation state.
   - `## Open work`: List 2–4 immediate, actionable tasks or technical debt items to tackle next.
   - `## Rules (do not break)`: Formulate 2–3 positive, binding constraints (invariants, API conventions, file scopes) that an AI agent cannot guess by reading code alone.

2. **Initialize Roadmap (`docs/ROADMAP.md`, Guide 14.4)**:
   - Provide at least one initial level 1 row:
     `| 1.1 | 1 | OPEN | Initialize project test and build suite | Build: <build-cmd>, Test: <test-cmd> | Setup clean CI pipeline | - |`

3. **Specification and Cross-File Consistency (`docs/spec/`, Guide 14.5)**:
   - Note that `docs/spec/consistency.toml` is not in the base template; the template provides modular TOML registries (`config-keys.toml`, `specs.toml`, `platforms.toml`, `divergences.toml`, `known.toml`).
   - If cross-file multi-fact verification is needed, create `docs/spec/consistency.toml` following Guide 14.5 with `[[match]]` blocks (for facts living across multiple files), a `[config]` block (for code config scanning), and a `[spec]` revision constant.
   - `scripts/consistency.py check` functions cleanly and verifies the existing spec registries even without `consistency.toml`.

4. **Executing the First Real Task (Guide 14.8)**:
   - To validate the workflow in practice, describe one real task vaguely to `planner` (e.g., "Add pagination to list endpoint" or "Add validation helper").
   - `planner` produces one or more Work Orders.
   - Validate each Work Order with the 5-point Readiness Gate (`.claude/skills/work-order/SKILL.md`): files named, deterministic diff, verifiable test command, <= 3 files, zero pending decisions.
   - Pass the verified order to `coder` (or `light` for small 1–2 file tasks).
   - Verify execution with the test command.
   - Apply the closure checklist (`CLAUDE.md` Section 5): update `Open work` and `Rules` in `docs/progress/core.md`, verify `python scripts/docs_audit.py score`, and append a run row to `docs/agents/ledger.txt`.

### Python Scripts and Tools Specification

Copy `scripts/*.py` and `tools/*.py` directly without code alterations. These scripts require Python 3.11+ and zero external dependencies:

1. **`scripts/agent_audit.py`**:
   - *Purpose*: Analyzes `docs/agents/ledger.txt` and reports run outcomes (%DONE, %BLOCKED, %FAILED), median token/time consumption, gate calibration, and flags expensive model overuse at low necessity (<=3).
   - *Usage*: `python scripts/agent_audit.py [--root DIR] [--ledger PATH] [--baseline PATH]`
   - *Exit code*: `0` = healthy; `1` = malformed ledger row or audit findings; `2` = usage error.
2. **`scripts/ci_audit.py`**:
   - *Purpose*: Lints GitHub Actions CI workflows for mandatory timeouts on all jobs, concurrency blocks, ignored sync branches (`sync/**`), and verified wait bounds against `.ci-audit.toml`.
   - *Usage*: `python scripts/ci_audit.py [--root DIR] [--workflow PATH] [--gh]`
   - *Exit code*: `0` = compliant; `1` = rule violation; `2` = usage error.
3. **`scripts/consistency.py`**:
   - *Purpose*: Compares code against specification registries in `docs/spec/`. `check` catches route/config drift; `gate` blocks release if open defect divergences exist.
   - *Usage*: `python scripts/consistency.py check [--root DIR]` or `python scripts/consistency.py gate [--root DIR]`
   - *Exit code*: `0` = clean / release ready; `1` = drift or release blockers; `2` = usage error.
4. **`scripts/docs_audit.py`**:
   - *Purpose*: Calculates docs health score (`always_loaded + mean_area + penalties`), checks for broken links, orphan area sheets, oversize documents, and identifies repeated prompts/commands for skill extraction.
   - *Usage*: `python scripts/docs_audit.py score [--root DIR] [--json]`, `python scripts/docs_audit.py repeats [N]`, `python scripts/docs_audit.py log <score> <keep|discard> "<msg>"`
   - *Exit code*: `0` = zero penalties; `1` = penalties detected; `2` = usage error.
5. **`scripts/selftest.py`**:
   - *Purpose*: Self-test harness for all audit scripts. Runs each audit on fixture data (in `examples/demo/`) and verifies that deliberate mutations trigger expected audit warnings.
   - *Usage*: `python scripts/selftest.py [--root DIR]`
   - *Exit code*: `0` = all 40/40 tests pass; `1` = test failure; `2` = usage error.
6. **`tools/sync_check.py`**:
   - *Purpose*: Sync health validator. Reads `sync/<ID>.md` status headers, flags stale heartbeats, past-ETA tasks, oversized inboxes (>5 lines), or IDLE operators.
   - *Usage*: `python tools/sync_check.py [--root DIR] [--strict]`
   - *Exit code*: `0` = healthy; `1` = protocol issues or IDLE operators; `2` = usage error.
7. **`tools/sync_hdr.py`**:
   - *Purpose*: Manages ISO 8601 status headers in `sync/<ID>.md`. Updates state, active task, ETA, or read receipt (`--ack auto`).
   - *Usage*: `python tools/sync_hdr.py <ID> --state <STATE> --task "<TASK>" --eta <ETA>`, `python tools/sync_hdr.py <ID> --ack auto`
   - *Exit code*: `0` = updated; `1` = file/header error; `2` = usage error.
8. **`tools/sync_watch.py`**:
   - *Purpose*: Non-AI background watcher. Polls the sync branch, detects inbox changes, and sends automatic heartbeats without consuming LLM context.
   - *Usage*: `python tools/sync_watch.py --id <ID> --branch sync/<name> [--every 5] [--beat 15] [--once]`
   - *Exit code*: `0` = clean exit; `1` = runtime error; `2` = usage error.

---

## 5. Verification Suite

Run the following commands in order to verify that the workspace is fully configured, consistent, and healthy:

1. **Verify Self-test** (requires `examples/demo/`):
   ```bash
   python scripts/selftest.py
   ```
   *Expected output*: `selftest: 40/40 checks passed` (exit code 0).
2. **Verify Documentation Health**:
   ```bash
   python scripts/docs_audit.py score
   ```
   *Expected output*: `score <N> (always loaded ... + mean area ... + penalties 0)` with exit code 0 and zero penalties.
3. **Verify Cross-File Consistency**:
   ```bash
   python scripts/consistency.py check
   ```
   *Expected output*: `consistency: 0 drift, 0 accepted, 0 stale` (exit code 0).
4. **Verify Release Gate (No Blocking Divergences)**:
   ```bash
   python scripts/consistency.py gate
   ```
   *Expected output*: `gate: 0 blockers` (exit code 0).
5. **Verify Subagent Ledger Audit**:
   ```bash
   python scripts/agent_audit.py
   ```
   *Expected output*: Audit report showing runs, %DONE, gate calibration, and model usage (exit code 0).
6. **Verify CI Audit** (if `.github/workflows/ci.yml` is present):
   ```bash
   python scripts/ci_audit.py
   ```
   *Expected output*: `ci_audit: 0 problems` (exit code 0).

If any check fails, address the reported penalty, broken link, or configuration mismatch immediately and re-run until all checks exit with code 0.

---

## 6. Daily Workflow, Routine and Metrics (Guide Chapter 15)

After successful verification, report to the user that the scaffold workflow is ready.

### Daily Retrieval and Inspection Commands

1. **Find what to do in an area without reading whole files**:
   ```bash
   grep -n -A 15 '^## Open work' docs/progress/<area>.md
   ```
2. **Consult rules of an area before modifying code**:
   ```bash
   grep -n -A 20 '^## Rules' docs/progress/<area>.md
   ```
3. **Check documentation health and link integrity**:
   ```bash
   python scripts/docs_audit.py score
   ```
4. **Check consistency drift**:
   ```bash
   python scripts/consistency.py check
   ```

### Operational Routine Table (Guide 15.1)

| When | What to Do |
|---|---|
| **Every task** | Closure checklist (`CLAUDE.md` Section 5): update `Open work` and `Rules` in area sheet; run `python scripts/docs_audit.py score`; run `python scripts/consistency.py check` and `python scripts/ci_audit.py` when relevant; append one ledger row in `docs/agents/ledger.txt` for each subagent run. |
| **Every milestone** | Run `docs-loop` optimization rounds (at most 8 iterations); update corresponding row in `docs/ROADMAP.md`; inspect `python scripts/consistency.py gate`; resolve or re-date open divergences. |
| **Every month** | Run `python scripts/agent_audit.py`: review %DONE by gate score; adjust autonomy threshold (start at 4) and Readiness Gate strictness; prune obsolete rules; run `python scripts/ci_audit.py --gh`. |
| **Whenever a script changes** | Run `python scripts/selftest.py`, and add a negative check for the new behavior. |
| **Whenever the workflow changes** | Update `docs/WORKFLOW.md` and project documentation. |

### Health Metrics to Watch (Guide 15.2)

| Metric | Source | Healthy State |
|---|---|---|
| **Docs score and penalties** | `python scripts/docs_audit.py score` | 0 penalties; always-loaded tokens flat or falling |
| **Consistency drift and gate blockers** | `python scripts/consistency.py check`, `gate` | 0 drift; 0 release blockers |
| **%DONE by gate score** | `python scripts/agent_audit.py` | Gate score 1 near 100% DONE; no "gate too optimistic" warning |
| **Expensive model use at low necessity** | `python scripts/agent_audit.py` | No warning; deep/pro subagents invoked only at necessity 4 or 5 |
| **CI duration and success rate** | `python scripts/ci_audit.py --gh` | Stable minutes; no run exceeding its timeout |
| **IDLE operators and unread rows** (sync) | `python tools/sync_check.py` | 0 problems when a sync is active |

### Active Pruning Principles (Guide 15.3)

- **Delete obsolete rules**: When a rule stops being true, delete it. Never write its negation (Guide Section 13).
- **Clear completed items**: Remove finished tasks from `## Open work`. Remove decided questions from `docs/open-decisions.md`.
- **Prune known drift**: Remove `docs/spec/known.toml` entries that `consistency.py check` identifies as stale; resolve or reclassify old `suspended` divergences.
- **Archive finished sync**: When multi-operator sync completes, archive `SYNC.md` in `docs/archive/` on the main branch and delete the `sync/<name>` branch.

---

## 7. Section Correspondence Table

Mapping between the 15 sections of the Scaffold Workflow Guide (`scaffold-workflow-EN.pdf`) and this setup prompt:

| Guide Section | Title in Guide | Corresponding Section in this Prompt |
|---|---|---|
| Section 1 | Why a workflow | Section 1 (Core Purpose & Principles) |
| Section 2 | Repository layout | Section 3 (Table of 42 Files to Create) |
| Section 3 | CLAUDE.md and targeted retrieval | Section 4 (`CLAUDE.md` Adaptation) & Section 6 (Daily Commands) |
| Section 4 | The docs system | Section 3 & 4 (`docs/progress.md`, area sheets, `ROADMAP.md`) |
| Section 5 | Subagent roles and routing | Section 3 & 4 (`.claude/agents/*.md`, `AGENTS.md`, `GEMINI.md`) |
| Section 6 | Readiness Gate | Section 4 (`.claude/skills/work-order/SKILL.md`, `AGENTS.md`) |
| Section 7 | Evidence-based escalation | Section 4 (Subagent closing states `DONE`, `BLOCKED`, `FAILED x2`) |
| Section 8 | Necessity score, autonomy threshold, ledger and agent_audit | Section 3, 4, 5 & 6 (`docs/agents/ledger.txt`, `scripts/agent_audit.py`) |
| Section 9 | Consistency gate: spec files, drift, divergences | Section 3, 4, 5 & 6 (`docs/spec/*`, `scripts/consistency.py`) |
| Section 10 | Docs audit | Section 3, 4, 5 & 6 (`scripts/docs_audit.py`, `docs-loop` skill) |
| Section 11 | CI audit | Section 3, 4, 5 & 6 (`.ci-audit.toml`, `.github/workflows/ci.yml`, `scripts/ci_audit.py`) |
| Section 12 | Multi-operator sync | Section 2, 3, 4 & 6 (`SYNC.md`, `sync/*`, `tools/sync_*.py`) |
| Section 13 | Writing rules as positive instructions | Section 1, 2b, 4 & 6 (Positive instruction rules, retirement by deletion) |
| Section 14 | Bootstrapping step by step | Sections 2, 2b, 2c, 4, 5 (The automated bootstrap procedure) |
| Section 15 | Maintenance and metrics | Section 5 (Verification Suite) & Section 6 (Daily Routine and Metrics) |
