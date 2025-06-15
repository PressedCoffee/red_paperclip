from typing import Optional, Dict, Any, List
from agents.badge_xp_system import BadgeXPSystem
from registry.capsule_registry import Capsule
from visibility.visibility_preferences import VisibilityPreferences
import requests
import logging
import uuid
import time

from agents.wallet.wallet_manager import WalletManager
from agents.x402_payment_handler import X402PaymentHandler


class AgentIdentity:
    """
    Represents the identity of an agent linked to a Genesis Capsule.
    Includes stubs for wallet address, NFT assignment status, personality traits, and placeholders for future integrations.
    """

    def __init__(
        self,
        agent_id: str,
        capsule_id: str,
        wallet_address: Optional[str] = None,
        nft_assigned: bool = False,
        personality_traits: Optional[Dict[str, Any]] = None,
        llm_profile: Optional[Dict[str, Any]] = None,
        pinecone_memory: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize an AgentIdentity instance.

        :param agent_id: Unique identifier for the agent.
        :param capsule_id: The linked Genesis Capsule ID.
        :param wallet_address: Placeholder for CDP Wallet address.
        :param nft_assigned: Status of Red Paperclip NFT assignment.
        :param personality_traits: Dictionary of personality traits.
        :param llm_profile: Placeholder for future LLM profile integration.
        :param pinecone_memory: Placeholder for future Pinecone memory integration.
        """
        self.agent_id = agent_id
        self.capsule_id = capsule_id
        self.wallet_address = wallet_address
        self.nft_assigned = nft_assigned
        self.personality_traits = personality_traits or {}
        self.llm_profile = llm_profile or {}
        self.pinecone_memory = pinecone_memory or {}


class Agent:
    """
    Basic Agent scaffolding class instantiated with Genesis Capsule data.
    Exposes capsule attributes for downstream logic.
    """

    def __init__(self, capsule_data: Dict[str, Any], agent_identity: Optional[AgentIdentity] = None, badge_xp_system: Optional[BadgeXPSystem] = None):
        """
        Initialize an Agent instance.

        :param capsule_data: Dictionary containing Genesis Capsule data.
        :param agent_identity: Optional AgentIdentity instance linked to this agent.
        :param badge_xp_system: Optional BadgeXPSystem instance for badge and XP management.
        """
        self.capsule_data = capsule_data
        self.agent_identity = agent_identity
        self.badge_xp_system = badge_xp_system

        # Initialize WalletManager and X402PaymentHandler for payment handling
        # Pass None or actual registry if available
        self.wallet_manager = WalletManager(capsule_registry=None)
        self.x402_payment_handler = X402PaymentHandler(self.wallet_manager)

        # Expose capsule attributes for convenience
        self.capsule_id = capsule_data.get("capsule_id")
        self.goal = capsule_data.get("goal")
        self.values = capsule_data.get("values")
        self.tags = capsule_data.get("tags")
        self.wallet_address = capsule_data.get("wallet_address")
        self.nft_assigned = capsule_data.get("nft_assigned", False)
        self.public_snippet = capsule_data.get("public_snippet")

    def get_agent_id(self) -> Optional[str]:
        """
        Get the unique agent ID if available.

        :return: Agent ID string or None.
        """
        if self.agent_identity:
            return self.agent_identity.agent_id
        return None

    @property
    def wallet_address(self) -> Optional[str]:
        """
        Get the wallet address from the agent identity if available.

        :return: Wallet address string or None.
        """
        if self.agent_identity:
            return self.agent_identity.wallet_address
        return None

    @wallet_address.setter
    def wallet_address(self, address: Optional[str]):
        """
        Set the wallet address in the agent identity.

        :param address: Wallet address string or None.
        """
        if self.agent_identity:
            self.agent_identity.wallet_address = address

    @property
    def nft_assigned(self) -> bool:
        """
        Get the NFT assignment status from the agent identity if available.

        :return: True if NFT assigned, False otherwise.
        """
        if self.agent_identity:
            return self.agent_identity.nft_assigned
        return False

    @nft_assigned.setter
    def nft_assigned(self, assigned: bool):
        """
        Set the NFT assignment status in the agent identity.

        :param assigned: Boolean status of NFT assignment.
        """
        if self.agent_identity:
            self.agent_identity.nft_assigned = assigned

    def broadcast_to_public(self, message: str, visibility_prefs: "VisibilityPreferences", category: str = "show_public_snippet") -> bool:
        """
        Scaffold method to publish trade reflections or goal shifts respecting visibility settings.
        Integrates references to agent public personas from Snapshot Panel for continuity.

        :param message: The content to broadcast.
        :param visibility_prefs: VisibilityPreferences instance of the viewer or public.
        :param category: Visibility category to check for permission.
        :return: True if broadcast was successful, False otherwise.
        """
        # Check if broadcasting is allowed based on visibility preferences
        if not visibility_prefs.can_view(category):
            # Broadcasting not allowed due to visibility restrictions
            return False

        # Reference public persona data (simulate fetching from Snapshot Panel)
        public_persona = getattr(
            self, "public_snippet", None) or "[No Public Persona]"

        # Simulate broadcast message composition
        broadcast_message = f"Broadcast from Agent {self.get_agent_id() or 'Unknown'} ({public_persona}): {message}"

        # Simulate broadcasting (e.g., logging or storing broadcast)
        print(broadcast_message)  # Placeholder for actual broadcast mechanism

        # Indicate successful broadcast
        return True

    def award_badge(self, milestone: str, xp_amount: int) -> Optional[Capsule]:
        """
        Award a badge to this agent for a milestone and add XP.

        :param milestone: The milestone achieved.
        :param xp_amount: XP to add for this milestone.
        :return: The created Capsule representing the badge, or None if badge_xp_system not set.
        """
        if self.badge_xp_system and self.get_agent_id():
            return self.badge_xp_system.award_badge(self.get_agent_id(), milestone, xp_amount)
        return None

    def get_xp(self) -> int:
        """
        Get the total XP accumulated by this agent.

        :return: Total XP, or 0 if badge_xp_system not set.
        """
        if self.badge_xp_system and self.get_agent_id():
            return self.badge_xp_system.get_agent_xp(self.get_agent_id())
        return 0

    def get_badges(self) -> List[Capsule]:
        """
        Get the list of badges earned by this agent.

        :return: List of badge Capsules, or empty list if badge_xp_system not set.
        """
        if self.badge_xp_system and self.get_agent_id():
            return self.badge_xp_system.get_agent_badges(self.get_agent_id())
        return []


class AgentLifecycleManager:
    """
    Placeholder class for managing agent lifecycle and modifications.
    """

    def __init__(self, agent: Agent):
        """
        Initialize the AgentLifecycleManager with the agent instance.

        :param agent: The agent instance to manage.
        """
        self.agent = agent

    def apply_modification(self, change: dict):
        """
        Apply a modification to the agent lifecycle.

        :param change: The modification details.
        """
        # Example: could update capsule or traits later
        print(
            f"[AgentLifecycleManager] Applied modification: '{change}' for agent {self.agent.agent_id}")

    def get_resource_with_x402_retry(self, url: str, max_retries: int = 1) -> Optional[requests.Response]:
        """
        Make a GET request to the given URL, handling HTTP 402 Payment Required responses
        by parsing payment parameters, signing payment authorization, and retrying with X-PAYMENT header.

        Args:
            url (str): The resource URL to fetch.
            max_retries (int): Maximum number of retries on 402 responses.

        Returns:
            requests.Response or None: The successful response or None if failed.
        """
        EXPERIMENTAL_FEATURES = {
            "x402": True}  # This should be imported or configured elsewhere

        if not EXPERIMENTAL_FEATURES.get("x402", False):
            # Feature disabled, just do a normal GET
            try:
                response = requests.get(url)
                return response
            except Exception as e:
                logging.error(f"Error fetching resource {url}: {e}")
                return None

        attempt = 0
        while attempt <= max_retries:
            try:
                response = requests.get(url)
            except Exception as e:
                logging.error(f"Error fetching resource {url}: {e}")
                return None

            if response.status_code != 402:
                # Success or other error, return response
                return response

            # Handle 402 Payment Required
            payment_params = self.x402_payment_handler.parse_402_response(
                response.text)
            if not payment_params:
                logging.error(
                    f"Failed to parse payment parameters from 402 response for URL {url}")
                return response

            signature = self.x402_payment_handler.sign_payment_authorization(
                payment_params)
            if not signature:
                logging.error(
                    f"Failed to sign payment authorization for URL {url}")
                return response

            payment_header = self.x402_payment_handler.construct_payment_header(
                signature, payment_params)

            # Log payment attempt
            correlation_id = str(uuid.uuid4())
            logging.info(
                f"Payment attempt {attempt+1} for URL {url} with correlation_id {correlation_id}")

            # Retry with X-PAYMENT header
            try:
                response = requests.get(url, headers=payment_header)
            except Exception as e:
                logging.error(
                    f"Error retrying resource {url} with payment header: {e}")
                return None

            if response.status_code == 200:
                logging.info(
                    f"Payment successful for URL {url} with correlation_id {correlation_id}")
                return response
            else:
                logging.warning(
                    f"Payment retry failed with status {response.status_code} for URL {url} correlation_id {correlation_id}")

            attempt += 1

        logging.error(f"Exceeded max retries for payment on URL {url}")
        return None
