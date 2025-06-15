import unittest
from unittest.mock import MagicMock, patch
from cognitive_autonomy_expansion_pack.meta_reasoning_engine import GenesisMetaReasoner
from cognitive_autonomy_expansion_pack.meta_capsule_drift_engine import EXPERIMENTAL_FEATURES


class TestGenesisMetaReasoner(unittest.TestCase):
    def setUp(self):
        self.mock_agent_memory = MagicMock()
        self.mock_goal_reevaluator = MagicMock()
        self.meta_reasoner = GenesisMetaReasoner(
            agent_memory=self.mock_agent_memory,
            goal_reevaluator=self.mock_goal_reevaluator,
            snapshot_panel=None
        )

    def test_propose_exit_protocol_logs_and_stores_reasoning_when_feature_enabled(self):
        EXPERIMENTAL_FEATURES["chaos_pack"] = True
        reasoning_text = "Test reasoning for exit protocol"

        # Patch _log_reasoning_cycle to track calls
        with patch.object(self.meta_reasoner, "_log_reasoning_cycle") as mock_log:
            self.meta_reasoner.propose_exit_protocol(reasoning_text)

            # Check that _log_reasoning_cycle was called with correct phase and data
            mock_log.assert_any_call("propose_exit_protocol", reasoning_text)

        # Check that reasoning was stored in agent_memory via add_reasoning_pattern
        self.mock_agent_memory.add_reasoning_pattern.assert_called_with(
            pattern_name=reasoning_text)

    def test_propose_exit_protocol_skips_when_feature_disabled(self):
        EXPERIMENTAL_FEATURES["chaos_pack"] = False
        reasoning_text = "Test reasoning when feature disabled"

        with patch.object(self.meta_reasoner, "_log_reasoning_cycle") as mock_log:
            self.meta_reasoner.propose_exit_protocol(reasoning_text)

            # Check that _log_reasoning_cycle was called with skip message
            mock_log.assert_any_call(
                "propose_exit_protocol", "Feature 'chaos_pack' disabled; skipping exit protocol.")

        # Ensure add_reasoning_pattern was NOT called
        self.mock_agent_memory.add_reasoning_pattern.assert_not_called()


if __name__ == "__main__":
    unittest.main()
