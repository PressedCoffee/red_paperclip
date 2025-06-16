from unittest.mock import MagicMock
import unittest
from cognitive_autonomy_expansion_pack.reality_query_interface import CapsuleRealityQueryInterface
import sys
import types

# Mock pinecone module to avoid import errors in tests
mock_pinecone = types.ModuleType("pinecone")
sys.modules["pinecone"] = mock_pinecone


class TestCapsuleRealityQueryInterface(unittest.TestCase):
    def setUp(self):
        self.mock_memory = MagicMock()
        self.mock_memory.store_query_response = MagicMock()
        self.mock_memory.store_llm_interaction = MagicMock()

        self.mock_trading_logic = MagicMock()

        self.mock_snapshot_panel = MagicMock()
        self.mock_snapshot_panel.update_query_log = MagicMock()

        self.mock_llm = MagicMock()

        self.interface_live = CapsuleRealityQueryInterface(
            agent_memory=self.mock_memory,
            trading_logic=self.mock_trading_logic,
            live_mode=True,
            snapshot_panel=self.mock_snapshot_panel,
            llm_client=self.mock_llm,
        )

        self.interface_simulated = CapsuleRealityQueryInterface(
            agent_memory=self.mock_memory,
            trading_logic=self.mock_trading_logic,
            live_mode=False,
            snapshot_panel=self.mock_snapshot_panel,
            llm_client=None,
        )

    def test_simulated_query(self):
        query = "What is the market trend?"
        response = self.interface_simulated.query_reality(query)
        self.assertIn("summary", response)
        self.assertTrue(response["summary"].startswith("Simulated response"))

    def test_live_query_invokes_llm_and_logs(self):
        query = "Live data query"
        self.mock_llm.invoke.return_value = "Live response"
        response = self.interface_live.query_reality(query)
        self.mock_llm.invoke.assert_called_once()
        self.mock_memory.store_llm_interaction.assert_called_once()
        log_call_args = self.mock_memory.store_llm_interaction.call_args[0][0]
        self.assertIn("prompt", log_call_args)
        self.assertIn("completion", log_call_args)
        self.assertIn("timestamp", log_call_args)
        self.assertIn("correlation_id", log_call_args)
        self.assertIn("completion", response)
        self.assertIn("correlation_id", response)

    def test_logging_and_snapshot_update(self):
        query = "Test query"
        self.interface_simulated.query_reality(query)
        self.mock_memory.store_query_response.assert_called()
        self.mock_snapshot_panel.update_query_log.assert_called()

    def test_get_snapshot_metadata(self):
        self.interface_simulated.query_reality("Test")
        metadata = self.interface_simulated.get_snapshot_metadata()
        self.assertIn("last_query", metadata)
        self.assertIn("query_log_length", metadata)
        self.assertFalse(metadata["live_mode"])


if __name__ == "__main__":
    unittest.main()
