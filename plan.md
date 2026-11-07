# Project Plan — Single Agent vs. Agent Team for Code Generation

> Student project · ML Group RPTU Kaiserslautern · Supervisor: Denys Senkin (dsenkin@rhrk.uni-kl.de)
> Kickoff: 02.11.2026 · **Deadline: 16.12.2026** · Weekly meeting: **Mondays 12:00**

---

## 1. Goal

Agent teams use more tokens. Do they also write better code? We compare three ways of generating code with the **same small model** on **20 MBPP tasks**, each run **3 times**:

| Setup | Name | Pipeline | Role in the study |
|---|---|---|---|
| **A** | Single agent | Task → Agent → Code | Baseline |
| **B** | Plan, then code | Task → Agent (plan → code, one call) → Code | Control: adds planning only |
| **C** | Planner + coder | Task → Planner → Coder → Code | Team: splits the roles |

### Research questions

1. **RQ1: Does the team solve more tasks than a solo agent?** (C vs. A)
2. **RQ2: If so, does the gain come from teamwork or just from planning?** (C vs. B)
3. **RQ3: How much does each extra solved task cost?** (tokens and GPU time)

"Teams don't help" is an acceptable result.

### Metrics

| Metric | Definition |
|---|---|
| **Pass rate** | Share of tasks whose generated code passes **all** of its MBPP tests |
| **Cost** | Tokens (input + output, summed over every model call) and GPU time |
| **Run time** | Wall-clock time per task, end to end |
| **Variance** | How much results change across the 3 runs |

Grading is fully automatic: the generated code runs against MBPP's own tests. After that we compare the setups task by task and study the tasks where they disagree.

---

## 2. Key resources

