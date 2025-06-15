import unittest
from unittest.mock import MagicMock, patch
from agents.nft.red_paperclip_nft import NFTAssignmentManager


class TestNFTAssignmentManager(unittest.TestCase):
    def setUp(self):
        # Mock WalletManager and CapsuleRegistry
        self.mock_wallet_manager = MagicMock()
        self.mock_capsule_registry = MagicMock()
        self.nft_manager = NFTAssignmentManager(
            wallet_manager=self.mock_wallet_manager,
            capsule_registry=self.mock_capsule_registry
        )

    def test_mint_and_assign_nft_success(self):
        # Setup mock wallet address
        wallet_address = "0xABC123"
        self.mock_wallet_manager.get_wallet_address.return_value = wallet_address

        # Patch PinataNFTStorage.store_metadata to return a fake IPFS hash
        with patch.object(self.nft_manager._pinata_storage, "store_metadata", return_value="QmFakeIpfsHash"):
            result = self.nft_manager.mint_and_assign_nft()

        # Assert wallet address returned
        self.assertEqual(result, wallet_address)

        # Assert NFT assigned
        self.assertTrue(self.nft_manager.is_nft_assigned(wallet_address))

        # Assert capsule created with correct tags and metadata_hash
        self.mock_capsule_registry.create_capsule.assert_called_once()
        args, kwargs = self.mock_capsule_registry.create_capsule.call_args
        capsule_data = args[0] if args else kwargs
        self.assertIn("nft", capsule_data.get("tags", []))
        self.assertIn("red-paperclip", capsule_data.get("tags", []))
        self.assertIn("soulbound", capsule_data.get("tags", []))
        self.assertEqual(capsule_data.get("agent_id"), wallet_address)
        self.assertIn("metadata_hash", capsule_data.get("values", {}))
        self.assertEqual(capsule_data["values"]
                         ["metadata_hash"], "QmFakeIpfsHash")

    def test_mint_and_assign_nft_fallback_to_s3(self):
        wallet_address = "0xDEF456"
        self.mock_wallet_manager.get_wallet_address.return_value = wallet_address

        # Patch store_metadata to simulate Pinata failure and S3 fallback success
        with patch.object(self.nft_manager._pinata_storage, "store_metadata", return_value="s3://bucket/key.json"):
            result = self.nft_manager.mint_and_assign_nft()

        self.assertEqual(result, wallet_address)
        self.mock_capsule_registry.create_capsule.assert_called_once()

    def test_mint_and_assign_nft_storage_failure(self):
        wallet_address = "0xFAIL"
        self.mock_wallet_manager.get_wallet_address.return_value = wallet_address

        # Patch store_metadata to simulate failure (returns None)
        with patch.object(self.nft_manager._pinata_storage, "store_metadata", return_value=None):
            result = self.nft_manager.mint_and_assign_nft()

        self.assertIsNone(result)
        self.mock_capsule_registry.create_capsule.assert_not_called()

    def test_mint_and_assign_nft_already_assigned(self):
        wallet_address = "0xALREADY"
        self.mock_wallet_manager.get_wallet_address.return_value = wallet_address

        # Pre-assign NFT
        self.nft_manager._assignments[wallet_address] = True

        # Call mint_and_assign_nft
        result = self.nft_manager.mint_and_assign_nft()

        # Should return wallet address without creating new capsule
        self.assertEqual(result, wallet_address)
        self.mock_capsule_registry.create_capsule.assert_not_called()

    def test_mint_and_assign_nft_no_wallet(self):
        # WalletManager returns None
        self.mock_wallet_manager.get_wallet_address.return_value = None

        # Call mint_and_assign_nft
        result = self.nft_manager.mint_and_assign_nft()

        # Should return None and not assign NFT
        self.assertIsNone(result)
        self.mock_capsule_registry.create_capsule.assert_not_called()


if __name__ == "__main__":
    unittest.main()
