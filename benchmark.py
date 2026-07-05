"""
Team Scorpians - Benchmark Script
Addresses judge feedback: "No Benchmarks - show numbers"

Runs a small labeled test set through the router and reports the numbers
that actually matter for Track 1's scoring: how much stayed local (free),
how much was escalated (real cost), estimated savings vs an "always-cloud"
baseline, and rough accuracy on questions with a known correct answer.

Run:  python benchmark.py
(Needs local-model + Fireworks reachable, same as router_agent.py)
"""

import json
from router_agent import route_query, FIREWORKS_PRICE_PER_1M_TOKENS

# Each entry: (query, expected_keyword_or_None, difficulty_label)
# Add more of your own before the real demo -- 10 is a starting point, not a target.
TEST_SET = [
    ("What is the capital of Pakistan?", "islamabad", "easy"),
    ("What is 15 + 27?", "42", "easy"),
    ("Who wrote Romeo and Juliet?", "shakespeare", "easy"),
    ("What is the boiling point of water in Celsius?", "100", "easy"),
    ("What color do you get by mixing blue and yellow?", "green", "easy"),
    ("Derive why merge sort has O(n log n) time complexity, step by step.", None, "hard"),
    ("Compare TCP and UDP and explain when to use each.", None, "hard"),
    ("Write a Python function to reverse a linked list.", None, "hard"),
    ("Explain the CAP theorem and its tradeoffs in distributed systems.", None, "hard"),
    ("Debug this: a recursive function causing a stack overflow on large inputs.", None, "hard"),
]


def run_benchmark():
    results = []
    for query, expected, difficulty in TEST_SET:
        r = route_query(query)
        correct = (expected.lower() in r.answer.lower()) if expected else None
        results.append({
            "query": query,
            "difficulty": difficulty,
            "escalated": r.escalated,
            "model_used": r.model_used,
            "local_tokens": r.local_tokens,
            "cloud_tokens": r.cloud_tokens,
            "latency_s": r.latency_s,
            "correct": correct,
        })
        tag = "CLOUD" if r.escalated else "LOCAL"
        print(f"[{tag}] ({difficulty}) {query[:50]}...")

    total = len(results)
    escalated_count = sum(1 for r in results if r["escalated"])
    local_only = total - escalated_count
    avg_latency = sum(r["latency_s"] for r in results) / total
    total_cloud_tokens = sum(r["cloud_tokens"] for r in results)

    checked = [r for r in results if r["correct"] is not None]
    accuracy = (sum(1 for r in checked if r["correct"]) / len(checked)) if checked else None

    # Baseline comparison: what would it cost if EVERY query went straight
    # to the Fireworks cloud model instead of trying local first?
    avg_tokens_per_cloud_call = (total_cloud_tokens / escalated_count) if escalated_count else 150
    baseline_cloud_tokens = avg_tokens_per_cloud_call * total
    baseline_cost = (baseline_cloud_tokens / 1_000_000) * FIREWORKS_PRICE_PER_1M_TOKENS
    actual_cost = (total_cloud_tokens / 1_000_000) * FIREWORKS_PRICE_PER_1M_TOKENS
    savings_pct = round((1 - actual_cost / baseline_cost) * 100, 1) if baseline_cost else 0.0

    print(f"\n{'=' * 55}")
    print(f"BENCHMARK RESULTS ({total} queries)")
    print(f"{'=' * 55}")
    print(f"Answered locally (zero-cost):  {local_only}/{total}  ({round(local_only / total * 100, 1)}%)")
    print(f"Escalated to cloud:            {escalated_count}/{total}  ({round(escalated_count / total * 100, 1)}%)")
    print(f"Average latency:               {round(avg_latency, 3)}s")
    if accuracy is not None:
        print(f"Accuracy (labeled subset):     {round(accuracy * 100, 1)}%  ({len(checked)} questions checked)")
    print(f"Actual cloud cost:             ${round(actual_cost, 4)}")
    print(f"'Always-cloud' baseline cost:  ${round(baseline_cost, 4)}")
    print(f"Estimated cost savings:        {savings_pct}%")
    print(f"{'=' * 55}")
    print("\nPut these numbers directly in your slide deck -- this is your")
    print("'How much faster / cheaper' answer.")

    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nFull per-query results saved to benchmark_results.json")


if __name__ == "__main__":
    run_benchmark()
