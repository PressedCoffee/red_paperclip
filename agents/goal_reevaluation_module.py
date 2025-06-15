import threading
import time
from typing import Optional, Dict, Any, List
from registry.capsule_registry import CapsuleRegistry, Capsule
from memory.agent_memory import AgentMemory
from agents.agent import Agent


class GoalReevaluationModule:
    """
    G.R.E.M. Goal Reevaluation Module for periodic re-assessment of agent goals, tags, and motivation scores.
    Logs internal reasoning and updates the Genesis Capsule accordingly.
    """

    def __init__(self, capsule_registry: CapsuleRegistry, agent_memory: AgentMemory, reevaluation_interval: int = 60):
        """
        Initialize the Goal Reevaluation Module.

        :param capsule_registry: CapsuleRegistry instance for capsule updates.
        :param agent_memory: AgentMemory instance for logging reasoning.
        :param reevaluation_interval: Interval in seconds for periodic reevaluation.
        """
        self.capsule_registry = capsule_registry
        self.agent_memory = agent_memory
        self.reevaluation_interval = reevaluation_interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start_periodic_reevaluation(self):
        """
        Start the periodic reevaluation in a background thread.
        """
        if self._thread and self._thread.is_alive():
            return  # Already running
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._periodic_reevaluation_loop, daemon=True)
        self._thread.start()

    def stop_periodic_reevaluation(self):
        """
        Stop the periodic reevaluation.
        """
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def _periodic_reevaluation_loop(self):
        while not self._stop_event.is_set():
            self.reevaluate_all_agents()
            time.sleep(self.reevaluation_interval)

    def reevaluate_all_agents(self):
        """
        Reevaluate goals, tags, and motivation scores for all capsules in the registry.
        """
        capsules = self.capsule_registry.list_capsules()
        for capsule in capsules:
            self.reevaluate_capsule(capsule)

    def reevaluate_capsule(self, capsule: Capsule):
        """
        Reevaluate a single capsule's goals, tags, and motivation scores.

        :param capsule: Capsule instance to reevaluate.
        """
        # Placeholder for reevaluation logic:
        # For demonstration, we simulate updating motivation score and tags.
        old_goal = capsule.goal
        old_tags = capsule.tags.copy()

        # Simulate reevaluation: append a tag "reevaluated" if not present
        if "reevaluated" not in capsule.tags:
            capsule.tags.append("reevaluated")

        # Simulate motivation score update in values dict
        motivation_score = capsule.values.get("motivation_score", 0)
        # Increment motivation score as example
        new_motivation_score = motivation_score + 1
        capsule.values["motivation_score"] = new_motivation_score

        # Log internal reasoning to AgentMemory
        reasoning = (
            f"Reevaluated capsule {capsule.capsule_id}: "
            f"Goal unchanged: '{old_goal}', "
            f"Tags updated from {old_tags} to {capsule.tags}, "
            f"Motivation score updated from {motivation_score} to {new_motivation_score}."
        )
        agent_id = capsule.capsule_id  # Using capsule_id as agent_id for memory logging
        self.agent_memory.add_trade_record(
            agent_id=agent_id,
            trade_item="Goal Reevaluation",
            outcome="updated",
            capsule_data=capsule.to_dict(),
        )

        # Update the capsule in the registry
        self.capsule_registry._capsules[capsule.capsule_id] = capsule
