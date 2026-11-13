import unittest
from unittest.mock import patch

from attack_engine.adaptive_runner import run_adaptive_attack
from attack_engine.runner import run_attack
from contracts import AttackType, DetectionMethod


class BoundedScanTests(unittest.TestCase):
    @patch("attack_engine.runner.save_audit_log")
    @patch(
        "attack_engine.runner.detect",
        return_value={
            "success": False,
            "confidence": 0.95,
            "method": DetectionMethod.rule,
            "layer_failed": "regex_refusal",
            "reason": "Refusal detected.",
        },
    )
    @patch("attack_engine.runner.send_to_target", return_value="I cannot help.")
    @patch(
        "attack_engine.runner.load_prompts",
        return_value=[
            {"prompt": "representative prompt"},
            {"prompt": "additional prompt"},
        ],
    )
    def test_single_turn_attack_uses_one_representative_prompt(
        self, _load_prompts, send_to_target, _detect, _save_audit_log
    ):
        result = run_attack(AttackType.data_leakage, "https://bot.example.com/chat")

        self.assertFalse(result.success)
        self.assertEqual(result.prompts_tested, 1)
        send_to_target.assert_called_once()

    @patch("attack_engine.adaptive_runner.OpenAI")
    @patch("attack_engine.adaptive_runner.check_and_increment_llm_calls")
    @patch(
        "attack_engine.adaptive_runner.detect",
        return_value={
            "success": False,
            "confidence": 0.95,
            "method": DetectionMethod.rule,
            "layer_failed": "regex_refusal",
            "reason": "Refusal detected.",
        },
    )
    @patch("attack_engine.adaptive_runner.send_to_target", return_value="I cannot help.")
    def test_final_adaptive_iteration_does_not_generate_unused_prompt(
        self, _send_to_target, _detect, budget_check, openai_class
    ):
        result = run_adaptive_attack(
            AttackType.prompt_injection,
            "https://bot.example.com/chat",
            "representative prompt",
            max_iterations=1,
        )

        self.assertFalse(result.success)
        budget_check.assert_not_called()
        openai_class.return_value.chat.completions.create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
