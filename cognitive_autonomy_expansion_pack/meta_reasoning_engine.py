import datetime
import time
import uuid
from typing import List, Dict, Any, Optional

# Assuming AgentMemory and GoalReevaluationModule are available in the project
try:
    from memory.agent_memory import AgentMemory
    from agents.goal_reevaluation_module import GoalReevaluationModule
    from ui.snapshot_panel import SnapshotPanel
    from cognitive_autonomy_expansion_pack.meta_capsule_drift_engine import EXPERIMENTAL_FEATURES
except ImportError:
    # Mock classes for standalone testing
    class AgentMemory:
        def log_event(self, event): pass
        def get_reasoning_history(self): return []
        def add_reasoning_pattern(self, pattern_name): pass
        def store_llm_interaction(self, log_entry): pass

    class GoalReevaluationModule:
        pass

    class SnapshotPanel:
        pass
    EXPERIMENTAL_FEATURES = {"chaos_pack": True}


class GenesisMetaReasoner:
    """
    Enhanced Meta Reasoning Engine with live LLM integration.
    Analyzes past reasoning patterns, generates hypotheses with LLM assistance,
    proposes strategy refinements, and integrates with AgentMemory.
    """

    def __init__(self, llm=None, agent_memory=None, goal_reevaluator=None,
                 snapshot_panel=None, capsule=None, live_mode=False):
        self.llm = llm
        self.agent_memory = agent_memory
        self.goal_reevaluator = goal_reevaluator
        self.snapshot_panel = snapshot_panel
        self.capsule = capsule
        self.live_mode = live_mode
        self.last_reasoning_cycle = None
        self.reasoning_log: List[Dict[str, Any]] = []
        self.meta_insights = []

    def _log_reasoning_cycle(self, cycle_type: str, content: str):
        """Enhanced logging with LLM correlation"""
        correlation_id = str(uuid.uuid4())
        log_entry = {
            "cycle_type": cycle_type,
            "content": content,
            "timestamp": time.time(),
            "correlation_id": correlation_id,
            "live_mode": self.live_mode
        }

        self.reasoning_log.append(log_entry)

        if self.agent_memory and hasattr(self.agent_memory, 'log_event'):
            self.agent_memory.log_event({
                "type": "meta_reasoning",
                **log_entry
            })

    def analyze_reasoning_patterns(self, recent_decisions: list = None) -> Dict[str, Any]:
        """
        Analyze reasoning patterns with live LLM assistance.
        """
        correlation_id = str(uuid.uuid4())

        # Get reasoning history
        if recent_decisions is None:
            reasoning_history = []
            if self.agent_memory and hasattr(self.agent_memory, 'get_reasoning_history'):
                reasoning_history = self.agent_memory.get_reasoning_history()
            recent_decisions = reasoning_history[-5:] if reasoning_history else []

        if self.live_mode and self.llm:
            # Live LLM analysis
            decisions_text = "\n".join([str(d) for d in recent_decisions])
            prompt = f"""Analyze the reasoning patterns in these recent AI agent decisions:

{decisions_text}

As a metacognitive analyst, identify:
1. Consistent decision-making patterns
2. Potential cognitive biases
3. Areas for improvement
4. Strategic recommendations

Provide structured analysis that would help the agent improve its reasoning."""

            analysis = self.llm.invoke(prompt)
            analysis_type = "live_llm_analysis"

            # Log LLM interaction
            if self.agent_memory and hasattr(self.agent_memory, 'store_llm_interaction'):
                self.agent_memory.store_llm_interaction({
                    "timestamp": time.time(),
                    "correlation_id": correlation_id,
                    "prompt": prompt,
                    "completion": analysis
                })
        else:
            # Fallback analysis
            analysis = self._simulate_pattern_analysis(recent_decisions)
            analysis_type = "simulated_analysis"

        result = {
            "analysis": analysis,
            "analysis_type": analysis_type,
            "decisions_count": len(recent_decisions),
            "timestamp": time.time(),
            "correlation_id": correlation_id
        }

        self._log_reasoning_cycle("pattern_analysis", analysis)
        return result

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
        if self.live_mode and self.llm_client:
            # Use LLM to generate refinements dynamically
            import uuid
            correlation_id = str(uuid.uuid4())
            prompt = "Based on the following hypotheses, propose strategy refinements:\n"
            hypotheses = self.generate_hypotheses()
            prompt += "\n".join(hypotheses) if hypotheses else "No hypotheses available."

            completion = self.llm_client.invoke(prompt)

            # Log LLM interaction in agent_memory
            import datetime
            timestamp = datetime.datetime.utcnow().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "correlation_id": correlation_id,
                "prompt": prompt,
                "completion": completion
            }
            self.agent_memory.store_llm_interaction(log_entry)

            refinements = [line.strip()
                           for line in completion.split("\n") if line.strip()]
            self._log_reasoning_cycle(
                "propose_strategy_refinements", refinements)
            return refinements
        else:
            hypotheses = self.generate_hypotheses()
            refinements = []
            for hypothesis in hypotheses:
                refinements.append(
                    f"Refinement proposal based on: {hypothesis}")

            self._log_reasoning_cycle(
                "propose_strategy_refinements", refinements)
            return refinements

    def feedback_loop(self):
        """
        Integrate with Goal Reevaluation Module to update goals based on reasoning outcomes.
        """
        if self.live_mode and self.llm_client:
            # Use LLM to detect cognitive dissonance or propose new self-reflection tasks
            import uuid
            correlation_id = str(uuid.uuid4())
            prompt = "Analyze the current strategy refinements and detect any cognitive dissonance or propose new self-reflection tasks:\n"
            refinements = self.propose_strategy_refinements()
            prompt += "\n".join(refinements) if refinements else "No refinements available."

            completion = self.llm_client.invoke(prompt)

            # Log LLM interaction in agent_memory
            import datetime
            timestamp = datetime.datetime.utcnow().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "correlation_id": correlation_id,
                "prompt": prompt,
                "completion": completion
            }
            self.agent_memory.store_llm_interaction(log_entry)

            # Optionally parse completion into tasks/goals and reevaluate
            new_tasks = [line.strip()
                         for line in completion.split("\n") if line.strip()]
            for task in new_tasks:
                self.goal_reevaluator.reevaluate_goal(task)

            self._log_reasoning_cycle("feedback_loop", new_tasks)
        else:
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

    def _simulate_pattern_analysis(self, recent_decisions: list) -> str:
        """Fallback pattern analysis when live_mode=False"""
        if not recent_decisions:
            return "No recent decisions available for pattern analysis."

        # Simple pattern detection
        patterns = []

        # Count decision types
        decision_types = {}
        for decision in recent_decisions:
            decision_str = str(decision)
            decision_types[decision_str] = decision_types.get(
                decision_str, 0) + 1

        # Identify repeated patterns
        repeated = [
            f"Repeated pattern: {k} ({v} times)" for k, v in decision_types.items() if v > 1]
        if repeated:
            patterns.extend(repeated)

        patterns.append(f"Analyzed {len(recent_decisions)} recent decisions.")
        patterns.append(
            "Recommendation: Continue monitoring for emerging patterns.")

        return " ".join(patterns)

    def propose_reasoning_improvement(self, current_strategy: Dict = None) -> Dict[str, Any]:
        """Propose reasoning improvements with live LLM assistance"""
        correlation_id = str(uuid.uuid4())

        if current_strategy is None:
            current_strategy = {"type": "default",
                                "description": "Standard reasoning approach"}

        if self.live_mode and self.llm:
            # Live LLM improvement suggestions
            strategy_text = str(current_strategy)
            prompt = f"""As a strategic reasoning advisor for an autonomous AI agent, analyze this current strategy:

{strategy_text}

Propose specific improvements to:
1. Decision-making processes
2. Risk assessment methods
3. Goal prioritization
4. Cognitive flexibility

Provide actionable recommendations that enhance reasoning capabilities."""

            improvements = self.llm.invoke(prompt)
            improvement_type = "live_llm_improvement"

            # Log LLM interaction
            if self.agent_memory and hasattr(self.agent_memory, 'store_llm_interaction'):
                self.agent_memory.store_llm_interaction({
                    "timestamp": time.time(),
                    "correlation_id": correlation_id,
                    "prompt": prompt,
                    "completion": improvements
                })
        else:
            # Fallback improvements
            improvements = self._simulate_improvement_suggestions(
                current_strategy)
            improvement_type = "simulated_improvement"

        result = {
            "improvements": improvements,
            "improvement_type": improvement_type,
            "current_strategy": current_strategy,
            "timestamp": time.time(),
            "correlation_id": correlation_id
        }

        self._log_reasoning_cycle("reasoning_improvement", improvements)
        return result

    def _simulate_improvement_suggestions(self, current_strategy: Dict) -> str:
        """Fallback improvement suggestions when live_mode=False"""
        suggestions = [
            "Consider implementing decision trees for complex choices.",
            "Add risk assessment scoring to evaluate potential outcomes.",
            "Incorporate feedback loops to learn from past decisions.",
            "Implement parallel reasoning to consider multiple approaches.",
            "Add uncertainty quantification to decision confidence."
        ]

        return f"Strategy improvement suggestions for {current_strategy.get('type', 'unknown')}: " + "; ".join(suggestions)
