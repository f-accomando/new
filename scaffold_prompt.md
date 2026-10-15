# Scaffold Workflow Setup Prompt for Claude Code

> Instructions for Claude Code: Read this entire file carefully before taking any action. Then execute the setup steps in the exact sequence described below.

---

## 1. Purpose and How to Use This File

This file provides an automated, non-destructive procedure for Claude Code to configure a complete, neutral, AI-assisted development workflow in any repository (new or existing).

The workflow enforces context-aware engineering principles: separating deciding (high-level reasoning) from executing (code generation), surgical targeted information retrieval instead of full-file reads, positive instruction rules, verified Work Orders with a 5-point Readiness Gate, multi-agent role routing, and audit scripts that verify documentation, CI, and cross-file consistency.

**Core Instruction**: Read this prompt completely, ask the user the initial configuration questions in a single turn, inspect the repository state, resolve any file conflicts with non-destructive defaults, download the toolkit files from the public repository, adapt the placeholders to the user's project, and execute the verification suite.

---

## 2. Initial Questions to the User

Before creating or editing any file, ask the user the following six questions in a **single, consolidated message**:

1. **Project Name**: What is the name of your project? (e.g., `MyProject` or `Taskly`)
2. **Short Description**: In 1–2 sentences, what does this project do and what is its core purpose?
3. **Language and Stack**: What programming languages, frameworks, and runtimes does the project use? (e.g., Python 3.12, Node.js / React, Go, Rust)
4. **Main Branch**: What is the default git branch name? (e.g., `main` or `master`)
5. **Build Command**: What exact command builds or checks the project? (e.g., `npm run build`, `make all`, `cargo build`, or `-` if interpreted/no build step)
6. **Test Command**: What exact command runs the test suite or unit tests? (e.g., `pytest`, `npm test`, `cargo test`, `python -m unittest`, or `-` if none yet)

Wait for the user's response before proceeding to project inspection.

---

## 2b. Checking an Existing Project

Before writing or modifying any file in the workspace:

1. **Inspect Git Working Tree**: Run `git status`. If the working tree has uncommitted changes or unstaged edits, ask the user to commit (`git commit`) or stash (`git stash`) them first before proceeding, ensuring a clean baseline.
2. **Scan for Pre-existing Files**: Check if any of the target paths from Table 3 already exist in the repository (e.g., `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.claude/`, `.github/workflows/ci.yml`, `.gitignore`, `docs/`, `scripts/`, `tools/`, `SYNC.md`).
3. **Determine Path**:
   - If **none** of the target paths exist, proceed directly as a clean new project installation.
   - If **one or more** target paths exist, follow the conflict resolution protocol in Section 2c.

---

## 2c. Handling Existing Paths (Non-Destructive Conflict Protocol)

**Binding Rule**: Never overwrite, delete, or move an existing user file without explicit, informed confirmation.

For each conflicting file path:
1. Read the existing file in the user's workspace.
2. Prepare a 3-line summary showing what the existing file contains.
3. Present the conflicts to the user in a **single message** containing all conflicting files, recommending ONE of the following options for each:
   - **Option (a) - Section-by-Section Merge**: Keep the user's file and append missing template sections in a dedicated block or at the end. For `CLAUDE.md` and `AGENTS.md`, preserve all user instructions and add workflow sections that do not contradict them; highlight any direct contradictions for user decision. Recommended default for `.gitignore`.
   - **Option (b) - Side-by-Side Reference (`.scaffold`)**: Keep the user's file completely untouched and write the scaffold template file alongside it with a `.scaffold` extension (e.g., `CLAUDE.md.scaffold`, `ci.yml.scaffold`) so the user can inspect or merge at their convenience. Recommended default for `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and `.github/workflows/ci.yml`.
   - **Option (c) - Backup and Replace**: Save an exact copy of the user's file into `.scaffold-backup/<YYYY-MM-DD-HHMMSS>/<path>` and replace the file with the template version. Only choose this with the user's explicit written approval.
4. **Existing Folders (`docs/`, `scripts/`, `tools/`)**: Process conflicts file-by-file, never at the directory level. Never wipe or overwrite an existing directory.
5. **Existing Subagents or Settings in `.claude/`**: If `.claude/settings.json` or subagent files with matching names already exist, keep the user's versions intact and append or provide side-by-side versions.

Wait for the user's confirmation on conflicting paths before writing any files.

---

## 2d. Execution Summary and Reversibility

