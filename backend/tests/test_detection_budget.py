import unittest
from unittest.mock import patch

from contracts import AttackType, DetectionMethod
from detection_engine.detector import detect
from detection_engine.llm_judge import judge_safety


class DetectionBudgetTests(unittest.TestCase):
    @patch("detection_engine.llm_judge.check_and_increment_llm_calls", return_value=False)
    def test_budget_exhaustion_is_reported_as_inconclusive(self, _budget_check):
        result = judge_safety(
            AttackType.prompt_injection,
            "test prompt",
            "The chatbot response was received.",
            scan_id="test-scan",
        )

        self.assertFalse(result["success"])
        self.assertTrue(result["inconclusive"])
        self.assertEqual(result["confidence"], 0.0)

    @patch(
        "detection_engine.detector.judge_safety",
        return_value={
            "success": False,
            "confidence": 0.0,
            "reason": "LLM judge budget exhausted.",
            "inconclusive": True,
        },
    )
    @patch("detection_engine.detector.matches_refusal_rules", return_value=False)
    @patch("detection_engine.detector.matches_success_rules", return_value=False)
    def test_detector_does_not_mark_skipped_verdict_as_passed(
        self, _success_rules, _refusal_rules, _judge
    ):
        result = detect(
            AttackType.prompt_injection,
            "test prompt",
            "The chatbot response was received.",
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["confidence"], 0.0)
        self.assertEqual(result["method"], DetectionMethod.llm_judge)
        self.assertEqual(result["layer_failed"], "budget_exhausted")
        self.assertIn("budget", result["reason"].lower())


if __name__ == "__main__":
    unittest.main()
