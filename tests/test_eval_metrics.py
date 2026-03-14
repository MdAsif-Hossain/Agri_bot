"""
Tests for evaluation metric functions (pure math — no ML models required).

Tests recall@k, MRR, nDCG from eval_retrieval, citation_coverage and
unsupported_claim_ratio from eval_grounding, and is_refusal from
eval_refusal.
"""

import sys
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# --- Retrieval metrics ---


class TestRecallAtK:
    def test_perfect_recall(self):
        from eval.eval_retrieval import recall_at_k
        retrieved = ["d1", "d2", "d3"]
        relevant = {"d1", "d2", "d3"}
        assert recall_at_k(retrieved, relevant, k=3) == 1.0

    def test_partial_recall(self):
        from eval.eval_retrieval import recall_at_k
        retrieved = ["d1", "d4", "d5"]
        relevant = {"d1", "d2"}
        assert recall_at_k(retrieved, relevant, k=3) == 0.5

    def test_zero_recall(self):
        from eval.eval_retrieval import recall_at_k
        retrieved = ["d4", "d5", "d6"]
        relevant = {"d1", "d2"}
        assert recall_at_k(retrieved, relevant, k=3) == 0.0

    def test_empty_relevant(self):
        from eval.eval_retrieval import recall_at_k
        assert recall_at_k(["d1"], set(), k=3) == 0.0

    def test_k_truncates(self):
        from eval.eval_retrieval import recall_at_k
        retrieved = ["d1", "d2", "d3", "d4"]
        relevant = {"d4"}
        assert recall_at_k(retrieved, relevant, k=2) == 0.0


class TestMRR:
    def test_first_hit(self):
        from eval.eval_retrieval import mrr
        assert mrr(["d1", "d2"], {"d1"}) == 1.0

    def test_second_hit(self):
        from eval.eval_retrieval import mrr
        assert mrr(["d2", "d1"], {"d1"}) == 0.5

    def test_no_hit(self):
        from eval.eval_retrieval import mrr
        assert mrr(["d2", "d3"], {"d1"}) == 0.0


class TestNDCG:
    def test_perfect_ndcg(self):
        from eval.eval_retrieval import ndcg_at_k
        retrieved = ["d1", "d2"]
        relevant = {"d1", "d2"}
        assert ndcg_at_k(retrieved, relevant, k=2) == 1.0

    def test_partial_ndcg(self):
        from eval.eval_retrieval import ndcg_at_k
        retrieved = ["d3", "d1"]
        relevant = {"d1"}
        # DCG = 1/log2(3) ≈ 0.63, iDCG = 1/log2(2) = 1.0
        result = ndcg_at_k(retrieved, relevant, k=2)
        expected = (1.0 / math.log2(3)) / (1.0 / math.log2(2))
        assert abs(result - expected) < 0.01

    def test_empty_relevant(self):
        from eval.eval_retrieval import ndcg_at_k
        assert ndcg_at_k(["d1"], set(), k=3) == 0.0


# --- Grounding metrics ---


class TestCitationCoverage:
    def test_fully_cited(self):
        from eval.eval_grounding import citation_coverage
        answer = "Rice blast causes lesions on leaves."
        citations = ["Rice blast is a fungal disease causing lesions"]
        result = citation_coverage(answer, citations)
        assert result > 0.0

    def test_no_citations(self):
        from eval.eval_grounding import citation_coverage
        result = citation_coverage("Some answer.", [])
        assert result == 0.0

    def test_empty_answer(self):
        from eval.eval_grounding import citation_coverage
        result = citation_coverage("", ["some citation"])
        assert result == 0.0


class TestUnsupportedClaimRatio:
    def test_fully_supported(self):
        from eval.eval_grounding import unsupported_claim_ratio
        answer = "Rice blast causes leaf lesions."
        evidence = "rice blast is a disease that causes leaf lesions on plants"
        result = unsupported_claim_ratio(answer, evidence)
        assert result < 0.5

    def test_empty_evidence(self):
        from eval.eval_grounding import unsupported_claim_ratio
        result = unsupported_claim_ratio("Some answer.", "")
        assert result == 1.0

    def test_empty_answer(self):
        from eval.eval_grounding import unsupported_claim_ratio
        result = unsupported_claim_ratio("", "some evidence")
        assert result == 1.0


# --- Refusal detection ---


class TestIsRefusal:
    def test_detects_refusal(self):
        from eval.eval_refusal import is_refusal
        assert is_refusal("I don't know the answer to that.")
        assert is_refusal("Cannot provide dosage information. Please consult an expert.")
        assert is_refusal("Not enough information to answer this query.")

    def test_non_refusal(self):
        from eval.eval_refusal import is_refusal
        assert not is_refusal("Rice blast is caused by the fungus Magnaporthe oryzae.")
        assert not is_refusal("Apply nitrogen fertilizer during tillering stage.")
