from typing import Dict, Tuple
from agents.agent import Agent
from memory.agent_memory import AgentMemory
from agents.blockchain_ops import BlockchainOpsSimulator


class TradeEvaluator:
    def __init__(self):
        self.agent_memory = AgentMemory()
        self.blockchain_ops_simulator = BlockchainOpsSimulator()

    def evaluate_trade(self, agent: Agent, offer: Dict) -> Tuple[Dict, bool]:
        """
        Evaluate the trade offer and return a multidimensional evaluation dict
        and an acceptance decision based on internal reasoning.

        Args:
            agent (Agent): The agent evaluating the trade.
            offer (dict): The trade offer dictionary.

        Returns:
            tuple: (evaluation_dict (Dict), accept (bool))
        """
        offer_tags = set(offer.get("item_tags", []))
        agent_values = set(agent.capsule_data.get("values", []))
        agent_tags = set(agent.capsule_data.get("tags", []))
        agent_goal = agent.capsule_data.get("goal", "")

        # Normalize goal to set of keywords (simple split by spaces, lowercase)
        if isinstance(agent_goal, str):
            goal_keywords = set(agent_goal.lower().split())
        elif isinstance(agent_goal, (list, set)):
            goal_keywords = set(map(str.lower, agent_goal))
        else:
            goal_keywords = set()

        # Calculate matches
        value_matches = offer_tags.intersection(agent_values)
        tag_matches = offer_tags.intersection(agent_tags)
        goal_matches = offer_tags.intersection(goal_keywords)

        # Calculate scores for each category
        total_tags = len(offer_tags) if offer_tags else 1
        value_score = len(value_matches) / total_tags
        tag_score = len(tag_matches) / total_tags
        goal_score = len(goal_matches) / total_tags

        # Compose multidimensional evaluation
        evaluation = {
            "alignment_score": max(0.0, min(1.0, 0.5 * goal_score + 0.3 * value_score + 0.2 * tag_score)),
            "emotional_resonance": self._generate_emotional_resonance(agent, offer),
            "symbolic_alignment": self._generate_symbolic_alignment(agent, offer),
            "narrative_potential": self._generate_narrative_potential(agent, offer),
        }

        # Use internal reasoning to decide acceptance (placeholder logic)
        accept = self.should_accept_trade(evaluation)

        # Record trade in memory with all details
        outcome = "accepted" if accept else "rejected"
        agent_id = getattr(agent, "identifier", None)
        if agent_id is None:
            # Fallback to string representation of capsule_data as agent_id
            agent_id = str(agent.capsule_data)

        trade_item = offer.get("item_name", "unknown_item")
        self.agent_memory.add_trade_record(
            agent_id, trade_item, outcome, agent.capsule_data)

        # Trigger blockchain ops simulation and log event
        blockchain_event = self.blockchain_ops_simulator.simulate_trade_consequence(
            agent_id, trade_item, outcome, agent.capsule_data)
        print(
            f"[TradeEvaluator] Blockchain event simulated: {blockchain_event}")

        # Log details
        print(f"[TradeEvaluator] Evaluation: {evaluation}")
        print(f"[TradeEvaluator] Trade {'ACCEPTED' if accept else 'REJECTED'}")

        return evaluation, accept

    def should_accept_trade(self, evaluation: Dict) -> bool:
        """
        Internal reasoning on multidimensional evaluation to decide accept/reject.

        Args:
            evaluation (Dict): The multidimensional evaluation dictionary.

        Returns:
            bool: True to accept, False to reject.
        """
        # Placeholder logic: accept if alignment_score > 0.15
        if evaluation.get("alignment_score", 0) > 0.15:
            return True
        return False

    def _generate_emotional_resonance(self, agent: Agent, offer: Dict) -> float:
        """
        Generate a score for emotional resonance between the agent and the offer.

        Args:
            agent (Agent): The agent evaluating the trade.
            offer (dict): The trade offer dictionary.

        Returns:
            float: A score between 0 and 1 representing emotional resonance.
        """
        # Placeholder implementation
        return 0.5

    def _generate_symbolic_alignment(self, agent: Agent, offer: Dict) -> float:
        """
        Generate a score for symbolic alignment between the agent and the offer.

        Args:
            agent (Agent): The agent evaluating the trade.
            offer (dict): The trade offer dictionary.

        Returns:
            float: A score between 0 and 1 representing symbolic alignment.
        """
        # Placeholder implementation
        return 0.5

    def _generate_narrative_potential(self, agent: Agent, offer: Dict) -> float:
        """
        Generate a score for narrative potential of the trade.

        Args:
            agent (Agent): The agent evaluating the trade.
            offer (dict): The trade offer dictionary.

        Returns:
            float: A score between 0 and 1 representing narrative potential.
        """
        # Placeholder implementation
        return 0.5
