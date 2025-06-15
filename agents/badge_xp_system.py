import random
from typing import Dict, List, Optional, Any
from registry.capsule_registry import CapsuleRegistry, Capsule


class BadgeXPSystem:
    """
    Manages badge naming, attribution, XP accumulation, and milestone tracking per agent.
    Integrates with CapsuleRegistry for badge data storage.
    """

    def __init__(self, capsule_registry: CapsuleRegistry):
        self.capsule_registry = capsule_registry
        # Store XP per agent_id
        self.agent_xp: Dict[str, int] = {}
        # Store badges per agent_id
        self.agent_badges: Dict[str, List[Capsule]] = {}

    def _generate_badge_name(self, milestone: str) -> str:
        """
        Stub for LLM-generated badge naming logic.
        For now, generate a simple badge name based on milestone.
        """
        # In real implementation, call LLM to generate creative badge name
        badge_names = [
            f"{milestone} Achiever",
            f"{milestone} Conqueror",
            f"{milestone} Champion",
            f"{milestone} Trailblazer",
            f"{milestone} Mastermind",
        ]
        return random.choice(badge_names)

    def award_badge(self, agent_id: str, milestone: str, xp_amount: int) -> Capsule:
        """
        Award a badge to an agent for reaching a milestone and add XP.

        :param agent_id: Unique identifier of the agent.
        :param milestone: The milestone achieved.
        :param xp_amount: XP to add for this milestone.
        :return: The created Capsule representing the badge.
        """
        badge_name = self._generate_badge_name(milestone)
        badge_goal = f"Badge for milestone: {milestone}"
        badge_values = {
            "agent_id": agent_id,
            "milestone": milestone,
            "xp_awarded": xp_amount,
            "badge_name": badge_name,
        }
        badge_tags = ["badge", milestone.lower().replace(" ", "_")]

        badge_capsule = self.capsule_registry.create_capsule(
            goal=badge_goal,
            values=badge_values,
            tags=badge_tags,
            wallet_address=None,
            public_snippet=f"Agent {agent_id} earned badge '{badge_name}' for {milestone} milestone."
        )

        # Track badge for agent
        if agent_id not in self.agent_badges:
            self.agent_badges[agent_id] = []
        self.agent_badges[agent_id].append(badge_capsule)

        # Add XP
        self.agent_xp[agent_id] = self.agent_xp.get(agent_id, 0) + xp_amount

        return badge_capsule

    def get_agent_xp(self, agent_id: str) -> int:
        """
        Get the total XP accumulated by an agent.

        :param agent_id: Unique identifier of the agent.
        :return: Total XP.
        """
        return self.agent_xp.get(agent_id, 0)

    def get_agent_badges(self, agent_id: str) -> List[Capsule]:
        """
        Get the list of badges earned by an agent.

        :param agent_id: Unique identifier of the agent.
        :return: List of badge Capsules.
        """
        return self.agent_badges.get(agent_id, [])

    def has_badge(self, agent_id: str, milestone: str) -> bool:
        """
        Check if an agent already has a badge for a given milestone.

        :param agent_id: Unique identifier of the agent.
        :param milestone: Milestone name.
        :return: True if badge exists, False otherwise.
        """
        badges = self.get_agent_badges(agent_id)
        for badge in badges:
            if badge.values.get("milestone") == milestone:
                return True
        return False


def grant_xp(agent_id: str, amount: int, reason: str = ""):
    """
    Grant XP to an agent with an optional reason.
    This is a stub function that could be expanded to interact with BadgeXPSystem.
    """
    print(
        f"[grant_xp] Granting {amount} XP to agent {agent_id}. Reason: {reason}")


def trigger_badge_unlock(agent_id: str, badge_name: str):
    """
    Trigger badge unlock for an agent.
    This is a stub function that could be expanded to interact with BadgeXPSystem.
    """
    print(
        f"[trigger_badge_unlock] Unlocking badge '{badge_name}' for agent {agent_id}.")
