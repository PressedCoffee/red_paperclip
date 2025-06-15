from cognitive_autonomy_expansion_pack.ugtt_module import CapsuleUGTT
import numpy as np
import unittest
import sys
import types

# Mock pinecone module to avoid import errors in tests
mock_pinecone = types.ModuleType("pinecone")
sys.modules["pinecone"] = mock_pinecone


class TestCapsuleUGTT(unittest.TestCase):
    def setUp(self):
        self.agent_id = "agent_123"
        self.ugtt = CapsuleUGTT(agent_id=self.agent_id,
                                badge_hooks_enabled=False)

    def test_construct_payoff_matrix(self):
        strategies = ["S1", "S2"]
        payoffs = [[3, 2], [1, 4]]
        matrix = self.ugtt.construct_payoff_matrix(strategies, payoffs)

        self.assertTrue(np.array_equal(matrix, np.array(payoffs)))

    def test_evaluate_strategy(self):
        payoff_matrix = np.array([[3, 2], [1, 4]])
        expected_payoff = self.ugtt.evaluate_strategy(payoff_matrix, 0)
        self.assertAlmostEqual(expected_payoff, 2.5)

    def test_evaluate_strategy_out_of_range(self):
        payoff_matrix = np.array([[3, 2], [1, 4]])
        with self.assertRaises(IndexError):
            self.ugtt.evaluate_strategy(payoff_matrix, 5)

    def test_compute_nash_equilibrium(self):
        payoff_matrix = np.array([[3, 2], [1, 4]])
        equilibrium = self.ugtt.compute_nash_equilibrium(payoff_matrix)
        # Strategy with highest average payoff is index 0 (matches implementation)
        self.assertEqual(equilibrium, [0])

    def test_execute_strategy_logs_and_snapshot(self):
        payoff_matrix = np.array([[3, 2], [1, 4]])
        self.ugtt.execute_strategy("TestStrategy", payoff_matrix, 0)
        self.assertEqual(
            self.ugtt.last_strategy_executed["strategy_name"], "TestStrategy")
        self.assertEqual(len(self.ugtt.strategy_execution_log), 1)

    def test_get_snapshot_metadata(self):
        payoff_matrix = np.array([[3, 2], [1, 4]])
        self.ugtt.execute_strategy("TestStrategy", payoff_matrix, 0)
        metadata = self.ugtt.get_snapshot_metadata()
        self.assertIn("last_strategy_executed", metadata)
        self.assertIn("strategy_execution_count", metadata)


if __name__ == "__main__":
    unittest.main()
