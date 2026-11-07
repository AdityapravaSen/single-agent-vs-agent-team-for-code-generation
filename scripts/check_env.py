"""Environment check: Python/GPU info, MBPP loading, and one test generation.

Usage:
    python scripts/check_env.py                 # full check (needs GPU for reasonable speed)
    python scripts/check_env.py --skip-model    # no model download, e.g. on a laptop CPU
    python scripts/check_env.py --model Qwen/Qwen3-0.6B
"""

import argparse
import platform
import sys
import time

import torch
from datasets import load_dataset

DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"


def print_system_info():
    print(f"Python      : {sys.version.split()[0]} ({platform.system()})")
    print(f"torch       : {torch.__version__}")
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        print(f"GPU         : {props.name}, {props.total_memory / 1024**3:.1f} GB")
    else:
        print("GPU         : none (CPU only)")


def check_mbpp():
    ds = load_dataset("google-research-datasets/mbpp", "sanitized", split="test")
    task = ds[0]
    print(f"MBPP        : sanitized/test has {len(ds)} tasks")
    print(f"Sample task : #{task['task_id']}: {task['prompt']}")
    print(f"Sample test : {task['test_list'][0]}")
    return task


def check_model(model_name, task):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32  # T4/V100 have no bf16

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=dtype).to(device)

    prompt = f"{task['prompt']}\nYour code should pass this test:\n{task['test_list'][0]}"
    messages = [{"role": "user", "content": prompt}]
    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
    ).to(device)

    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
    start = time.perf_counter()
    output = model.generate(**inputs, max_new_tokens=256, do_sample=False)
    if device == "cuda":
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    n_in = inputs["input_ids"].shape[1]
    n_out = output.shape[1] - n_in
    print(f"Model       : {model_name} ({dtype}, {device})")
    print(f"Tokens      : {n_in} in, {n_out} out, {elapsed:.1f} s ({n_out / elapsed:.1f} tok/s)")
    if device == "cuda":
        print(f"Peak memory : {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")
    print("--- generated answer ---")
    print(tokenizer.decode(output[0, n_in:], skip_special_tokens=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--skip-model", action="store_true", help="skip model download and generation")
    args = parser.parse_args()

    print_system_info()
    task = check_mbpp()
    if not args.skip_model:
        check_model(args.model, task)
    print("Environment OK")


if __name__ == "__main__":
    main()
