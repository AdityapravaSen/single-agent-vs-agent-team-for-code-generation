# Progress Log

Running record of work done, decisions made and next steps. Newest entries at the top.

**Working agreement:** every change to the project (files, code, git) is proposed first and made only after approval.

---

## Status overview

| Phase | Description | Status |
|---|---|---|
| 0 | Project setup (docs, git, environment) | ✅ Done (only Llama 3.2 licence approval pending) |
| 1 | Data loading and sandboxed test runner | ⚪ Not started |
| 2 | Setup A end to end on 5 tasks | ⚪ Not started |
| 3 | Setups B and C, plus logging | ⚪ Not started |
| 4 | Full experiment (3 × 20 × 3) | ⚪ Not started |
| 5 | Analysis | ⚪ Not started |
| 6 | Report | ⚪ Not started |
| 7 | Wrap up and talk (deadline 16.12.2026) | ⚪ Not started |

### Where to pick up next session
- **Phase 1** (CPU only, on the laptop):
  - `src/data.py`: load the sanitized test split and select tasks with a fixed seed → `data/tasks.json`
  - `src/executor.py`: run code against a task's tests in a subprocess with a timeout
  - `scripts/check_executor.py`: reference solutions must pass 100%; the wrong `remove_Occ` from the Colab test must fail
- Before fixing the 20-task list, ask at the **Monday 09.11, 12:00** meeting: random 20 tasks or a specific selection? (plan.md §7)
- Watch for the email from Meta about Llama 3.2 access, then check it with `.venv\Scripts\hf.exe download meta-llama/Llama-3.2-1B-Instruct config.json`

---

## 2026-11-07 (Sat): Compute decision and environment setup

### Decisions
- **Google Colab (free T4) is the only GPU platform** (plan.md D10). The Elwetritsch cluster is a backup. Reasons:
  - The workload is small: about 240 model calls, roughly 30–60 minutes for one model on a T4
  - The kickoff slides allow either platform ("Elwetritsch V100s or free Google Colab")
  - It avoids the cluster account, SLURM and queue waits
- Models load in **fp16** (T4 has no bf16); every result logs the GPU name; the main experiment runs in one session; runs can resume; results go to Google Drive
- Local laptop (RTX 3050, 4 GB) is for development and CPU-only work
- To confirm with the supervisor (plan.md §7, question 8)

### Done
- `requirements.txt` with pinned versions: transformers 5.22.2, accelerate 1.15.0, datasets 5.1.0, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, matplotlib 3.11.2, tqdm 4.70.1, PyYAML 6.0.3. `torch` is left out on purpose (Colab has its own CUDA build). This was later split into two files (see "Fix" below)
- Local `.venv`: Python 3.13.9 with torch 2.15.0 (CPU build)
- `scripts/check_env.py`: prints Python and GPU info, loads MBPP, and optionally runs one test generation with the main model (memory, time, tokens/s)
- `notebooks/colab_run.ipynb`: clone repo → install requirements → load HF token from Colab secrets → environment check
- README: new Setup section (Colab, local CPU, Hugging Face access); plan.md updated (D10, risks, folder structure, Phase 0 checklist)
- Local check passed (`check_env.py --skip-model`): **MBPP sanitized test split has 257 tasks** (train 120, validation 43, prompt 7). First test task: #11 `remove_Occ`
- Harmless warnings during the check: no HF token (only affects download rate limits); Windows has no symlink support for the HF cache (uses a bit more disk space)

### First Colab run (`notebooks/colab_run.ipynb`)
| | Result |
|---|---|
| GPU | Tesla T4, 14.6 GB |
| Python / torch | 3.13.16 / 2.14.1+cu130 (same Python minor version as local) |
| Model | Qwen2.5-Coder-1.5B-Instruct, fp16 |
| Speed | 68 tokens in, 139 tokens out in 7.0 s → **19.9 tokens/s** (greedy, batch size 1) |
| Peak GPU memory | **2.89 GB** |

- **Runtime estimate:** about 300 output tokens per call is about 15 s, so ~240 calls take about **60 minutes**. That still fits in one Colab session
- **The sample answer for task #11 is wrong.** The model used `s.rstrip(c)` to remove the "last occurrence", but `rstrip` only strips trailing characters. `remove_Occ("hello","l")` returns `"helo"` instead of `"heo"`. This is the kind of mistake the test runner has to catch
- **The model adds an explanation after the code block.** The code extractor (Phase 2) must take just the ```` ```python ```` block

### Fix: the install conflicted with Colab's packages
- Problem: pinning `pandas==3.1.1` and `numpy==2.5.4` upgraded Colab's preinstalled packages. That broke `google-colab` (needs pandas 2.2.3), `numba` (needs numpy < 2.5) and `cudf`, and caused a `bottleneck` warning
- Fix: split the requirements
  - `requirements.txt` (Colab + local): transformers, accelerate, datasets, tqdm, PyYAML. numpy and pandas are not pinned, so Colab keeps its own
  - `requirements-analysis.txt` (local only): numpy, pandas, scipy, matplotlib, pinned
- `check_env.py`: replaced the deprecated `torch_dtype=` argument with `dtype=`

### Next steps
- [x] Run `notebooks/colab_run.ipynb` on a T4 and record GPU memory and tokens/s for Qwen2.5-Coder-1.5B
- [x] Re-run the notebook on a fresh Colab runtime and confirm the install shows no conflicts
  - Verified: only `cudf` vs `pyarrow` remains (harmless; we don't use cudf). The pandas, numpy and bottleneck conflicts and the `torch_dtype` warning are gone
  - 23.1 tokens/s, peak memory 2.89 GB; the same answer as the first run (greedy decoding is deterministic)
- [x] Hugging Face account and token
  - Locally: token stored with `hf auth login` (in the user's HF cache, not in the repo)
  - Colab: `HF_TOKEN` secret, loaded into the environment by a notebook cell so `!python` scripts can use it
  - Gemma 3 1B-it licence accepted; **Llama 3.2 1B Instruct is waiting for Meta's approval**
- [ ] Monday 09.11 meeting: open questions (plan.md §7)
- [ ] Phase 1: `src/data.py` (task selection) and `src/executor.py` (sandboxed test runner); see "Where to pick up next session" above

---

## 2026-11-07 (Sat): Git repository setup

### Done
- Initialised a local git repo on branch `main`
- Linked the remote `origin` → https://github.com/AdityapravaSen/single-agent-vs-agent-team-for-code-generation
- Based local `main` on the remote's first commit, which holds the MIT `LICENSE`, so nothing was overwritten or force-pushed
- Added `.gitignore`: the kickoff PDF (course material, kept local only), Python caches, virtual environments, Jupyter checkpoints, model/dataset caches, `results/raw/`, SLURM logs, `.env`, editor files
- Committed and pushed `README.md`, `plan.md`, `progress.md`, `.gitignore`

### Next steps
- [x] Set up the Python environment and `requirements.txt` (see the entry above)
- [ ] Take the open questions (plan.md §7) to the Monday 09.11 meeting (carried forward)
- [ ] Start Phase 1: data loader and sandboxed test runner (carried forward)

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
