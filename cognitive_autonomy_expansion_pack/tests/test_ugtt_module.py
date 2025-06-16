from cognitive_autonomy_expansion_pack.ugtt_module import CapsuleUGTT
import numpy as np
import unittest
from unittest.mock import MagicMock
import sys
import types

# Mock pinecone module to avoid import errors in tests
mock_pinecone = types.ModuleType("pinecone")
sys.modules["pinecone"] = mock_pinecone


class TestCapsuleUGTT(unittest.TestCase):
    def setUp(self):
        self.agent_id = "agent_123"
        self.mock_llm = MagicMock()
        self.mock_agent_memory = MagicMock()
        self.ugtt = CapsuleUGTT(agent_id=self.agent_id,
                                badge_hooks_enabled=False,
                                llm=self.mock_llm,
                                agent_memory=self.mock_agent_memory)

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
        self.assertEqual(equilibrium, [0])

    def test_execute_strategy_live_mode_invokes_llm_and_logs(self):
        payoff_matrix = np.array([[3, 2], [1, 4]])
        self.ugtt.live_mode = True
        self.ugtt.llm = self.mock_llm
        self.ugtt.agent_memory = self.mock_agent_memory
        self.mock_llm.invoke.return_value = "LLM completion"

        result = self.ugtt.execute_strategy(
            "TestStrategy", payoff_matrix, 0, live_mode=True, correlation_id="corr123")

        self.mock_llm.invoke.assert_called_once()
        self.mock_agent_memory.log.assert_called_once()
        log_call_args = self.mock_agent_memory.log.call_args[0][0]
        self.assertIn("prompt", log_call_args)
        self.assertIn("completion", log_call_args)
        self.assertIn("timestamp", log_call_args)
        self.assertIn("correlation_id", log_call_args)
        self.assertIn("LLM completion", result)

    def test_execute_strategy_fallback(self):
        payoff_matrix = np.array([[3, 2], [1, 4]])
        self.ugtt.live_mode = False
        self.ugtt.llm = None
        self.ugtt.agent_memory = self.mock_agent_memory

        result = self.ugtt.execute_strategy(
            "TestStrategy", payoff_matrix, 0, live_mode=False)

        self.assertIn("UGTT Analysis", result)
        self.assertEqual(len(self.ugtt.strategy_execution_log), 1)
        self.assertEqual(
            self.ugtt.last_strategy_executed["strategy_name"], "TestStrategy")

    def test_get_snapshot_metadata(self):
        payoff_matrix = np.array([[3, 2], [1, 4]])
        self.ugtt.execute_strategy("TestStrategy", payoff_matrix, 0)
        metadata = self.ugtt.get_snapshot_metadata()
        self.assertIn("last_strategy_executed", metadata)
        self.assertIn("strategy_execution_count", metadata)


if __name__ == "__main__":
    unittest.main()
