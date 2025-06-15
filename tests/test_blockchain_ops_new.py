import unittest
from agents.blockchain_ops import BlockchainOpsSimulator
from trading.trading_logic import TradeEvaluator
from agents.agent import Agent


class TestBlockchainOpsSimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = BlockchainOpsSimulator()

    def test_simulate_trade_consequence_basic(self):
        agent_id = "agent_1"
        trade_item = "item_xyz"
        outcome = "accepted"
        capsule_data = {
            "values": ["sacrifice", "legacy"],
            "tags": ["strategic risk"],
        }
        event = self.simulator.simulate_trade_consequence(
            agent_id, trade_item, outcome, capsule_data)
        self.assertEqual(event["agent_id"], agent_id)
        self.assertEqual(event["trade_item"], trade_item)
        self.assertEqual(event["outcome"], outcome)
        self.assertIn("sacrifice", event["symbolic_tags"])
        self.assertIn("strategic risk", event["symbolic_tags"])
        self.assertIn("legacy", event["symbolic_tags"])
        self.assertIn("Blockchain event for trade", event["description"])

    def test_generate_symbolic_tags_empty(self):
        tags = self.simulator._generate_symbolic_tags(None)
        self.assertEqual(tags, [])


class TestTradeEvaluatorIntegration(unittest.TestCase):
    def setUp(self):
        # Mock pinecone and environment variables to avoid errors
        import os
        from unittest.mock import patch, MagicMock

        patcher_env = patch.dict(os.environ, {
            "PINECONE_API_KEY": "fake_key",
            "PINECONE_ENVIRONMENT": "fake_env"
        })
        patcher_env.start()
        self.addCleanup(patcher_env.stop)

        # Update to use the new Pinecone client pattern
        patcher_pinecone = patch("memory.agent_memory.Pinecone")
        self.mock_pinecone = patcher_pinecone.start()
        mock_pc_instance = MagicMock()
        self.mock_pinecone.return_value = mock_pc_instance
        mock_pc_instance.list_indexes.return_value = []
        mock_index = MagicMock()
        mock_pc_instance.Index.return_value = mock_index
        self.addCleanup(patcher_pinecone.stop)
        
        self.evaluator = TradeEvaluator()
        self.agent = Agent(capsule_data={"capsule_id": "agent123", "values": ["opportunity"], "tags": ["legacy"], "goal": "maximize growth"})
        self.agent.identifier = "agent_42"

    def test_evaluate_trade_triggers_blockchain_ops(self):
        offer = {
            "item_name": "rare_artifact",
            "item_tags": ["opportunity", "legacy"],
        }
        evaluation, accept = self.evaluator.evaluate_trade(self.agent, offer)
        self.assertIsInstance(evaluation, dict)
        self.assertIn("alignment_score", evaluation)
        self.assertTrue(isinstance(accept, bool))
        # Check that blockchain events were recorded
        events = self.evaluator.blockchain_ops_simulator.blockchain_events
        self.assertTrue(any(event["trade_item"] ==
                        "rare_artifact" for event in events))
        # Check that trade record was added to memory
        trade_history = self.evaluator.agent_memory.get_trade_history(
            self.agent.identifier)
        self.assertTrue(
            any(record["trade_item"] == "rare_artifact" for record in trade_history))


if __name__ == "__main__":
    unittest.main()