Once files have been written:
1. Output a clear summary table listing:
   - Files created fresh from template
   - Files merged with existing user files (Option a)
   - Files saved alongside as `<name>.scaffold` (Option b)
   - Files backed up into `.scaffold-backup/` (Option c)
2. Provide explicit undo instructions:
   - To review changes: `git status` or `git diff`
   - To revert created files: `git clean -f <paths>`
   - To restore modified files: `git checkout -- <paths>`
3. **No Automatic Commits**: Do not run `git commit` automatically. Leave all new files in the working directory for the user to review and commit.

---

## 3. Tree of Files to Create

The complete scaffold toolkit comprises 41 files across 7 areas.

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

*Excluded from installation*: `video/`, `examples/`, `.claude/skills/explainer-video/`, and `.pdf` files.

---

## 4. Downloading and Adapting Files

### Source Repository Configuration

```bash
SCAFFOLD_REPO="https://github.com/f-accomando/scaffold"
SCAFFOLD_REF="claude/workflow-template"
# Note: when PR 1 is merged into main, change SCAFFOLD_REF to "main"
```

### Download Procedure

1. Create a clean temporary directory outside the project (e.g., `<temp-dir>/scaffold-download`).
2. Clone the repository at the specified reference:
   ```bash
   git clone --depth 1 --branch "$SCAFFOLD_REF" "$SCAFFOLD_REPO" "<temp-dir>/scaffold-download"
   ```
   *Alternative without git*: Fetch individual raw files using `curl -fsSL "https://raw.githubusercontent.com/f-accomando/scaffold/$SCAFFOLD_REF/<path>" -o "<target-path>"`.
3. Copy ONLY the 41 files listed in Table 3 to their designated relative paths in the workspace. Never copy the `.git/` folder from the scaffold clone.

### File Adaptation Rules

After copying, customize each file by replacing placeholders with the answers gathered in Section 2:

| File | Placeholders to Replace | Adaptation Instructions |
|---|---|---|
| `CLAUDE.md` | `<PROJECT>`, `<main-branch>`, `<build-cmd>`, `<test-cmd>`, `<area>`, `<branch>`, `<file>`, `<symbol>`, `<name>`, `<placeholder>` | Replace header with project name. Set main branch, build command, and test command. In Section 1 quick-lookup table, remove rows for unused tools. Keep positive instruction rules. |
| `AGENTS.md` | `<PROJECT>`, `<reason>` | Replace `<PROJECT>` with project name. Ensure role table and Readiness Gate match project architecture. |
| `GEMINI.md` | `<PROJECT>`, `<main-branch>`, `<build-cmd>`, `<test-cmd>`, `<area>`, `<file>`, `<symbol>` | Replace `<PROJECT>`, stack summary, build command, and test command. |
| `.claude/agents/coder.md` | `<PROJECT>`, `<detail>`, `<reason>` | Replace `<PROJECT>` with project name. |
| `.claude/agents/deep.md` | `<PROJECT>` | Replace `<PROJECT>` with project name. |
| `.claude/agents/light.md` | `<PROJECT>`, `<name>`, `<reason>`, `<test-cmd>` | Replace `<PROJECT>` with project name and `<test-cmd>` with project test command. |
| `.claude/agents/mechanic.md` | `<PROJECT>`, `<area>`, `<reason>` | Replace `<PROJECT>` with project name. |
| `.claude/agents/ops.md` | `<PROJECT>`, `<ID>`, `<branch>`, `<build-cmd>` | Replace `<PROJECT>` with project name and `<build-cmd>` with project build command. |
| `.claude/agents/planner.md` | `<PROJECT>` | Replace `<PROJECT>` with project name. |
| `.claude/agents/research.md` | `<PROJECT>` | Replace `<PROJECT>` with project name. |
| `.claude/skills/work-order/SKILL.md` | `<test-cmd>`, `<reason>` | Replace `<test-cmd>` with project test command. |
| `SYNC.md` | `{name}`, `{owner/repo}`, `<main-branch>`, `<ID>`, `<name>`, `<base>`, `<commit>` | Replace template placeholders with project repository name, owner/repo, and main branch name. |
| `docs/WORKFLOW.md` | `<PROJECT>`, `<area>`, `<build-cmd>`, `<test-cmd>`, `<name>` | Replace `<PROJECT>`, `<build-cmd>`, and `<test-cmd>` with project values. |
| `docs/ROADMAP.md` | `<area>`, `<build-cmd>`, `<test-cmd>`, `<n>` | Replace `<build-cmd>` and `<test-cmd>` in initial milestone level 1 row. |
| `docs/progress.md` | `<PROJECT>` | Replace `<PROJECT>` with project name. Adjust initial area table to match user's architecture. |
| `docs/progress/core.md` | `<area>` | Rename or copy for the project's primary module/area (e.g., `docs/progress/core.md` or `docs/progress/server.md`). |
| `.ci-audit.toml` | (None) | Set `required_run` to include `python scripts/selftest.py` and the project test command. |
| `.github/workflows/ci.yml` | (None) | Ensure branch ignore includes `sync/**` and every job defines `timeout-minutes`. |
| `.gitignore` | (None) | If merging with existing `.gitignore`, append missing scaffold rules (`.scaffold-backup/`, `*.scaffold`, `__pycache__/`). |

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
   - *Purpose*: Self-test harness for all audit scripts. Runs each audit on fixture data and verifies that deliberate mutations trigger expected audit warnings.
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

