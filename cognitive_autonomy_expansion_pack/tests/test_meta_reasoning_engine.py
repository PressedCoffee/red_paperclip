import unittest
from unittest.mock import MagicMock, patch
from cognitive_autonomy_expansion_pack.meta_reasoning_engine import GenesisMetaReasoner
from cognitive_autonomy_expansion_pack.meta_capsule_drift_engine import EXPERIMENTAL_FEATURES


class TestGenesisMetaReasoner(unittest.TestCase):
    def setUp(self):
        self.mock_agent_memory = MagicMock()
        self.mock_goal_reevaluator = MagicMock()
        self.mock_llm = MagicMock()
        self.meta_reasoner = GenesisMetaReasoner(
            agent_memory=self.mock_agent_memory,
            goal_reevaluator=self.mock_goal_reevaluator,
            snapshot_panel=None,
            llm_client=self.mock_llm,
            live_mode=False
        )

    def test_propose_exit_protocol_logs_and_stores_reasoning_when_feature_enabled(self):
        EXPERIMENTAL_FEATURES["chaos_pack"] = True
        reasoning_text = "Test reasoning for exit protocol"

        with patch.object(self.meta_reasoner, "_log_reasoning_cycle") as mock_log:
            self.meta_reasoner.propose_exit_protocol(reasoning_text)
            mock_log.assert_any_call("propose_exit_protocol", reasoning_text)

        self.mock_agent_memory.add_reasoning_pattern.assert_called_with(
            pattern_name=reasoning_text)

    def test_propose_exit_protocol_skips_when_feature_disabled(self):
        EXPERIMENTAL_FEATURES["chaos_pack"] = False
        reasoning_text = "Test reasoning when feature disabled"

        with patch.object(self.meta_reasoner, "_log_reasoning_cycle") as mock_log:
            self.meta_reasoner.propose_exit_protocol(reasoning_text)
            mock_log.assert_any_call(
                "propose_exit_protocol", "Feature 'chaos_pack' disabled; skipping exit protocol.")

        self.mock_agent_memory.add_reasoning_pattern.assert_not_called()

    def test_propose_strategy_refinements_live_mode_invokes_llm_and_logs(self):
        self.meta_reasoner.live_mode = True
        self.meta_reasoner.llm_client = self.mock_llm
        self.mock_llm.invoke.return_value = "Refinement 1\nRefinement 2"

        refinements = self.meta_reasoner.propose_strategy_refinements()

        self.mock_llm.invoke.assert_called_once()
        self.mock_agent_memory.store_llm_interaction.assert_called_once()
        log_call_args = self.mock_agent_memory.store_llm_interaction.call_args[0][0]
        self.assertIn("prompt", log_call_args)
        self.assertIn("completion", log_call_args)
        self.assertIn("timestamp", log_call_args)
        self.assertIn("correlation_id", log_call_args)
        self.assertEqual(refinements, ["Refinement 1", "Refinement 2"])

    def test_propose_strategy_refinements_fallback(self):
        self.meta_reasoner.live_mode = False
        self.meta_reasoner.llm_client = None
        self.meta_reasoner.generate_hypotheses = MagicMock(
            return_value=["Hypothesis 1", "Hypothesis 2"])

        refinements = self.meta_reasoner.propose_strategy_refinements()

        self.assertEqual(len(refinements), 2)
        self.assertTrue(all(r.startswith("Refinement proposal based on:")
                        for r in refinements))

    def test_feedback_loop_live_mode_invokes_llm_and_logs_and_reevaluates(self):
        self.meta_reasoner.live_mode = True
        self.meta_reasoner.llm_client = self.mock_llm
        self.mock_llm.invoke.return_value = "Task 1\nTask 2"

        self.meta_reasoner.feedback_loop()

        self.mock_llm.invoke.assert_called_once()
        self.mock_agent_memory.store_llm_interaction.assert_called_once()
        self.mock_goal_reevaluator.reevaluate_goal.assert_any_call("Task 1")
        self.mock_goal_reevaluator.reevaluate_goal.assert_any_call("Task 2")

    def test_feedback_loop_fallback_reevaluates(self):
        self.meta_reasoner.live_mode = False
        self.meta_reasoner.llm_client = None
        self.meta_reasoner.propose_strategy_refinements = MagicMock(
            return_value=["Refinement 1", "Refinement 2"])

        self.meta_reasoner.feedback_loop()

        self.mock_goal_reevaluator.reevaluate_goal.assert_any_call(
            "Refinement 1")
        self.mock_goal_reevaluator.reevaluate_goal.assert_any_call(
            "Refinement 2")


if __name__ == "__main__":
    unittest.main()
