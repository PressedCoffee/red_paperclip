import unittest
from unittest.mock import MagicMock
from cognitive_autonomy_expansion_pack.meta_capsule_drift_engine import MetaCapsule


class TestMetaCapsuleDriftEngine(unittest.TestCase):

    def setUp(self):
        # Setup a mock AgentMemory
        self.mock_agent_memory = MagicMock()
        self.mock_agent_memory.log_capsule_drift = MagicMock()
        self.mock_agent_memory.get_last_drift_states = MagicMock(return_value=(
            {
                "value_biases": [0.0, 0.0],
                "goal_weights": [1.0, 1.0],
                "curiosity_mode": "neutral"
            },
            {
                "value_biases": [0.1, -0.1],
                "goal_weights": [1.1, 0.9],
                "curiosity_mode": "exploratory"
            }
        ))

        self.mock_llm = MagicMock()
        self.capsule = MetaCapsule(
            goal="Test Goal",
            values={"val1": 0.5, "val2": -0.5},
            tags=["test"],
            value_biases=[0.0, 0.0],
            goal_weights=[1.0, 1.0],
            curiosity_mode="neutral",
            agent_memory=self.mock_agent_memory,
            llm=self.mock_llm,
            live_mode=False
        )

    def test_drift_parameters_mutates_values(self):
        before = self.capsule.snapshot_parameters()
        self.capsule.drift_parameters(stress_factor=0.5)
        after = self.capsule.snapshot_parameters()

        changed = (
            before["value_biases"] != after["value_biases"] or
            before["goal_weights"] != after["goal_weights"] or
            before["curiosity_mode"] != after["curiosity_mode"]
        )
        self.assertTrue(changed, "Drift parameters did not mutate any values")

    def test_drift_parameters_logs_to_agent_memory(self):
        self.capsule.drift_parameters(stress_factor=0.1)
        self.mock_agent_memory.log_capsule_drift.assert_called_once()
        args, kwargs = self.mock_agent_memory.log_capsule_drift.call_args
        self.assertEqual(args[0], self.capsule.capsule_id)
        self.assertIn("before", args[1])
        self.assertIn("after", args[1])

    def test_capsule_diff_report_returns_diffs(self):
        diff_report = self.capsule.capsule_diff_report()
        self.assertIn("value_biases changed", diff_report)
        self.assertIn("goal_weights changed", diff_report)
        self.assertIn("curiosity_mode changed", diff_report)

    def test_capsule_diff_report_no_agent_memory(self):
        capsule_no_mem = MetaCapsule(
            goal="Test Goal",
            values={"val1": 0.5},
            tags=["test"],
            agent_memory=None
        )
        report = capsule_no_mem.capsule_diff_report()
        self.assertEqual(report, "No AgentMemory available.")

    def test_drift_parameters_live_mode_invokes_llm_and_logs(self):
        self.capsule.live_mode = True
        self.capsule.llm = self.mock_llm
        self.mock_llm.invoke.return_value = '{"value_biases": [0.1, 0.2], "goal_weights": [1.1, 1.2], "curiosity_mode": "exploratory"}'

        self.capsule.drift_parameters()

        self.mock_llm.invoke.assert_called_once()
        self.mock_agent_memory.log_llm_interaction.assert_called_once()
        log_call_args = self.mock_agent_memory.log_llm_interaction.call_args[0][1]
        self.assertIn("prompt", log_call_args)
        self.assertIn("completion", log_call_args)
        self.assertIn("timestamp", log_call_args)
        self.assertIn("correlation_id", log_call_args)
        self.assertEqual(self.capsule.value_biases, [0.1, 0.2])
        self.assertEqual(self.capsule.goal_weights, [1.1, 1.2])
        self.assertEqual(self.capsule.curiosity_mode, "exploratory")


if __name__ == "__main__":
    unittest.main()
