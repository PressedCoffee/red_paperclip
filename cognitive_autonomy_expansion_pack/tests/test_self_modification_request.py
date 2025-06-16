from unittest.mock import MagicMock
import unittest
from cognitive_autonomy_expansion_pack.self_modification_request import GenesisSelfModificationRequest


class TestGenesisSelfModificationRequest(unittest.TestCase):
    def setUp(self):
        self.mock_meta_reasoner = MagicMock()
        self.mock_lifecycle_manager = MagicMock()
        self.mock_snapshot_panel = MagicMock()
        self.mock_llm = MagicMock()
        self.mock_agent_memory = MagicMock()
        self.mock_capsule_registry = MagicMock()

        self.self_mod_request = GenesisSelfModificationRequest(
            meta_reasoner=self.mock_meta_reasoner,
            lifecycle_manager=self.mock_lifecycle_manager,
            llm=self.mock_llm,
            agent_memory=self.mock_agent_memory,
            capsule_registry=self.mock_capsule_registry,
            snapshot_panel=self.mock_snapshot_panel,
            live_mode=False,
        )

    def test_create_request(self):
        details = {"param": "value"}
        request = self.self_mod_request.create_request(
            "agent_1", details, requires_approval=True)
        self.assertEqual(request["agent_id"], "agent_1")
        self.assertEqual(request["modification_details"], details)
        self.assertEqual(request["status"], "pending")

    def test_review_request_approval_live_mode_invokes_llm_and_logs(self):
        self.self_mod_request.live_mode = True
        self.self_mod_request.llm = self.mock_llm
        self.self_mod_request.agent_memory = self.mock_agent_memory
        self.mock_llm.invoke.return_value = "approve"
        request = self.self_mod_request.create_request(
            "agent_1", {"param": "value"})

        approved = self.self_mod_request.review_request(request)

        self.mock_llm.invoke.assert_called_once()
        self.mock_agent_memory.log_interaction.assert_any_call({
            "type": "llm_prompt",
            "content": unittest.mock.ANY,
            "timestamp": unittest.mock.ANY,
            "correlation_id": unittest.mock.ANY,
        })
        self.mock_agent_memory.log_interaction.assert_any_call({
            "type": "llm_completion",
            "content": "approve",
            "timestamp": unittest.mock.ANY,
            "correlation_id": unittest.mock.ANY,
        })
        self.assertTrue(approved)
        self.mock_capsule_registry.create_capsule.assert_called_once()
        self.mock_lifecycle_manager.apply_modification.assert_called_once()
        self.mock_snapshot_panel.update_self_mod_request.assert_called()

    def test_review_request_rejection_live_mode(self):
        self.self_mod_request.live_mode = True
        self.self_mod_request.llm = self.mock_llm
        self.self_mod_request.agent_memory = self.mock_agent_memory
        self.mock_llm.invoke.return_value = "reject"
        request = self.self_mod_request.create_request(
            "agent_1", {"param": "value"})

        approved = self.self_mod_request.review_request(request)

        self.assertFalse(approved)
        self.mock_lifecycle_manager.apply_modification.assert_not_called()
        self.mock_snapshot_panel.update_self_mod_request.assert_called()

    def test_review_request_fallback(self):
        self.self_mod_request.live_mode = False
        request = self.self_mod_request.create_request(
            "agent_1", {"param": "value"}, requires_approval=False)

        approved = self.self_mod_request.review_request(
            request, reviewer_comments="Looks good")

        self.assertTrue(approved)
        self.mock_lifecycle_manager.apply_modification.assert_called_once()
        self.mock_snapshot_panel.update_self_mod_request.assert_called()

    def test_get_snapshot_metadata(self):
        request = self.self_mod_request.create_request(
            "agent_1", {"param": "value"})
        self.self_mod_request.review_request(request, approved=True)
        metadata = self.self_mod_request.get_snapshot_metadata()
        self.assertEqual(metadata["self_mod_request_status"], "approved")
        self.assertEqual(metadata["audit_trail_length"], 2)


if __name__ == "__main__":
    unittest.main()
