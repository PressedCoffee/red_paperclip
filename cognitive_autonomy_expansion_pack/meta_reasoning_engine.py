import datetime
from typing import List, Dict, Any, Optional

# Assuming AgentMemory and GoalReevaluationModule are available in the project
from memory.agent_memory import AgentMemory
from agents.goal_reevaluation_module import GoalReevaluationModule
from ui.snapshot_panel import SnapshotPanel
from cognitive_autonomy_expansion_pack.meta_capsule_drift_engine import EXPERIMENTAL_FEATURES


class GenesisMetaReasoner:
    """
    MetaReasoningEngine to analyze past reasoning patterns, generate hypotheses,
    propose strategy refinements, and integrate with AgentMemory and Goal Reevaluation Module.
    Includes snapshot panel reasoning logs and feedback loop.
    """

    def __init__(self, agent_memory: AgentMemory, goal_reevaluator: GoalReevaluationModule,
                 snapshot_panel: Optional[SnapshotPanel] = None, capsule=None):
        self.agent_memory = agent_memory
        self.goal_reevaluator = goal_reevaluator
        self.snapshot_panel = snapshot_panel
        self.capsule = capsule
        self.last_reasoning_cycle = None
        self.reasoning_log: List[Dict[str, Any]] = []

    def analyze_reasoning_patterns(self) -> List[str]:
        """
        Analyze past reasoning logs from AgentMemory and identify patterns or anomalies.
        Returns a list of hypotheses or insights.
        """
        reasoning_history = self.agent_memory.get_reasoning_history()
        hypotheses = []

        # Simple pattern recognition example: count repeated failed strategies
        failed_strategies = {}
        for entry in reasoning_history:
            if entry.get("outcome") == "failure":
                strategy = entry.get("strategy")
                failed_strategies[strategy] = failed_strategies.get(
                    strategy, 0) + 1

        for strategy, count in failed_strategies.items():
            if count > 2:
                hypotheses.append(
                    f"Strategy '{strategy}' has failed {count} times; consider refinement.")

        self._log_reasoning_cycle("analyze_reasoning_patterns", hypotheses)
        return hypotheses

    def generate_hypotheses(self) -> List[str]:
        """
        Generate new hypotheses based on reasoning patterns and external context.
        """
        hypotheses = self.analyze_reasoning_patterns()
        # Additional hypothesis generation logic can be added here
        self._log_reasoning_cycle("generate_hypotheses", hypotheses)
        return hypotheses

    def propose_strategy_refinements(self) -> List[str]:
        """
        Propose refinements to current strategies based on hypotheses and feedback.
        """
        hypotheses = self.generate_hypotheses()
        refinements = []
        for hypothesis in hypotheses:
            refinements.append(f"Refinement proposal based on: {hypothesis}")

        self._log_reasoning_cycle("propose_strategy_refinements", refinements)
        return refinements

    def feedback_loop(self):
        """
        Integrate with Goal Reevaluation Module to update goals based on reasoning outcomes.
        """
        refinements = self.propose_strategy_refinements()
        for refinement in refinements:
            self.goal_reevaluator.reevaluate_goal(refinement)

        self._log_reasoning_cycle("feedback_loop", refinements)

    def _log_reasoning_cycle(self, phase: str, data: Any):
        """
        Internal method to log reasoning cycle data and update snapshot panel.
        """
        timestamp = datetime.datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "phase": phase,
            "data": data
        }
        self.reasoning_log.append(log_entry)
        # Update snapshot panel if available
        self.last_reasoning_cycle = log_entry
        if self.snapshot_panel:
            self.snapshot_panel.update_reasoning_log(log_entry)

    def get_snapshot_metadata(self) -> Dict[str, Any]:
        """
        Return structured metadata for agent snapshot observability.
        """
        return {
            "strategic_posture": "meta_reasoning_active",
            "last_reasoning_cycle": self.last_reasoning_cycle,
            "reasoning_log_length": len(self.reasoning_log),
        }

    def propose_exit_protocol(self, reasoning_text):
        """
        Propose an exit protocol based on reasoning text.
        Only active when chaos_pack experimental feature is enabled.
        """
        if not EXPERIMENTAL_FEATURES.get("chaos_pack"):
            self._log_reasoning_cycle(
                "propose_exit_protocol", "Feature 'chaos_pack' disabled; skipping exit protocol.")
            return

        self._log_reasoning_cycle("propose_exit_protocol", reasoning_text)
        self.reasoning_log.append(reasoning_text)

        # Store reasoning pattern in agent memory
        self.agent_memory.add_reasoning_pattern(pattern_name=reasoning_text)

        # Also store in capsule memory if available
        if self.capsule and hasattr(self.capsule, "memory"):
            self.capsule.memory.store_exit_proposal(reasoning_text)
