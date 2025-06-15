import unittest
from unittest.mock import patch, MagicMock
from registry.capsule_registry import CapsuleRegistry
from agents.wallet.wallet_manager import WalletManager


class TestWalletManager(unittest.TestCase):

    def setUp(self):
        self.capsule_registry = CapsuleRegistry()
        self.wallet_manager = WalletManager(self.capsule_registry)

    @patch("agents.wallet.wallet_manager.AgentKit")
    def test_create_wallet_and_store_address(self, mock_agentkit):
        # Mock the AgentKit and its wallets.create() method
        mock_wallets = MagicMock()
        mock_wallet_address = "0xTestWalletAddress123"
        mock_wallets.create.return_value = mock_wallet_address
        mock_agentkit.return_value.wallets = mock_wallets

        # Create a new WalletManager instance to use the mocked AgentKit
        wallet_manager = WalletManager(self.capsule_registry)
        wallet_address = wallet_manager.create_wallet()

        # Assert the wallet address returned is the mocked address
        self.assertEqual(wallet_address, mock_wallet_address)

        # Assert the wallet address is stored in the WalletManager instance
        self.assertEqual(
            wallet_manager.get_wallet_address(), mock_wallet_address)

        # Assert the wallet address is stored in a Genesis Capsule in CapsuleRegistry
        capsules = self.capsule_registry.list_capsules()
        self.assertTrue(
            any(c.wallet_address == mock_wallet_address for c in capsules))


if __name__ == "__main__":
    unittest.main()
