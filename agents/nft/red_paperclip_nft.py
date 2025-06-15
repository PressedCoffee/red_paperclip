import logging
from typing import Dict, Optional
from agents.wallet.wallet_manager import WalletManager
from registry.capsule_registry import CapsuleRegistry
from agents.nft.pinata_nft_storage import PinataNFTStorage


class RedPaperclipNFT:
    """
    Represents the soulbound Red Paperclip NFT schema.
    """

    def __init__(self):
        self.schema = {
            "name": "Red Paperclip",
            "description": "Soulbound NFT representing the legendary Red Paperclip.",
            "attributes": {
                "soulbound": True,
                "origin": "Genesis Pad",
                "rarity": "unique"
            }
        }


class NFTAssignmentManager:
    """
    Manages assignment of the Red Paperclip NFT to wallet addresses.
    """

    def __init__(self, wallet_manager: WalletManager, capsule_registry: CapsuleRegistry):
        # Records assignment status keyed by wallet address
        self._assignments: Dict[str, bool] = {}
        self._wallet_manager = wallet_manager
        self._capsule_registry = capsule_registry
        self._nft = RedPaperclipNFT()
        self._pinata_storage = PinataNFTStorage()

    def mint_and_assign_nft(self) -> Optional[str]:
        """
        Mint and assign the Red Paperclip NFT to the wallet address retrieved from WalletManager.
        Store NFT metadata in the agent's Genesis Capsule, pinning to Pinata with fallback to S3.
        """
        wallet_address = self._wallet_manager.get_wallet_address()
        if not wallet_address:
            logging.error("No wallet address available for NFT assignment.")
            return None

        if self.is_nft_assigned(wallet_address):
            logging.info(f"NFT already assigned to wallet {wallet_address}.")
            return wallet_address

        # Simulate minting and assignment
        success = self.assign_nft(wallet_address)
        if not success:
            logging.error(f"Failed to assign NFT to wallet {wallet_address}.")
            return None

        # Pin/store metadata using PinataNFTStorage
        ipfs_or_s3_hash = self._pinata_storage.store_metadata(self._nft.schema)
        if not ipfs_or_s3_hash:
            logging.error(
                "Failed to store NFT metadata in Pinata and fallback storage.")
            return None

        # Store NFT metadata in Genesis Capsule with IPFS hash or fallback URL
        capsule_data = {
            "agent_id": wallet_address,
            "goal": "Store Red Paperclip NFT metadata",
            "values": {**self._nft.schema, "metadata_hash": ipfs_or_s3_hash},
            "tags": ["nft", "red-paperclip", "soulbound"],
            "public_snippet": "Soulbound Red Paperclip NFT assigned and metadata stored."
        }
        self._capsule_registry.create_capsule(capsule_data)

        logging.info(
            f"NFT metadata stored with hash {ipfs_or_s3_hash} for wallet {wallet_address}.")
        return wallet_address

    def assign_nft(self, wallet_address: str) -> bool:
        """
        Assign the Red Paperclip NFT to a wallet address.

        Args:
            wallet_address (str): The wallet address to assign the NFT to.

        Returns:
            bool: True if assignment is successful, False otherwise.
        """
        # Simulate successful assignment
        self._assignments[wallet_address] = True
        return True

    def is_nft_assigned(self, wallet_address: str) -> bool:
        """
        Check if the NFT has been assigned to the given wallet address.

        Args:
            wallet_address (str): The wallet address to check.

        Returns:
            bool: True if NFT assigned, False otherwise.
        """
        return self._assignments.get(wallet_address, False)
