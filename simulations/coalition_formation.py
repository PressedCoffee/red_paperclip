import random
import logging
from typing import List, Dict, Optional, Set, Tuple
from negotiation.negotiation_module import NegotiationModule

logger = logging.getLogger(__name__)


class CoalitionFormation:
    def __init__(self, agents: List["AutonomousAgent"], agent_memories: Dict[str, "AgentMemory"] = None):
        """
        Initialize with a list of agents and optional agent memories for negotiation.
        """
        self.agents = agents
        # coalition_id -> set of agent_ids
        self.coalitions: Dict[int, Set[str]] = {}
        self.next_coalition_id = 1
        # agent_id -> coalition_id
        self.agent_to_coalition: Dict[str, int] = {}

        # Initialize negotiation module if agent memories provided
        if agent_memories is None:
            agent_memories = {}
        self.negotiation_module = NegotiationModule(agent_memories)

        # Store payoff shares per coalition for lifecycle management
        self.coalition_payoff_shares: Dict[int, Dict[str, float]] = {}

    def propose_coalition(self, proposing_agent_id: str, candidate_agent_ids: List[str]) -> Optional[Dict]:
        """
        Propose a coalition with the proposing agent and candidate agents.
        Coalition must have 3 or more agents.
        Returns coalition proposal dict if valid, else None.
        """
        members = set(candidate_agent_ids)
        members.add(proposing_agent_id)
        if len(members) < 3:
            logger.debug(
                f"Coalition proposal rejected: less than 3 members ({members})")
            return None

        # Check if any member is already in a coalition
        for agent_id in members:
            if agent_id in self.agent_to_coalition:
                logger.debug(
                    f"Agent {agent_id} already in coalition {self.agent_to_coalition[agent_id]}")
                return None

        # Simulate pooled payoff as sum of random payoffs for each member
        pooled_payoff = sum(random.uniform(1, 10) for _ in members)

        # Use negotiation module to propose payoff splits
        payoff_shares = self.negotiation_module.propose_split(
            pooled_payoff, list(members))

        proposal = {
            "coalition_id": self.next_coalition_id,
            "members": list(members),
            "pooled_payoff": pooled_payoff,
            "payoff_shares": payoff_shares,
            "accepted": False,
        }
        logger.debug(f"Coalition proposed: {proposal}")
        return proposal

    def accept_coalition(self, proposal: Dict) -> bool:
        """
        Accept the coalition proposal.
        Updates coalition membership and agent mappings.
        Returns True if accepted successfully.
        """
        coalition_id = proposal["coalition_id"]
        members = proposal["members"]

        # Double check no member is already in a coalition
        for agent_id in members:
            if agent_id in self.agent_to_coalition:
                logger.debug(
                    f"Cannot accept coalition {coalition_id}: agent {agent_id} already in coalition {self.agent_to_coalition[agent_id]}")
                return False

        self.coalitions[coalition_id] = set(members)
        for agent_id in members:
            self.agent_to_coalition[agent_id] = coalition_id

        # Store payoff shares for lifecycle use
        self.coalition_payoff_shares[coalition_id] = proposal.get(
            "payoff_shares", {})

        proposal["accepted"] = True
        logger.debug(
            f"Coalition {coalition_id} accepted with members {members}")
        return True

    def update_xp_and_badges(self, proposal: Dict, badge_xp_systems: Dict[str, "BadgeXPSystem"]):
        """
        Update XP and badges for coalition members based on payoff shares.
        """
        if not proposal.get("accepted", False):
            return

        payoff_shares = proposal.get("payoff_shares", {})
        members = proposal["members"]

        for agent_id in members:
            badge_xp_system = badge_xp_systems.get(agent_id)
            if badge_xp_system:
                # Grant XP equal to payoff share * 10 (arbitrary scaling)
                xp_amount = int(payoff_shares.get(agent_id, 0) * 10)
                # Use standalone grant_xp function instead of method call
                from agents.badge_xp_system import grant_xp
                grant_xp(
                    agent_id, xp_amount, f"Coalition payoff share in coalition {proposal['coalition_id']}")
                logger.debug(
                    f"Granted {xp_amount} XP to {agent_id} for coalition {proposal['coalition_id']}")

    def dissolve_coalition(self, coalition_id: int):
        """
        Dissolve a coalition, removing all members from it.
        """
        if coalition_id not in self.coalitions:
            return
        members = self.coalitions.pop(coalition_id)
        for agent_id in members:
            self.agent_to_coalition.pop(agent_id, None)
        self.coalition_payoff_shares.pop(coalition_id, None)
        logger.debug(f"Coalition {coalition_id} dissolved")

    def agent_leave_coalition(self, agent_id: str, payoff_threshold: float = 1.0) -> bool:
        """
        Allow an agent to leave its coalition if its payoff share drops below a threshold.
        Returns True if agent left coalition, False otherwise.
        """
        coalition_id = self.agent_to_coalition.get(agent_id)
        if coalition_id is None:
            return False

        payoff_shares = self.coalition_payoff_shares.get(coalition_id, {})
        agent_payoff = payoff_shares.get(agent_id, 0)
        if agent_payoff < payoff_threshold:
            coalition_members = self.coalitions.get(coalition_id, set())
            coalition_members.remove(agent_id)
            self.agent_to_coalition.pop(agent_id, None)
            logger.debug(
                f"Agent {agent_id} left coalition {coalition_id} due to low payoff {agent_payoff}")
            logger.info(
                f"Coalition {coalition_id} split: agent {agent_id} left")
            # If coalition too small, dissolve it
            if len(coalition_members) < 3:
                self.dissolve_coalition(coalition_id)
            else:
                self.coalitions[coalition_id] = coalition_members
            return True
        return False

    def merge_coalitions(self, coalition_id1: int, coalition_id2: int) -> Optional[int]:
        """
        Merge two coalitions if mutual benefit is detected.
        Returns new coalition_id if merged, else None.
        """
        members1 = self.coalitions.get(coalition_id1)
        members2 = self.coalitions.get(coalition_id2)
        if not members1 or not members2:
            return None

        combined_members = members1.union(members2)
        if len(combined_members) < 3:
            return None

        # Dissolve old coalitions
        self.dissolve_coalition(coalition_id1)
        self.dissolve_coalition(coalition_id2)

        # Create new coalition
        new_coalition_id = self.next_coalition_id
        self.next_coalition_id += 1
        self.coalitions[new_coalition_id] = combined_members
        for agent_id in combined_members:
            self.agent_to_coalition[agent_id] = new_coalition_id

        logger.info(
            f"Coalitions {coalition_id1} and {coalition_id2} merged into {new_coalition_id}")
        return new_coalition_id

    def get_coalition_id(self, agent_id: str) -> Optional[int]:
        """
        Get the coalition ID for a given agent, or None if not in a coalition.
        """
        return self.agent_to_coalition.get(agent_id)

    def get_coalition_members(self, coalition_id: int) -> Optional[Set[str]]:
        """
        Get the members of a coalition by ID.
        """
        return self.coalitions.get(coalition_id)
