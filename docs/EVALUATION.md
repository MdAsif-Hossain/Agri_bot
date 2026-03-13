# Evaluation & Reliability

AgriBot ships with a comprehensive offline evaluation harness to validate the reliability of its retrieved intelligence and safety policies.

## Harness Overview (`eval/`)

The framework relies on static ground-truth datasets located in `eval/datasets/`.

Evaluate your setup using standard Make commands:

```bash
make eval
```

## Supported Evaluations

### 1. Retrieval Quality (`eval_retrieval.py`)
Measures the capability of the Hybrid+Reranker pipeline at finding correct documentation chunks based on internal citations.
- **Metrics**: Recall@K, Mean Reciprocal Rank (MRR), nDCG@K.

### 2. Grounding Policy (`eval_grounding.py`)
Measures LLM hallucination resistance.
- **Metrics**: Citation Coverage (percentage of generated sentences containing source keywords), Unsupported Claim Ratio.

### 3. Refusal Correctness (`eval_refusal.py`)
Tests whether out-of-scope (OOS) or unsafe dosage questions are proactively blocked or appropriately caveated by the grounding enforcer.
- **Metrics**: Accuracy, False Positive Refusal Rate.

### 4. Latency Trace (`eval_latency.py`)
Collects and aggregates timings embedded in the payload's `timings_ms` trace from the graph nodes.
- **Metrics**: P50/P95 end-to-end, P50/P95 per-node.

## Running Ablation Studies

Execute `make ablations` (`eval/run_ablations.py`) to run evaluations across multiple backend configurations sequentially (e.g., sparse-only vs. dense-only vs. hybrid-kg) and generate comparative reports.
