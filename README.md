# Single Agent vs. Agent Team for Code Generation

**Do AI agent teams actually write better code?**

Student project, ML Group RPTU Kaiserslautern (AI software engineering), supervised by Denys Senkin.

Multi-agent setups are popular, and they use more tokens. This project tests whether splitting the work across roles (a *planner* and a *coder*) improves code generation, or whether a single agent that plans first does just as well.

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

## Repository structure (planned)

```
configs/      experiment configs
data/         selected task IDs
prompts/      prompt templates for each setup and role
src/          data loading, model wrapper, code extraction, sandboxed test runner, setups A/B/C
results/      raw JSONL logs
analysis/     tables, plots, statistics
slurm/        job scripts for the Elwetritsch cluster
report/       report and slides
```

## Getting started

> Work in progress. Install and run instructions will be added once the code exists.

```bash
# planned
pip install -r requirements.txt
python run_experiment.py --setups A B C --tasks data/tasks.json --runs 3 --model Qwen/Qwen2.5-Coder-1.5B-Instruct
```

**Compute:** the Elwetritsch cluster (V100) or free Google Colab.

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
