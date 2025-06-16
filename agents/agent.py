from agents.x402_payment_handler import X402PaymentHandler
from agents.wallet.wallet_manager import WalletManager
import datetime
import time
import uuid
import logging
import requests
from cognitive_autonomy_expansion_pack.shared_llm_client import get_shared_llm
from cognitive_autonomy_expansion_pack.ugtt_module import CapsuleUGTT
# Import CapsuleRealityQueryInterface lazily to avoid circular imports
from config.trade_config import get_config, get_archetype_config, calculate_base_costs
from visibility.visibility_preferences import VisibilityPreferences
from registry.capsule_registry import Capsule
from agents.badge_xp_system import BadgeXPSystem
from typing import Optional, Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
        # Initialize WalletManager and X402PaymentHandler for payment handling
        self.badge_xp_system = badge_xp_system
        # Pass None or actual registry if available
        self.wallet_manager = WalletManager(capsule_registry=None)
        self.x402_payment_handler = X402PaymentHandler(self.wallet_manager)

        # Initialize cognitive modules for appraisal (lazy import to avoid circular dependencies)
        from cognitive_autonomy_expansion_pack.reality_query_interface import CapsuleRealityQueryInterface
        self.reality_query = CapsuleRealityQueryInterface()
        self.ugtt_module = CapsuleUGTT()
        self.config = get_config()

        # Initialize appraisal history
        self.appraisal_history = []
        self.nft_ownership_chain = []
        self.current_owned_nfts = []

        # Expose capsule attributes for convenience
        self.capsule_id = capsule_data.get("capsule_id")
        self.goal = capsule_data.get("goal")
        self.values = capsule_data.get("values")
        self.tags = capsule_data.get("tags")
        self.wallet_address = capsule_data.get("wallet_address")
        self.nft_assigned = capsule_data.get("nft_assigned", False)
        self.public_snippet = capsule_data.get("public_snippet")
        self.archetype = capsule_data.get(
            "archetype", "default")  # Agent archetype

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

    def generate_persuasion_pitch(self, target_capsule: Capsule, context: str = "trade", llm=None) -> Dict[str, Any]:
        """
        Generate a personalized persuasion pitch for the target capsule.

        Args:
            target_capsule: The target capsule to create a pitch for
            context: The context (trade, coalition, etc.)
            llm: Optional LLM for live pitch generation

        Returns:
            Dict containing pitch text, metadata, and cost information
        """
        correlation_id = str(uuid.uuid4())
        timestamp = time.time()

        # Feature flag for verbal exchange
        ENABLE_VERBAL_EXCHANGE = True

        if not ENABLE_VERBAL_EXCHANGE:
            return {
                "pitch": "",
                "cost": 0,
                "enabled": False,
                "correlation_id": correlation_id,
                "timestamp": timestamp
            }

        # Generate pitch using LLM if available, otherwise use template
        if llm:
            pitch_text = self._generate_llm_pitch(
                target_capsule, context, llm, correlation_id)
        else:
            pitch_text = self._generate_template_pitch(target_capsule, context)

        # Calculate and deduct cost
        cost_result = self._deduct_pitch_cost()

        pitch_result = {
            "pitch": pitch_text,
            "target_capsule_id": target_capsule.capsule_id,
            "context": context,
            "cost": cost_result["cost"],
            "payment_method": cost_result["method"],
            "success": cost_result["success"],
            "correlation_id": correlation_id,
            "timestamp": timestamp,
            "agent_id": self.get_agent_id() or self.capsule_id
        }

        # Log the pitch generation
        self._log_pitch_generation(pitch_result)

        return pitch_result

    def _generate_llm_pitch(self, target_capsule: Capsule, context: str, llm, correlation_id: str) -> str:
        """
        Generate persuasion pitch using LLM.
        """
        prompt = f"""
        You are an AI agent creating a persuasive pitch for a {context} proposal.
        
        Your Profile:
        - Goal: {self.goal}
        - Values: {self.values}
        - Tags: {self.tags}
        
        Target Agent Profile:
        - Goal: {target_capsule.goal}
        - Values: {target_capsule.values}
        - Tags: {target_capsule.tags}
        
        Create a 1-2 sentence persuasive pitch that:
        1. Shows alignment between both goals
        2. Uses psychological principles (reciprocity, urgency, mutual benefit)
        3. Is personalized to the target's values
        4. Sounds natural and compelling
        
        Respond with just the pitch text, no explanations.
        """

        try:
            response = llm.invoke(prompt)

            # Log LLM interaction
            if hasattr(self, 'memory') and self.memory:
                llm_log = {
                    "type": "llm_interaction",
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "correlation_id": correlation_id,
                    "prompt": "Persuasion pitch generation",
                    "completion": response,
                    "live_mode": True
                }
                self.memory.store_llm_interaction(llm_log)

            return response.strip()
        except Exception as e:
            # Fallback to template if LLM fails
            return self._generate_template_pitch(target_capsule, context)

    def _generate_template_pitch(self, target_capsule: Capsule, context: str) -> str:
        """
        Generate persuasion pitch using template fallback.
        """
        # Find common ground between goals and values
        common_values = []
        if hasattr(self, 'values') and hasattr(target_capsule, 'values'):
            self_values = set(self.values.keys()) if isinstance(
                self.values, dict) else set()
            target_values = set(target_capsule.values.keys()) if isinstance(
                target_capsule.values, dict) else set()
            common_values = list(self_values.intersection(target_values))

        # Template pitches based on context
        templates = {
            "trade": [
                f"I believe this {context} aligns perfectly with both our goals of {self.goal} and {target_capsule.goal}. Let's create mutual value together!",
                f"Given our shared focus on {', '.join(common_values[:2]) if common_values else 'growth'}, this {context} offers immediate benefits for both of us.",
                f"This {context} opportunity combines your expertise in {target_capsule.goal} with my focus on {self.goal} - a perfect synergy!"
            ],
            "coalition": [
                f"Together, we can achieve more than either of us could alone. Our combined goals of {self.goal} and {target_capsule.goal} create powerful synergies.",
                f"I see great potential in uniting our efforts - your {target_capsule.goal} expertise with my {self.goal} focus could be game-changing.",
                f"This coalition leverages our shared values around {', '.join(common_values[:2]) if common_values else 'excellence'} for extraordinary results."
            ]
        }

        # Select appropriate template
        context_templates = templates.get(context, templates["trade"])
        return context_templates[hash(str(target_capsule.capsule_id)) % len(context_templates)]

    def _deduct_pitch_cost(self) -> Dict[str, Any]:
        """
        Deduct cost for generating a pitch (USDC or XP).
        """
        cost_usdc = 0.01  # 1 cent USD
        cost_xp = 5

        # Try USDC payment first
        try:
            if self.x402_payment_handler:
                # Simplified payment deduction
                payment_result = {"success": True,
                                  "method": "USDC", "cost": cost_usdc}
                return payment_result
        except Exception as e:
            pass

        # Fallback to XP deduction
        try:
            if self.badge_xp_system:
                current_xp = self.badge_xp_system.get_current_xp(
                    self.get_agent_id() or self.capsule_id)
                if current_xp >= cost_xp:
                    # Deduct XP (negative grant)
                    from agents.badge_xp_system import grant_xp
                    grant_xp(self.get_agent_id() or self.capsule_id, -
                             cost_xp, "Persuasion pitch cost")
                    return {"success": True, "method": "XP", "cost": cost_xp}
                else:
                    return {"success": False, "method": "XP", "cost": cost_xp, "reason": "Insufficient XP"}
        except Exception as e:
            pass

        # If both payment methods fail, allow free pitch (could be configured differently)
        return {"success": True, "method": "FREE", "cost": 0, "reason": "Payment systems unavailable"}

    def _log_pitch_generation(self, pitch_result: Dict[str, Any]):
        """
        Log pitch generation event.
        """
        log_entry = {
            "event_type": "persuasion_pitch_generated",
            "agent_id": pitch_result["agent_id"],
            "target_capsule_id": pitch_result["target_capsule_id"],
            "context": pitch_result["context"],
            "cost": pitch_result["cost"],
            "payment_method": pitch_result["payment_method"],
            "timestamp": pitch_result["timestamp"],
            "correlation_id": pitch_result["correlation_id"],
            "capsule_snapshot": {
                "goal": self.goal,
                "values": self.values,
                "tags": self.tags
            }
        }

        # Log to agent memory if available
        if hasattr(self, 'memory') and self.memory:
            self.memory.log_event(log_entry)

    def appraise_item(self, item_data: Dict[str, Any], archetype: str, llm=None) -> Dict[str, Any]:
        """
        Appraise an item based on its data and the agent's expertise.

        Args:
            item_data: The data of the item to be appraised
            archetype: The archetype category for the item
            llm: Optional LLM for live appraisal

        Returns:
            Dict containing appraisal value, metadata, and cost information
        """
        correlation_id = str(uuid.uuid4())
        timestamp = time.time()

        # Fetch archetype configuration
        archetype_config = get_archetype_config(archetype)

        # Calculate base costs and value ranges
        base_costs = calculate_base_costs(item_data, archetype_config)

        # Feature flag for advanced appraisal
        ENABLE_ADVANCED_APPRAISAL = True

        if not ENABLE_ADVANCED_APPRAISAL:
            return {
                "value": base_costs["min_value"],
                "cost": base_costs["cost"],
                "enabled": False,
                "correlation_id": correlation_id,
                "timestamp": timestamp
            }

        # Perform appraisal using LLM if available, otherwise fallback to base costs
        if llm:
            appraisal_value = self._perform_llm_appraisal(
                item_data, llm, correlation_id)
        else:
            # Fallback to minimum value
            appraisal_value = base_costs["min_value"]

        # Log the appraisal event
        self._log_appraisal_event(item_data, appraisal_value, correlation_id)

        return {
            "value": appraisal_value,
            "cost": base_costs["cost"],
            "currency": base_costs["currency"],
            "success": True,
            "correlation_id": correlation_id,
            "timestamp": timestamp
        }

    def _perform_llm_appraisal(self, item_data: Dict[str, Any], llm, correlation_id: str) -> float:
        """
        Perform item appraisal using LLM.
        """
        prompt = f"""
        You are an AI appraiser evaluating an item for its fair market value.

        Item Data:
        {item_data}

        Consider the item's condition, rarity, demand, and any other relevant factors.
        Provide a precise appraisal value in USD.

        Respond with just the value, no explanations.
        """

        try:
            response = llm.invoke(prompt)
            value = float(response.strip())

            # Log LLM interaction for appraisal
            if hasattr(self, 'memory') and self.memory:
                llm_log = {
                    "type": "llm_interaction",
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "correlation_id": correlation_id,
                    "prompt": "Item appraisal",
                    "completion": response,
                    "live_mode": True
                }
                self.memory.store_llm_interaction(llm_log)

            return value
        except Exception as e:
            logging.error(f"LLM appraisal error: {e}")
            return 0.0  # Fallback to zero value on error

    def _log_appraisal_event(self, item_data: Dict[str, Any], appraisal_value: float, correlation_id: str):
        """
        Log item appraisal event.
        """
        log_entry = {
            "event_type": "item_appraised",
            "agent_id": self.get_agent_id(),
            "item_data": item_data,
            "appraisal_value": appraisal_value,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "correlation_id": correlation_id
        }

        # Log to agent memory if available
        if hasattr(self, 'memory') and self.memory:
            self.memory.log_event(log_entry)

    # ...existing code...


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

    def appraise_item(self, item_metadata: Dict[str, Any], context: str = "trade",
                      target_capsule: Optional[Capsule] = None, enable_pitch: bool = False) -> Dict[str, Any]:
        """
        Comprehensive item appraisal with archetype-driven behavior, cost estimation, and LLM reasoning.

        Args:
            item_metadata: Metadata about the item being appraised
            context: Context for the appraisal ("trade", "coalition", "investment")
            target_capsule: Target capsule if this is for a specific trade
            enable_pitch: Whether to include pitch generation costs

        Returns:
            Dict containing full appraisal breakdown and decision
        """
        correlation_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()

        logging.info(f"Starting item appraisal for {item_metadata.get('name', 'unknown')} "
                     f"with correlation_id {correlation_id}")

        try:
            # Step 1: Calculate base subjective value
            base_value = self._calculate_base_subjective_value(
                item_metadata, context, correlation_id)

            # Step 2: Apply drift adjustments and goal alignment
            drift_adjustment = self._calculate_drift_adjustment(
                item_metadata, correlation_id)
            alignment_score = self._calculate_goal_alignment(
                item_metadata, target_capsule, correlation_id)

            # Step 3: Get UGTT strategy bonus
            ugtt_bonus = self._calculate_ugtt_bonus(
                item_metadata, context, correlation_id)

            # Step 4: Calculate all costs
            cost_breakdown = self._calculate_total_costs(
                enable_pitch, context, correlation_id)

            # Step 5: Apply archetype-specific logic
            archetype_config = get_archetype_config(self.archetype)
            final_value = self._apply_archetype_logic(
                base_value, drift_adjustment, alignment_score, ugtt_bonus,
                cost_breakdown, archetype_config, correlation_id
            )

            # Step 6: Generate LLM reasoning if enabled
            reasoning = self._generate_value_reasoning(
                item_metadata, base_value, final_value, context, correlation_id
            )

            # Step 7: Create comprehensive appraisal result
            appraisal_result = {
                "correlation_id": correlation_id,
                "timestamp": timestamp,
                "item_metadata": item_metadata,
                "context": context,
                "archetype": self.archetype,
                "base_value": base_value,
                "adjustments": {
                    "drift": drift_adjustment,
                    "alignment": alignment_score,
                    "ugtt_bonus": ugtt_bonus,
                },
                "costs": cost_breakdown,
                "archetype_multipliers": archetype_config,
                "final_net_value": final_value,
                "reasoning": reasoning,
                "decision": "accept" if final_value > 0 else "reject",
                "agent_id": self.get_agent_id(),
                "capsule_id": self.capsule_id,
            }

            # Step 8: Store in history
            self.appraisal_history.append(appraisal_result)

            # Step 9: Log comprehensive breakdown
            self._log_appraisal_breakdown(appraisal_result)

            return appraisal_result

        except Exception as e:
            logging.error(
                f"Error in item appraisal with correlation_id {correlation_id}: {e}")
            return {
                "correlation_id": correlation_id,
                "timestamp": timestamp,
                "error": str(e),
                "decision": "error",
                "final_net_value": 0,
            }

    def _calculate_base_subjective_value(self, item_metadata: Dict[str, Any],
                                         context: str, correlation_id: str) -> float:
        """Calculate base subjective value using LLM or hybrid approach."""
        try:
            if self.config["llm"]["enable_llm_reasoning"]:
                return self._llm_value_calculation(item_metadata, context, correlation_id)
            else:
                return self._hybrid_value_calculation(item_metadata, context, correlation_id)
        except Exception as e:
            logging.warning(
                f"Error in base value calculation {correlation_id}: {e}")
            return self._fallback_value_calculation(item_metadata)

    def _llm_value_calculation(self, item_metadata: Dict[str, Any],
                               context: str, correlation_id: str) -> float:
        """Use LLM for sophisticated value reasoning."""
        llm = get_shared_llm()
        if not llm:
            return self._hybrid_value_calculation(item_metadata, context, correlation_id)

        prompt = f"""Evaluate the subjective value of this item for an AI agent:

Agent Profile:
- Goal: {self.goal}
- Values: {self.values}
- Tags: {self.tags}
- Archetype: {self.archetype}

Item Details:
- Name: {item_metadata.get('name', 'Unknown')}
- Description: {item_metadata.get('description', 'No description')}
- Category: {item_metadata.get('category', 'Unknown')}
- Market Value: ${item_metadata.get('market_value', 0)}
- Condition: {item_metadata.get('condition', 'Unknown')}

Context: {context}

Provide a numerical value score (0-100) representing how valuable this item is to this specific agent.
Consider alignment with goals, values, and archetype. Respond with just the number."""

        try:
            response = llm.generate_text(prompt, max_tokens=50)
            # Extract numerical value from response
            import re
            numbers = re.findall(r'\d+\.?\d*', response)
            if numbers:
                return float(numbers[0])
            else:
                return self._hybrid_value_calculation(item_metadata, context, correlation_id)
        except Exception as e:
            logging.warning(
                f"LLM value calculation failed {correlation_id}: {e}")
            return self._hybrid_value_calculation(item_metadata, context, correlation_id)

    def _hybrid_value_calculation(self, item_metadata: Dict[str, Any],
                                  context: str, correlation_id: str) -> float:
        """Hybrid calculation using Reality Query and capsule biases."""
        try:
            # Get market context from Reality Query
            market_context = self.reality_query.query_reality(
                f"Current market trends for {item_metadata.get('category', 'general')} items",
                context={"item": item_metadata}
            )

            # Base value from market
            market_value = float(item_metadata.get('market_value', 0))

            # Apply capsule biases
            category_interest = self._calculate_category_interest(
                item_metadata.get('category', ''))
            condition_multiplier = self._get_condition_multiplier(
                item_metadata.get('condition', 'good'))

            base_value = market_value * category_interest * condition_multiplier

            # Apply market context modifier
            market_modifier = self._parse_market_context(
                market_context.get('result', ''))

            return base_value * market_modifier

        except Exception as e:
            logging.warning(
                f"Hybrid value calculation failed {correlation_id}: {e}")
            return self._fallback_value_calculation(item_metadata)

    def _fallback_value_calculation(self, item_metadata: Dict[str, Any]) -> float:
        """Simple fallback calculation."""
        market_value = float(item_metadata.get('market_value', 0))
        return market_value * 0.8  # Conservative fallback

    def _calculate_drift_adjustment(self, item_metadata: Dict[str, Any], correlation_id: str) -> float:
        """Calculate drift-based value adjustment."""
        # Simulate drift based on recent history and market changes
        drift_factor = 0.0

        # Check recent appraisal history for trends
        if len(self.appraisal_history) > 3:
            recent_values = [a.get('final_net_value', 0)
                             for a in self.appraisal_history[-3:]]
            if len(recent_values) >= 2:
                trend = (recent_values[-1] -
                         recent_values[0]) / len(recent_values)
                drift_factor = trend * 0.1  # Scale drift influence

        return drift_factor

    def _calculate_goal_alignment(self, item_metadata: Dict[str, Any],
                                  target_capsule: Optional[Capsule], correlation_id: str) -> float:
        """Calculate how well the item aligns with agent goals."""
        alignment_score = 0.0

        # Check alignment with own goals
        item_keywords = set(item_metadata.get(
            'description', '').lower().split())
        goal_keywords = set(self.goal.lower().split())
        value_keywords = set(' '.join(str(v)
                             for v in self.values.values()).lower().split())

        goal_overlap = len(item_keywords.intersection(
            goal_keywords)) / max(len(goal_keywords), 1)
        value_overlap = len(item_keywords.intersection(
            value_keywords)) / max(len(value_keywords), 1)

        alignment_score = (goal_overlap + value_overlap) * 0.5

        # If trading with another agent, consider their alignment too
        if target_capsule:
            target_goal_keywords = set(target_capsule.goal.lower().split())
            target_overlap = len(item_keywords.intersection(
                target_goal_keywords)) / max(len(target_goal_keywords), 1)
            alignment_score = (alignment_score + target_overlap) * 0.5

        return alignment_score * 20  # Scale to meaningful value

    def _calculate_ugtt_bonus(self, item_metadata: Dict[str, Any],
                              context: str, correlation_id: str) -> float:
        """Calculate UGTT strategic bonus."""
        try:
            # Create a simple game scenario
            payoff_matrix = [[1, 0], [0, 1]]  # Simple coordination game
            strategy_result = self.ugtt_module.execute_strategy(
                payoff_matrix,
                context=f"Item appraisal for {item_metadata.get('name', 'item')}",
                agent_id=self.get_agent_id() or "unknown"
            )

            # Extract bonus from strategy
            confidence = strategy_result.get(
                'strategy_result', {}).get('confidence', 0.5)
            strategy_type = strategy_result.get(
                'strategy_result', {}).get('strategy', 'neutral')

            base_bonus = confidence * 10  # Base bonus from confidence

            # Strategy-specific bonuses
            strategy_bonuses = {
                'cooperative': 5,
                'competitive': 3,
                'neutral': 0,
                'aggressive': -2,
            }

            strategy_bonus = strategy_bonuses.get(strategy_type, 0)

            return base_bonus + strategy_bonus

        except Exception as e:
            logging.warning(
                f"UGTT bonus calculation failed {correlation_id}: {e}")
            return 0.0

    def _calculate_total_costs(self, enable_pitch: bool, context: str, correlation_id: str) -> Dict[str, float]:
        """Calculate all transaction costs."""
        base_costs = calculate_base_costs()

        costs = {
            "gas_cost_usd": base_costs["gas_cost_usd"],
            "x402_fee_usd": base_costs["x402_fee_usd"],
            "coalition_share": 0.0,
            "pitch_cost_xp": 0,
            "pitch_cost_usd": 0.0,
            "total_cost_usd": base_costs["total_base_cost_usd"],
        }

        # Add coalition profit share if applicable
        if context == "coalition":
            coalition_share = self.config["x402_payments"]["coalition_profit_share"]
            costs["coalition_share"] = coalition_share
            costs["total_cost_usd"] += coalition_share

        # Add pitch costs if enabled
        if enable_pitch:
            agent_xp = self.get_xp()
            pitch_threshold = self.config["x402_payments"]["premium_pitch_threshold"]

            if agent_xp >= pitch_threshold:
                # Use XP for pitch
                costs["pitch_cost_xp"] = base_costs["pitch_cost_xp"]
            else:
                # Use USD for pitch
                costs["pitch_cost_usd"] = base_costs["pitch_cost_usd"]
                costs["total_cost_usd"] += costs["pitch_cost_usd"]

        return costs

    def _apply_archetype_logic(self, base_value: float, drift_adjustment: float,
                               alignment_score: float, ugtt_bonus: float,
                               cost_breakdown: Dict[str, float], archetype_config: Dict[str, Any],
                               correlation_id: str) -> float:
        """Apply archetype-specific calculation logic."""

        # Calculate adjusted base value
        adjusted_base = base_value + \
            (drift_adjustment * archetype_config["drift_weight"])
        adjusted_base += alignment_score * \
            self.config["values"]["alignment_weight"]

        # Apply UGTT bonus with archetype multiplier
        ugtt_contribution = ugtt_bonus * \
            archetype_config["ugtt_bonus_multiplier"]

        # Calculate total costs with sensitivity
        total_costs = cost_breakdown["total_cost_usd"] * \
            archetype_config["cost_sensitivity"]

        # Apply archetype-specific formula
        if self.archetype == "visionary":
            # Visionaries: (Base + Adj) * UGTT - Costs
            final_value = (adjusted_base + ugtt_contribution) * \
                archetype_config["risk_multiplier"] - total_costs
        elif self.archetype == "investor":
            # Investors: (Base + Adj - Costs) * UGTT
            final_value = (adjusted_base - total_costs) * \
                (1 + ugtt_contribution * 0.1)
        else:
            # Default: Balanced approach
            final_value = adjusted_base + ugtt_contribution - total_costs

        return final_value

    def _generate_value_reasoning(self, item_metadata: Dict[str, Any], base_value: float,
                                  final_value: float, context: str, correlation_id: str) -> str:
        """Generate LLM-powered reasoning for the valuation."""
        if not self.config["llm"]["enable_llm_reasoning"]:
            return f"Base value {base_value:.2f}, final value {final_value:.2f} for {context}"

        llm = get_shared_llm()
        if not llm:
            return f"Calculated value {final_value:.2f} based on {context} context"

        prompt = f"""Explain why this item valuation makes sense for this AI agent:

Agent: {self.goal} (Archetype: {self.archetype})
Item: {item_metadata.get('name', 'Unknown')}
Base Value: ${base_value:.2f}
Final Value: ${final_value:.2f}
Context: {context}

Provide a brief reasoning in 2-3 sentences."""

        try:
            reasoning = llm.generate_text(
                prompt, max_tokens=self.config["llm"]["max_reasoning_tokens"])
            return reasoning.strip()
        except Exception as e:
            logging.warning(
                f"LLM reasoning generation failed {correlation_id}: {e}")
            return f"Value {final_value:.2f} calculated based on agent goals and market context"

    def _log_appraisal_breakdown(self, appraisal_result: Dict[str, Any]):
        """Log comprehensive appraisal breakdown."""
        correlation_id = appraisal_result["correlation_id"]

        logging.info(f"=== ITEM APPRAISAL BREAKDOWN [{correlation_id}] ===")
        logging.info(
            f"Item: {appraisal_result['item_metadata'].get('name', 'Unknown')}")
        logging.info(
            f"Agent: {appraisal_result['agent_id']} ({appraisal_result['archetype']})")
        logging.info(f"Context: {appraisal_result['context']}")
        logging.info(f"Base Value: ${appraisal_result['base_value']:.2f}")
        logging.info(f"Adjustments: Drift={appraisal_result['adjustments']['drift']:.2f}, "
                     f"Alignment={appraisal_result['adjustments']['alignment']:.2f}, "
                     f"UGTT={appraisal_result['adjustments']['ugtt_bonus']:.2f}")
        logging.info(
            f"Costs: Total=${appraisal_result['costs']['total_cost_usd']:.2f}")
        logging.info(
            f"Final Net Value: ${appraisal_result['final_net_value']:.2f}")
        logging.info(f"Decision: {appraisal_result['decision'].upper()}")
        logging.info(f"Reasoning: {appraisal_result['reasoning']}")
        logging.info(f"=== END APPRAISAL [{correlation_id}] ===")

    def _calculate_category_interest(self, category: str) -> float:
        """Calculate interest level in item category based on agent profile."""
        if not category:
            return 1.0

        # Simple keyword matching with agent profile
        category_lower = category.lower()
        goal_lower = self.goal.lower()

        # Check for category-goal alignment
        if any(word in goal_lower for word in category_lower.split()):
            return 1.5
        elif any(tag.lower() in category_lower for tag in self.tags):
            return 1.3
        else:
            return 1.0

    def _get_condition_multiplier(self, condition: str) -> float:
        """Get value multiplier based on item condition."""
        condition_multipliers = {
            'excellent': 1.2,
            'very good': 1.1,
            'good': 1.0,
            'fair': 0.8,
            'poor': 0.6,
        }
        return condition_multipliers.get(condition.lower(), 1.0)

    def _parse_market_context(self, market_context: str) -> float:
        """Parse market context to extract value modifier."""
        if not market_context:
            return 1.0

        context_lower = market_context.lower()

        # Simple sentiment analysis for market modifier
        positive_words = ['growth', 'rising', 'strong',
                          'bullish', 'increasing', 'demand']
        negative_words = ['decline', 'falling', 'weak',
                          'bearish', 'decreasing', 'oversupply']

        positive_count = sum(
            1 for word in positive_words if word in context_lower)
        negative_count = sum(
            1 for word in negative_words if word in context_lower)

        net_sentiment = positive_count - negative_count

        # Convert to multiplier (0.8 to 1.2 range)
        return 1.0 + (net_sentiment * 0.1)

    def mint_nft_on_trade(self, item_metadata: Dict[str, Any], trade_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mint new NFT after successful trade and update ownership chain.

        Args:
            item_metadata: Metadata of the traded item
            trade_context: Context of the trade (partner, terms, etc.)

        Returns:
            Dict containing NFT mint details and updated ownership
        """
        correlation_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()

        # Determine NFT standard based on item type
        is_digital = item_metadata.get('type', 'physical') == 'digital'
        nft_standard = self.config["nft"]["digital_nft_standard"] if is_digital else self.config["nft"]["redeemable_contract"]

        # Create NFT metadata
        nft_metadata = {
            "nft_id": correlation_id,
            "standard": nft_standard,
            "item_metadata": item_metadata,
            "trade_context": trade_context,
            "mint_timestamp": timestamp,
            "minted_by": self.get_agent_id(),
            "owner": self.get_agent_id(),
            "provenance_chain": [],
            "is_current_owner": True,
        }

        # Archive previous NFTs
        for nft in self.current_owned_nfts:
            if nft.get("item_metadata", {}).get("name") == item_metadata.get("name"):
                nft["is_current_owner"] = False
                nft["archived_timestamp"] = timestamp
                self.nft_ownership_chain.append(nft)

        # Add to current owned NFTs
        self.current_owned_nfts = [nft for nft in self.current_owned_nfts
                                   if nft.get("item_metadata", {}).get("name") != item_metadata.get("name")]
        self.current_owned_nfts.append(nft_metadata)

        # Log NFT creation
        logging.info(f"Minted NFT {nft_metadata['nft_id']} for item {item_metadata.get('name', 'Unknown')} "
                     f"using {nft_standard} standard")

        return nft_metadata

    def get_appraisal_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent appraisal history."""
        return self.appraisal_history[-limit:] if self.appraisal_history else []

    def get_owned_nfts(self) -> List[Dict[str, Any]]:
        """Get currently owned NFTs."""
        return self.current_owned_nfts

    def get_nft_provenance_chain(self, item_name: str) -> List[Dict[str, Any]]:
        """Get provenance chain for a specific item."""
        chain = []

        # Add current ownership
        for nft in self.current_owned_nfts:
            if nft.get("item_metadata", {}).get("name") == item_name:
                chain.append(nft)

        # Add historical ownership
        for nft in self.nft_ownership_chain:
            if nft.get("item_metadata", {}).get("name") == item_name:
                chain.append(nft)

        # Sort by timestamp
        chain.sort(key=lambda x: x.get("mint_timestamp", ""), reverse=True)

        return chain[:self.config["nft"]["provenance_chain_length"]]
