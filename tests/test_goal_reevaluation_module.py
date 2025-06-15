import unittest
from registry.capsule_registry import CapsuleRegistry, Capsule
from memory.agent_memory import AgentMemory
from agents.goal_reevaluation_module import GoalReevaluationModule


class TestGoalReevaluationModule(unittest.TestCase):
    def setUp(self):
        import os
        from unittest.mock import patch, MagicMock

        patcher_env = patch.dict(os.environ, {
            "PINECONE_API_KEY": "fake_key",
            "PINECONE_ENVIRONMENT": "fake_env"
        })
        patcher_env.start()
        self.addCleanup(patcher_env.stop)

        # Mock Pinecone
        patcher_pinecone = patch("memory.agent_memory.Pinecone")
        mock_pinecone_class = patcher_pinecone.start()
        mock_pc_instance = MagicMock()
        mock_pinecone_class.return_value = mock_pc_instance
        mock_pc_instance.list_indexes.return_value = []
        mock_index = MagicMock()
        mock_pc_instance.Index.return_value = mock_index
        self.addCleanup(patcher_pinecone.stop)

        self.capsule_registry = CapsuleRegistry()
        self.agent_memory = AgentMemory()
        self.module = GoalReevaluationModule(
            capsule_registry=self.capsule_registry,
            agent_memory=self.agent_memory,
            reevaluation_interval=1  # short interval for testing
        )

        # Create a test capsule
        self.capsule = self.capsule_registry.create_capsule(
            goal="Initial Goal",
            values={"motivation_score": 0},
            tags=["initial"],
            wallet_address="wallet123",
            public_snippet="Test snippet"
        )

    def test_reevaluate_capsule_updates_tags_and_motivation(self):
        # Before reevaluation
        self.assertIn("initial", self.capsule.tags)
        self.assertNotIn("reevaluated", self.capsule.tags)
        self.assertEqual(self.capsule.values["motivation_score"], 0)

        # Perform reevaluation
        self.module.reevaluate_capsule(self.capsule)

        # After reevaluation
        self.assertIn("reevaluated", self.capsule.tags)
        self.assertEqual(self.capsule.values["motivation_score"], 1)

        # Check that a trade record was added to memory
        trade_history = self.agent_memory.get_trade_history(
            self.capsule.capsule_id)
        self.assertTrue(
            any(record["trade_item"] == "Goal Reevaluation" for record in trade_history))

    def test_periodic_reevaluation_updates_capsules(self):
        # Start periodic reevaluation
        self.module.start_periodic_reevaluation()

        # Wait for a couple of intervals
        import time
        time.sleep(2.5)

        # Stop periodic reevaluation
        self.module.stop_periodic_reevaluation()

        # Check capsule updated
        updated_capsule = self.capsule_registry.get_capsule_by_id(
            self.capsule.capsule_id)
        self.assertIn("reevaluated", updated_capsule.tags)
        self.assertGreaterEqual(updated_capsule.values["motivation_score"], 1)

        # Check memory logs
        trade_history = self.agent_memory.get_trade_history(
            self.capsule.capsule_id)
        self.assertTrue(
            any(record["trade_item"] == "Goal Reevaluation" for record in trade_history))


if __name__ == "__main__":
    unittest.main()
