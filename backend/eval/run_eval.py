"""Lightweight RAG pipeline evaluation - latency, retrieval hit-rate, classification
agreement - against a small hand-labeled test set. No LLM-judge calls: agreement is
measured directly against known-correct labels, keeping this cheap and fast to re-run.

Usage:
    python -m backend.eval.run_eval
"""
import asyncio
import json
import statistics
import time
from pathlib import Path

from backend.rag.setup import build_pipeline

TEST_SET_PATH = Path(__file__).parent / "test_clauses.json"
REPORT_PATH = Path(__file__).parent / "eval_report.md"


def _percentile(values, pct):
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * (pct / 100)
    f, c = int(k), min(int(k) + 1, len(values) - 1)
    if f == c:
        return values[f]
    return values[f] + (values[c] - values[f]) * (k - f)


async def run():
    with open(TEST_SET_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    pipeline = build_pipeline()

    latencies = []
    results = []

    for case in test_cases:
        start = time.perf_counter()
        candidates = await pipeline.retriever.retrieve(case["clause_text"], case["jurisdiction"])
        candidates = await pipeline.reranker.rerank(case["clause_text"], candidates)
        analysis = await pipeline.analyze_clause(case["clause_text"], case["jurisdiction"])
        elapsed = time.perf_counter() - start
        latencies.append(elapsed)

        retrieved_ids = {c["id"] for c in candidates}
        retrieval_hit = case["expected_statute_id"] in retrieved_ids
        classification_match = analysis.classification == case["expected_classification"]

        results.append({
            "id": case["id"],
            "jurisdiction": case["jurisdiction"],
            "expected_classification": case["expected_classification"],
            "actual_classification": analysis.classification,
            "classification_match": classification_match,
            "expected_statute_id": case["expected_statute_id"],
            "retrieval_hit": retrieval_hit,
            "latency_seconds": round(elapsed, 2),
        })

    n = len(results)
    retrieval_hit_rate = sum(r["retrieval_hit"] for r in results) / n if n else 0
    classification_agreement = sum(r["classification_match"] for r in results) / n if n else 0

    report_lines = [
        "# Clause-Guard RAG Pipeline Evaluation Report",
        "",
        f"Test set size: {n} hand-labeled clauses across {len(set(r['jurisdiction'] for r in results))} jurisdictions.",
        "",
        "## Aggregate Metrics",
        "",
        f"- **Retrieval hit-rate**: {retrieval_hit_rate:.1%} (expected statute appeared in the retrieved/reranked candidate set)",
        f"- **Classification agreement rate**: {classification_agreement:.1%} (pipeline output matched the hand-labeled expected classification)",
        f"- **Latency p50**: {_percentile(latencies, 50):.2f}s",
        f"- **Latency p95**: {_percentile(latencies, 95):.2f}s",
        f"- **Latency p99**: {_percentile(latencies, 99):.2f}s",
        f"- **Mean latency**: {statistics.mean(latencies):.2f}s" if latencies else "- Mean latency: n/a",
        "",
        "## Per-Case Results",
        "",
        "| ID | Jurisdiction | Expected | Actual | Match | Retrieval Hit | Latency (s) |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        report_lines.append(
            f"| {r['id']} | {r['jurisdiction']} | {r['expected_classification']} | "
            f"{r['actual_classification']} | {'yes' if r['classification_match'] else 'NO'} | "
            f"{'yes' if r['retrieval_hit'] else 'NO'} | {r['latency_seconds']} |"
        )

    report = "\n".join(report_lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)
    print(f"\nReport written to {REPORT_PATH}")


if __name__ == "__main__":
    asyncio.run(run())
