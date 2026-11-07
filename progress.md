# Progress Log

Running record of work done, decisions made and next steps. Newest entries at the top.

**Working agreement:** every change to the project (files, code, git) is proposed first and made only after approval.

---

## Status overview

| Phase | Description | Status |
|---|---|---|
| 0 | Project setup (docs, git, environment) | 🟡 In progress |
| 1 | Data loading and sandboxed test runner | ⚪ Not started |
| 2 | Setup A end to end on 5 tasks | ⚪ Not started |
| 3 | Setups B and C, plus logging | ⚪ Not started |
| 4 | Full experiment (3 × 20 × 3) | ⚪ Not started |
| 5 | Analysis | ⚪ Not started |
| 6 | Report | ⚪ Not started |
| 7 | Wrap up and talk (deadline 16.12.2026) | ⚪ Not started |

---

## 2026-11-07 (Sat): Remove Claude co-author attribution

### Problem
- The first commit (`7e94012`) ended with a `Co-Authored-By: Claude` line, so GitHub listed Claude as a contributor.

### Done
- Turned off Claude attribution in commits and PRs globally (`attribution` in `~/.claude/settings.json`)
- Saved a rule in Claude's memory never to add attribution lines in this project
- [x] Rewrote commit `7e94012` → `2ce26fc` without the co-author line and force-pushed it. The user ran this by hand because Claude Code's safety check blocked it. Verified: the remote history now names only Adityaprava Sen

### Commands used
```bash
git commit --amend -m "Add project plan, README, progress log and .gitignore"
git push --force-with-lease origin main
```

---

## 2026-11-07 (Sat): Git repository setup

### Done
- Initialised a local git repo on branch `main`
- Linked the remote `origin` → https://github.com/AdityapravaSen/single-agent-vs-agent-team-for-code-generation
- Based local `main` on the remote's first commit, which holds the MIT `LICENSE`, so nothing was overwritten or force-pushed
- Added `.gitignore`: the kickoff PDF (course material, kept local only), Python caches, virtual environments, Jupyter checkpoints, model/dataset caches, `results/raw/`, SLURM logs, `.env`, editor files
- Committed and pushed `README.md`, `plan.md`, `progress.md`, `.gitignore`

### Next steps
- [ ] Set up the Python environment and `requirements.txt`
- [ ] Take the open questions (plan.md §7) to the Monday 09.11 meeting
- [ ] Start Phase 1: data loader and sandboxed test runner

---

## 2026-11-07 (Sat): Kickoff review and planning

### Done
- Read the kickoff slides (`kickoff_rptu_1.pdf`, 9 slides, dated 02.11.2026). Key points:
  - Three setups: **A** single agent, **B** plan then code (one agent), **C** planner + coder (team)
  - Same small model everywhere · 20 MBPP tasks · 3 runs each
  - Research questions: C vs. A (does the team help?), C vs. B (teamwork or just planning?), cost per extra solved task
  - Metrics: pass rate, cost (tokens, GPU time), run time, variance across runs
  - Candidate models: Qwen2.5-Coder-1.5B-Instruct, Qwen3-0.6B, Llama 3.2 1B Instruct, Gemma 3 1B-it
  - Compute: Elwetritsch V100s or Google Colab
  - Deliverables: code others can rerun, results (tables, plots, statistics), a 3–4 page report, a 5-minute talk
  - Deadline **16.12.2026**; weekly meeting Mondays 12:00
- Reviewed the MBPP dataset card on Hugging Face:
  - `full` config (974 tasks; train 374, test 500, validation 90, prompt 10) and `sanitized` config (427 hand-verified tasks)
  - Each task has 3 assert tests in `test_list`, plus `test_setup_code` / `test_imports`
  - The card warns to run generated code in a safe environment
- Reviewed the original google-research/mbpp repo:
  - Task ID splits: 1–10 prompt, 11–510 test, 511–600 validation, 601–974 train
  - Paper prompt format: "You are an expert Python programmer, and here is your task: … Your code should pass these tests: …", with `[BEGIN]`/`[DONE]` delimiters and 3-shot examples from tasks 2–4
- Created `plan.md` (phases, design decisions D1–D9, risks, open questions), `README.md` and `progress.md`

### Decisions (proposed, waiting for supervisor confirmation)
- Use the `sanitized` test split; pick 20 tasks with a fixed seed
- Show the test asserts in the prompt so the model knows the function signature
- Sample with seeds 0/1/2 so that run-to-run variance exists
- Main model: Qwen2.5-Coder-1.5B-Instruct

### Next steps
- [x] Set up the git repo (done, see the entry above)
