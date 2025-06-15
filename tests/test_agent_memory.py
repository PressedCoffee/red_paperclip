import unittest
from unittest.mock import patch, MagicMock
from memory.agent_memory import AgentMemory, TradeRecord


class TestAgentMemory(unittest.TestCase):

    @patch("memory.agent_memory.Pinecone")
    def setUp(self, mock_pinecone_class):
        # Mock the Pinecone class and its instance
        mock_pc_instance = MagicMock()
        mock_pinecone_class.return_value = mock_pc_instance
        mock_pc_instance.list_indexes.return_value = []
        mock_index = MagicMock()
        mock_pc_instance.Index.return_value = mock_index
        self.mock_index = mock_index

        # Patch environment variables
        patcher_api_key = patch.dict("os.environ", {
                                     "PINECONE_API_KEY": "fake_key", "PINECONE_ENVIRONMENT": "fake_env"})
        patcher_api_key.start()
        self.addCleanup(patcher_api_key.stop)

        self.agent_memory = AgentMemory()

    def test_add_trade_record_indexes_in_pinecone(self):
        agent_id = "agent1"
        trade_item = "item1"
        outcome = "accepted"

        self.agent_memory.add_trade_record(agent_id, trade_item, outcome)

        # Check that trade record is added in memory
        self.assertIn(agent_id, self.agent_memory.agent_trade_history)
        self.assertEqual(
            len(self.agent_memory.agent_trade_history[agent_id]), 1)

        # Check that upsert was called on Pinecone index
        self.mock_index.upsert.assert_called_once()
        args, kwargs = self.mock_index.upsert.call_args
        vectors = kwargs.get("vectors")
        self.assertEqual(len(vectors), 1)
        record_id, embedding, metadata = vectors[0]
        self.assertTrue(record_id.startswith(agent_id))
        self.assertIsInstance(metadata, dict)
        self.assertIn("trade_item", metadata)

    def test_recall_context_returns_metadata(self):
        agent_id = "agent1"
        query = "some query"

        # Setup mock query response
        self.mock_index.query.return_value = {
            "matches": [
                {"metadata": {"trade_item": "item1", "outcome": "accepted"}},
                {"metadata": {"trade_item": "item2", "outcome": "rejected"}},
            ]
        }

        results = self.agent_memory.recall_context(agent_id, query, top_k=2)

        self.mock_index.query.assert_called_once()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["trade_item"], "item1")
        self.assertEqual(results[1]["outcome"], "rejected")


if __name__ == "__main__":
    unittest.main()
