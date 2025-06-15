from typing import List, Dict
from memory.agent_memory import AgentMemory
import logging

logger = logging.getLogger(__name__)


class NegotiationModule:
    def __init__(self, agent_memories: Dict[str, AgentMemory]):
        """
        Initialize with a dictionary mapping agent_id to AgentMemory.
        """
        self.agent_memories = agent_memories

    def propose_split(self, total_payoff: float, members: List[str]) -> Dict[str, float]:
        """
        Propose a payoff split among members weighted by their reputation.

        Args:
            total_payoff: The total payoff to split.
            members: List of agent IDs in the coalition.

        Returns:
            A dict mapping agent_id to their payoff share.
        """
        reputations = {}
        total_reputation = 0.0
        for agent_id in members:
            mem = self.agent_memories.get(agent_id)
            rep = mem.get_reputation() if mem else 1.0
            reputations[agent_id] = rep
            total_reputation += rep

        if total_reputation == 0:
            # Avoid division by zero, split equally
            equal_share = total_payoff / len(members)
            shares = {agent_id: equal_share for agent_id in members}
        else:
            shares = {agent_id: (
                reputations[agent_id] / total_reputation) * total_payoff for agent_id in members}

        # Log and update negotiation histories
        for agent_id, share in shares.items():
            mem = self.agent_memories.get(agent_id)
            if mem:
                outcome = {
                    "coalition_members": members,
                    "total_payoff": total_payoff,
                    "proposed_share": share,
                    "reputation": reputations[agent_id],
                }
                mem.log_negotiation_result(outcome)
                logger.debug(f"Negotiation split for {agent_id}: {outcome}")

        return shares
