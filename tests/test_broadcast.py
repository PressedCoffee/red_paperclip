import unittest
from agents.agent import Agent, AgentIdentity
from visibility.visibility_preferences import VisibilityPreferences


class MockVisibilityPreferences:
    def __init__(self, can_view_result=True):
        self.allow_broadcast = can_view_result

    def can_view(self, category):
        return self.allow_broadcast


class TestAgentBroadcast(unittest.TestCase):
    def setUp(self):
        capsule_data = {
            "capsule_id": "capsule123",
            "goal": "Test Goal",
            "values": ["value1", "value2"],
            "tags": ["tag1", "tag2"],
            "wallet_address": "wallet123",
            "nft_assigned": True,
            "public_snippet": "Public Persona"
        }
        agent_identity = AgentIdentity(
            agent_id="agent123", capsule_id="capsule123")
        self.agent = Agent(capsule_data, agent_identity)

    def test_broadcast_success(self):
        visibility_prefs = MockVisibilityPreferences(can_view_result=True)
        message = "This is a test broadcast."
        result = self.agent.broadcast_to_public(message, visibility_prefs)
        self.assertTrue(result)

    def test_broadcast_failure_due_to_visibility(self):
        visibility_prefs = MockVisibilityPreferences(can_view_result=False)
        message = "This broadcast should fail."
        result = self.agent.broadcast_to_public(message, visibility_prefs)
        self.assertFalse(result)

    def test_broadcast_message_content(self):
        visibility_prefs = MockVisibilityPreferences(can_view_result=True)
        message = "Check message content."
        # Capture printed output
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.agent.broadcast_to_public(message, visibility_prefs)
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("agent123", output)
        self.assertIn("Public Persona", output)
        self.assertIn(message, output)


class AgentKit:
    def __init__(self, config):
        self.wallets = self.WalletManager()

    class WalletManager:
        def create(self, network):
            return "0x1234567890abcdef"


class AgentKitConfig:
    def __init__(self, wallet_provider):
        self.wallet_provider = wallet_provider


class CdpEvmServerWalletProvider:
    def __init__(self, config):
        self.config = config


class CdpEvmServerWalletProviderConfig:
    def __init__(self, network):
        self.network = network


if __name__ == "__main__":
    unittest.main()