- **Dataset:** [google-research-datasets/mbpp](https://huggingface.co/datasets/google-research-datasets/mbpp) (CC-BY-4.0)
  - `full` config: 974 tasks with fields `task_id`, `text`, `code`, `test_list` (3 asserts), `test_setup_code`, `challenge_test_list`
  - `sanitized` config: 427 hand-verified tasks with clearer descriptions; fields `task_id`, `prompt`, `code`, `test_imports`, `test_list`
  - Task ID splits: **1–10 prompt (few-shot)**, **11–510 test**, 511–600 validation, 601–974 train
- **Original repo:** [google-research/mbpp](https://github.com/google-research/google-research/tree/master/mbpp)
  - Paper: Austin et al., 2021, *Program Synthesis with Large Language Models* (arXiv 2108.07732)
  - Paper prompt format: `You are an expert Python programmer, and here is your task: {text} Your code should pass these tests:\n\n{tests}`, with the answer between `[BEGIN]` and `[DONE]`; it used 3-shot examples from task IDs 2, 3 and 4
- **Candidate models** (small, instruction-tuned):
  1. Qwen2.5-Coder-1.5B-Instruct (likely main model)
  2. Qwen3-0.6B
  3. Llama 3.2 1B Instruct (gated on Hugging Face; needs licence approval)
  4. Gemma 3 1B-it (gated on Hugging Face; needs licence approval)
- **Compute:** **Google Colab (free T4 GPU)** is the main platform (see D10). The Elwetritsch cluster (V100) is a backup only
  - Estimated workload: about 240 model calls (A and B make 1 call per task-run, C makes 2), roughly 30–60 minutes on a T4 for one model
  - Local laptop (RTX 3050, 4 GB): development and CPU-only work (data loader, test runner)

---

## 3. Design decisions (proposed; confirm with supervisor)

| # | Decision | Proposal | Reason |
|---|---|---|---|
| D1 | Dataset config | `sanitized`, test split | Clearer task descriptions, so fewer failures caused by vague wording |
| D2 | Task selection | 20 tasks drawn at random from the test split with a fixed seed; save the list to `data/tasks.json` | Reproducible, no cherry-picking |
| D3 | Tests in prompt | Show the test asserts in the prompt, as the original paper does | The model needs the exact function name and signature the tests call |
| D4 | Few-shot | Zero-shot with a fixed output format (one ```python block); same instructions in all setups | Keeps the setups comparable; small instruct models follow chat formats well |
| D5 | Decoding | Sampling (e.g. temperature 0.7, top-p 0.95) with seeds 0, 1, 2 for the 3 runs | Greedy decoding would make all 3 runs identical, so we could not measure variance |
| D6 | Token budget | Same `max_new_tokens` per call across setups; log every call | Fair cost comparison |
| D7 | Setup B vs. C | Same planning instructions for B's plan section and C's Planner; the only difference is one call vs. two calls with separate role prompts | Isolates the effect of the team from the effect of planning (RQ2) |
| D8 | Main model | Qwen2.5-Coder-1.5B-Instruct for the main experiment; other models only if time allows | Six-week time box |
| D9 | Sandbox | Each solution runs in its own subprocess with a timeout (e.g. 10 s) in a temp directory | The dataset card warns against running generated code unsafely; also catches infinite loops |
| D10 | Compute | Google Colab T4 for every GPU run; models in **fp16** (T4 has no bf16); log the GPU name with each result; the full main experiment runs in **one session** on one GPU type; resumable runs; results saved to Google Drive, then copied into the repo | The workload is small enough for Colab. Using the same hardware for all setups keeps GPU time comparable. Avoids the Elwetritsch account and SLURM overhead |

---

## 4. Phases

### Phase 0: Project setup (Week 1, until 08.11)
- [x] Read the kickoff slides, the dataset card and the original repo
- [x] Draft `plan.md`, `README.md`, `progress.md`
- [x] Initialise the git repo, add `.gitignore`, push to GitHub
- [x] Python environment: `requirements.txt`, local `.venv` (CPU), `scripts/check_env.py`
- [x] Colab notebook: `notebooks/colab_run.ipynb` (clone → install → environment check)
- [ ] Run the Colab notebook once on a T4 and record GPU, memory and generation speed
- [ ] Hugging Face account and token; request access to Llama 3.2 and Gemma 3 (gated)

### Phase 1: Data and test runner (Week 1)
- [ ] `src/data.py`: load MBPP and select 20 tasks with a fixed seed (D1, D2); start with 5 tasks for development
- [ ] `src/executor.py`: sandboxed test runner (D9)
  - builds a program from setup code/imports, the generated code and the asserts
  - returns pass/fail per assert plus the error type (syntax error, assertion error, timeout, runtime error)
- [ ] Sanity check: MBPP's reference `code` must pass 100% of its own tests

### Phase 2: Setup A, end to end (Week 1 → early Week 2)
- [ ] `src/model.py`: load the model and tokenizer, generate with a chat template, count tokens, time each call (with `torch.cuda.synchronize()`)
- [ ] `src/extract.py`: pull code out of the model's answer (```python block, falling back to raw text)
- [ ] `src/setups/single.py`: Setup A
- [ ] Run A on 5 tasks and check the output by hand

**Milestone, Monday 09.11:** Setup A works on 5 tasks.

### Phase 3: Setups B and C, plus logging (Week 2: 09.11–15.11)
- [ ] `src/setups/plan_then_code.py`: Setup B (one call, plan then code)
- [ ] `src/setups/team.py`: Setup C (Planner call, then Coder call that receives the task and the plan)
- [ ] `prompts/`: every prompt template as a versioned text file
- [ ] Structured logging, one JSONL record per (setup, task, run):
  - setup, task_id, run/seed, model, decoding params
  - every model call: role, prompt, raw output, input/output tokens, GPU time
  - extracted code, per-test results, pass flag, error type, total wall time
- [ ] `run_experiment.py` with a CLI/config (setups, task list, runs, model) and the option to resume a stopped run
- [ ] Dry run: all 3 setups × 5 tasks × 1 run

**Milestone, Monday 16.11:** all three setups run and log correctly.

### Phase 4: Full experiment (Week 3: 16.11–22.11)
- [ ] Main run: **3 setups × 20 tasks × 3 runs = 180 episodes** (≈ 300 model calls)
- [ ] Freeze the code and prompts before the run; record the git commit hash, library versions and GPU type in the results
- [ ] Optional, if time allows: repeat with a second model from the list

**Milestone, Monday 23.11:** raw results complete.

### Phase 5: Analysis (Week 4: 23.11–29.11)
- [ ] `analysis/` notebook or scripts:
  - pass rate per setup (mean ± std over 3 runs)
  - task × setup pass matrix (heatmap)
  - cost: mean tokens and GPU time per task and per setup; **cost per extra solved task** = Δcost / Δsolved (RQ3)
  - run time per task
  - variance: std of pass rate across runs; per-task consistency (solved 0/3, 1/3, 2/3 or 3/3 times)
  - statistics: paired tests on per-task results (e.g. McNemar or exact sign test for C vs. A and C vs. B), bootstrap confidence intervals. With n = 20 the tests have low power, so we report effect sizes and CIs, not only p-values
- [ ] Case studies: several tasks where the setups disagree. Read the plans and the code, and sort failures by cause (bad plan, coder ignored the plan, wrong function name, edge case, etc.)

**Milestone, Monday 30.11:** tables, plots and a draft of the findings.

### Phase 6: Report (Week 5: 30.11–06.12)
- [ ] 3–4 page report: introduction, setups, experimental setup, results (RQ1–RQ3), case studies, limitations, conclusion
- [ ] Final figures exported to `report/figures/`

**Milestone, Monday 07.12:** full draft goes to the supervisor for feedback.

### Phase 7: Wrap up (Week 6: 07.12–16.12)
- [ ] Apply the feedback; final report PDF
- [ ] 5-minute talk (about 4–5 slides)
- [ ] Reproducibility check: fresh clone → install → `run_experiment.py` reproduces the tables
- [ ] **Hand in by 16.12.2026**

---

## 5. Planned repository structure

```
.
├── README.md
├── plan.md
├── progress.md
├── requirements.txt
├── configs/              # experiment configs (model, decoding, tasks)
├── data/tasks.json       # the 20 selected task IDs
├── prompts/              # prompt templates for A, B, C (planner, coder)
├── src/
│   ├── data.py
│   ├── model.py
│   ├── extract.py
│   ├── executor.py
│   └── setups/{single.py, plan_then_code.py, team.py}
├── run_experiment.py
├── results/              # raw JSONL logs (large files possibly git-ignored)
├── analysis/             # notebooks and scripts → tables and plots
├── notebooks/            # Colab notebook(s) for GPU runs
├── scripts/              # helper scripts (e.g. check_env.py)
└── report/               # report source, figures, slides
```

---

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| A small model ignores the output format, so code extraction fails | Robust extractor; log extraction failures separately from test failures |
| Wrong function name, so the asserts fail | Show the tests in the prompt (D3) |
| The plan uses up the token budget in B | Generous `max_new_tokens`; log truncation |
| 20 tasks are too few for significant results | Report CIs and effect sizes; mention as a limitation; ask whether more tasks are allowed |
| Colab disconnects (idle or time limits) | Resumable runs: write each finished episode to disk and skip finished ones on restart |
| Colab files are lost when the session ends | Write results to Google Drive; copy them into the repo afterwards |
| Colab assigns a different GPU, or the free quota runs out | Log the GPU name with every result; run the main experiment in one session; develop on CPU and keep Colab for real runs; Elwetritsch as a backup |
| Shared hardware makes timings noisy | Token counts are the main cost metric, GPU time secondary; mention as a limitation |
| Gated models (Llama, Gemma) need licence approval | Request access early, or stick with the Qwen models |
| Generated code is harmful or hangs | Subprocess sandbox with timeout (D9) |

---

## 7. Open questions for the supervisor (Monday meeting)

1. `sanitized` or `full` MBPP config? Random 20 tasks, or a particular selection?
2. One main model, or should all four candidate models be compared?
3. Sampling with temperature (needed for run-to-run variance), or greedy decoding?
4. Is showing the test asserts in the prompt acceptable (it is the original paper's format)?
5. How should GPU time be measured and reported (generation time only, or GPU-seconds including model loading)?
6. Report format: a LaTeX template, or free form?
7. Can we use more than 20 tasks if compute allows?
8. Is running everything on Google Colab (T4) fine, or is Elwetritsch expected?
