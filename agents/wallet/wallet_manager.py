from typing import Optional
from registry.capsule_registry import CapsuleRegistry
import os

try:
    from coinbase_agentkit import AgentKit, AgentKitConfig, CdpEvmServerWalletProvider, CdpEvmServerWalletProviderConfig
    print("✅ Successfully imported coinbase_agentkit modules")
    COINBASE_AVAILABLE = True
except ImportError:
    print("⚠️ Warning: coinbase_agentkit not found. Using mock implementations.")
    COINBASE_AVAILABLE = False    # Fallback mocks for local dev or CI

    class CdpEvmServerWalletProviderConfig:
        def __init__(self, **kwargs):
            self.config = kwargs

    class CdpEvmServerWalletProvider:
        def __init__(self, config):
            self.config = config

    class AgentKitConfig:
        def __init__(self, wallet_provider):
            self.wallet_provider = wallet_provider

    class AgentKit:
        def __init__(self, config):
            self.config = config
            self.wallets = self.MockWallets()

        class MockWallets:
            def create(self, network=None, **kwargs):
                # Generate a mock wallet address
                import hashlib
                import time
                seed = f"{network}_{time.time()}_{hash(str(kwargs))}"
                return "0x" + hashlib.md5(seed.encode()).hexdigest()[:40]

BASE_SEPOLIA_NETWORK = "base-sepolia"


class WalletManager:
    """
    Manages wallet creation and storage using AgentKit.
    """

    def __init__(self, capsule_registry: CapsuleRegistry):
        self._wallet_address: Optional[str] = None
        self._capsule_registry = capsule_registry

        api_key_id = os.getenv("CDP_API_KEY_ID")
        api_key_secret = os.getenv("CDP_API_KEY_SECRET")

        provider_config = CdpEvmServerWalletProviderConfig(
            api_key_id=api_key_id,
            api_key_private=api_key_secret,
            network_id=BASE_SEPOLIA_NETWORK
        )
        self._wallet_provider = CdpEvmServerWalletProvider(provider_config)
        self._agentkit = AgentKit(AgentKitConfig(
            wallet_provider=self._wallet_provider))

    def create_wallet(self) -> str:
        self._wallet_address = self._agentkit.wallets.create(
            network=BASE_SEPOLIA_NETWORK)

        # Create capsule using the expected dictionary format
        capsule_data = {
            "agent_id": self._wallet_address,  # Use wallet address as agent_id
            "goal": "Genesis Capsule for wallet storage",
            "values": {},
            "tags": ["genesis", "wallet"],
            "wallet_address": self._wallet_address,
            "public_snippet": "Wallet created and stored in Genesis Capsule."
        }
        self._capsule_registry.create_capsule(capsule_data)
        return self._wallet_address

    def get_wallet_address(self) -> Optional[str]:
        return self._wallet_address
