# Single Agent vs. Agent Team for Code Generation

**Do AI agent teams actually write better code?**

Student project, ML Group RPTU Kaiserslautern (AI software engineering), supervised by Denys Senkin.

Multi-agent setups are popular, and they use more tokens. This project tests whether splitting the work across roles (a *planner* and a *coder*) improves code generation, or whether a single agent that plans first does just as well.

**Status (07.11.2026):** Phase 0 is done: repo, environment and the Colab GPU setup are verified. Next is Phase 1: data loader and sandboxed test runner. See [progress.md](progress.md).

---

## Experimental setups

All three setups use the **same small model**, the **same 20 MBPP tasks**, and **3 runs per task**.

```
A · Single agent        B · Plan, then code         C · Planner + coder
  Task                    Task                        Task
   ↓                       ↓                           ↓
  Agent                   Agent: plan → code          Planner
   ↓                       ↓                           ↓
  Code                    Code                        Coder
                                                       ↓
                                                      Code
 (baseline)              (control: adds planning)    (team: splits roles)
```

## Research questions

| # | Question | Comparison |
|---|---|---|
| 1 | Does the team solve more tasks than a solo agent? | C vs. A |
| 2 | If so, does the gain come from teamwork or just from planning? | C vs. B |
| 3 | How much does each extra solved task cost? | Tokens and GPU time |

## Metrics

- **Pass rate**: share of tasks that pass all of their MBPP tests
- **Cost**: tokens and GPU time spent
- **Run time**: how long each task takes
- **Variance**: how much results change across the 3 runs

No manual grading: the generated code runs against MBPP's own unit tests.

## Dataset

[MBPP (Mostly Basic Python Problems)](https://huggingface.co/datasets/google-research-datasets/mbpp) has about 1,000 entry-level Python tasks, each with a description, a reference solution and 3 assert-based tests. Licence CC-BY-4.0.
Original source: [google-research/mbpp](https://github.com/google-research/google-research/tree/master/mbpp) · Paper: Austin et al., 2021, *Program Synthesis with Large Language Models*.

## Models

Candidates (small, instruction-tuned):
- Qwen2.5-Coder-1.5B-Instruct
- Qwen3-0.6B
- Llama 3.2 1B Instruct
- Gemma 3 1B-it

## Repository structure

```
notebooks/                  Colab notebook for GPU runs              (exists)
scripts/                    helper scripts, e.g. check_env.py        (exists)
requirements.txt            generation packages (Colab + local)      (exists)
requirements-analysis.txt   analysis packages (local only)           (exists)
configs/                    experiment configs                       (planned)
data/                       selected task IDs                        (planned)
prompts/                    prompt templates for each setup and role (planned)
src/                        data loading, model wrapper, code extraction,
                            sandboxed test runner, setups A/B/C      (planned)
results/                    raw JSONL logs                           (planned)
analysis/                   tables, plots, statistics                (planned)
report/                     report and slides                        (planned)
```

## Setup

**Compute:** all GPU runs happen on **Google Colab (free T4)**. RPTU GPU access (provided by the supervisor) is an optional alternative. Local machines handle development and CPU-only work.

### Google Colab (GPU runs)
1. Open [notebooks/colab_run.ipynb](notebooks/colab_run.ipynb) in Colab (*File → Open notebook → GitHub*, paste the repo URL).
2. *Runtime → Change runtime type → T4 GPU*.
3. Optional: add a Hugging Face token as a secret (see below).
4. *Runtime → Run all*. The notebook clones this repo, installs `requirements.txt`, loads the token and runs the environment check. The last line should be `Environment OK`.

Edits made inside Colab are **not** saved back to GitHub. Change the notebook in the repo, push, then re-open it in Colab.

### Local (development, CPU)
```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install torch                          # CPU build; see pytorch.org for a CUDA build
pip install -r requirements.txt            # generation packages
pip install -r requirements-analysis.txt   # numpy, pandas, scipy, matplotlib
python scripts/check_env.py --skip-model   # checks Python, torch, MBPP loading
```

There are two requirements files:
- `requirements.txt`: what generation runs need. Both Colab and local machines install it. It leaves out `torch` (Colab ships its own CUDA build) and does not pin numpy or pandas, so Colab's preinstalled packages stay intact.
- `requirements-analysis.txt`: analysis packages, pinned, **local only**. Installing these on Colab breaks its built-in packages.

### Hugging Face access
The Qwen models are public and need no token. Llama 3.2 and Gemma 3 are *gated*:
1. Create a **Read** token at huggingface.co → *Settings → Access Tokens*.
2. Accept the licences on the model pages ([Llama 3.2 1B Instruct](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct), [Gemma 3 1B-it](https://huggingface.co/google/gemma-3-1b-it)). Check the status under *Settings → Gated Repositories*.
3. Log in:
   - **Locally:** `hf auth login`. The token is saved in the Hugging Face cache, not in the repo. Check with `hf auth whoami`.
   - **Colab:** 🔑 *Secrets* → add `HF_TOKEN` with *Notebook access* on. The notebook loads it automatically.

Never put the token in a repo file.

## Running the experiment

> Work in progress. Planned interface:

```bash
python run_experiment.py --setups A B C --tasks data/tasks.json --runs 3 --model Qwen/Qwen2.5-Coder-1.5B-Instruct
```

> ⚠️ This project runs model-generated code. It always runs in a subprocess with a timeout. Do not run it outside the provided sandboxed runner.

## Timeline

| Week | Phase | Goal |
|---|---|---|
| 1 | Setup | MBPP, a test runner, and Setup A working on 5 tasks |
| 2 | Build | Setups B and C, plus logging |
| 3 | Run | 3 setups × 20 tasks × 3 runs |
| 4 | Analyze | Tables, plots, statistics, unusual cases |
| 5 | Write | 3–4 page report |
| 6 | Wrap up | Hand in by **16.12.2026**, plus a 5-minute talk |

## Deliverables

- Code for all three setups that others can rerun
- Results: tables, plots, statistics
- A 3–4 page report
- A short talk (5 minutes max)

## Project docs

- [plan.md](plan.md): detailed phased plan, design decisions, risks, open questions
- [progress.md](progress.md): running log of work done and decisions made
