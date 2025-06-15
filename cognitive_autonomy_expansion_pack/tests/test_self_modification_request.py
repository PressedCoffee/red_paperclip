from unittest.mock import MagicMock
import unittest
from cognitive_autonomy_expansion_pack.self_modification_request import GenesisSelfModificationRequest
import sys
import types

# Mock pinecone module to avoid import errors in tests
mock_pinecone = types.ModuleType("pinecone")
sys.modules["pinecone"] = mock_pinecone


class TestGenesisSelfModificationRequest(unittest.TestCase):
    def setUp(self):
        self.mock_meta_reasoner = MagicMock()
        self.mock_lifecycle_manager = MagicMock()
        self.mock_snapshot_panel = MagicMock()

        self.self_mod_request = GenesisSelfModificationRequest(
            meta_reasoner=self.mock_meta_reasoner,
            lifecycle_manager=self.mock_lifecycle_manager,
            snapshot_panel=self.mock_snapshot_panel,
        )

    def test_create_request(self):
        details = {"param": "value"}
        request = self.self_mod_request.create_request(
            "agent_1", details, requires_approval=True)
        self.assertEqual(request["agent_id"], "agent_1")
        self.assertEqual(request["modification_details"], details)
        self.assertEqual(request["status"], "pending")

    def test_review_request_approval(self):
        request = self.self_mod_request.create_request(
            "agent_1", {"param": "value"})
        self.self_mod_request.review_request(
            request, approved=True, reviewer_comments="Looks good")
        self.assertEqual(request["status"], "approved")
        self.mock_lifecycle_manager.apply_modification.assert_called_once()
        self.mock_snapshot_panel.update_self_mod_request.assert_called()

    def test_review_request_rejection(self):
        request = self.self_mod_request.create_request(
            "agent_1", {"param": "value"})
        self.self_mod_request.review_request(
            request, approved=False, reviewer_comments="Rejecting")
        self.assertEqual(request["status"], "rejected")
        self.mock_lifecycle_manager.apply_modification.assert_not_called()
        self.mock_snapshot_panel.update_self_mod_request.assert_called()

    def test_get_snapshot_metadata(self):
        request = self.self_mod_request.create_request(
            "agent_1", {"param": "value"})
        self.self_mod_request.review_request(request, approved=True)
        metadata = self.self_mod_request.get_snapshot_metadata()
        self.assertEqual(metadata["self_mod_request_status"], "approved")
        # create + review logged
        self.assertEqual(metadata["audit_trail_length"], 2)


if __name__ == "__main__":
    unittest.main()