Run the following commands in order to verify that the workspace is fully configured and healthy:

1. **Verify Self-test**:
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
4. **Verify CI Audit** (if `.github/workflows/ci.yml` is present):
   ```bash
   python scripts/ci_audit.py
   ```
   *Expected output*: `ci_audit: 0 problems` (exit code 0).

If any check fails, address the reported penalty, broken link, or configuration mismatch immediately and re-run until all checks exit with code 0.

---

## 6. First Session Guide: Daily Workflow

After successful verification, report to the user that the scaffold workflow is ready and provide these three daily commands to start working:

1. **Find what to do in an area without reading whole files**:
   ```bash
   grep -n -A 15 '^## Open work' docs/progress/<area>.md
   ```
2. **Check documentation health and link integrity**:
   ```bash
   python scripts/docs_audit.py score
   ```
3. **Check consistency and release blockers**:
   ```bash
   python scripts/consistency.py check
   ```

Remind the user:
- Delegate complex or open-ended requests to `planner` first to generate verified Work Orders.
- Run selective tests rather than the entire test suite on every change.
- Follow the task closure checklist in `CLAUDE.md` Section 5 before marking tasks complete.

---

## 7. Section Correspondence Table

Mapping between the 15 sections of the Scaffold Workflow Guide (`scaffold-workflow-EN.pdf`) and this setup prompt:

| Guide Section | Title in Guide | Corresponding Section in this Prompt |
|---|---|---|
| Section 1 | Why a workflow | Section 1 (Core Purpose & Principles) |
| Section 2 | Repository layout | Section 3 (Table of 41 Files to Create) |
| Section 3 | CLAUDE.md and targeted retrieval | Section 4 (`CLAUDE.md` Adaptation) & Section 6 (Daily Commands) |
| Section 4 | The docs system | Section 3 & 4 (`docs/progress.md`, area sheets, `ROADMAP.md`) |
| Section 5 | Subagent roles and routing | Section 3 & 4 (`.claude/agents/*.md`, `AGENTS.md`, `GEMINI.md`) |
| Section 6 | Readiness Gate | Section 4 (`.claude/skills/work-order/SKILL.md`, `AGENTS.md`) |
| Section 7 | Evidence-based escalation | Section 4 (Subagent closing states `DONE`, `BLOCKED`, `FAILED x2`) |
| Section 8 | Necessity score, autonomy threshold, ledger and agent_audit | Section 3 & 4 (`docs/agents/ledger.txt`, `scripts/agent_audit.py`) |
| Section 9 | Consistency gate: spec files, drift, divergences | Section 3, 4 & 5 (`docs/spec/*`, `scripts/consistency.py`) |
| Section 10 | Docs audit | Section 3, 4 & 5 (`scripts/docs_audit.py`, `docs-loop` skill) |
| Section 11 | CI audit | Section 3, 4 & 5 (`.ci-audit.toml`, `.github/workflows/ci.yml`, `scripts/ci_audit.py`) |
| Section 12 | Multi-operator sync | Section 3 & 4 (`SYNC.md`, `sync/*`, `tools/sync_*.py`) |
| Section 13 | Writing rules as positive instructions | Section 1, 2c & 4 (Positive instruction rules, retirement by deletion) |
| Section 14 | Bootstrapping step by step | Sections 2, 2b, 2c, 2d, 4, 5 (The automated bootstrap procedure) |
| Section 15 | Maintenance and metrics | Section 5 (Verification Suite) & Section 6 (Daily Workflow) |
