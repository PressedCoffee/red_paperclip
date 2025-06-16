import copy
import json
import logging
import random
from typing import List, Optional

from registry.capsule_registry import Capsule
from memory.agent_memory import AgentMemory

# Feature flag control
EXPERIMENTAL_FEATURES = {
    "chaos_pack": True
}


class MetaCapsule(Capsule):
    """
    Extends the Genesis Capsule with driftable fields and drift engine.
    """

    def __init__(
        self,
        goal: str,
        values: dict,
        tags: List[str],
        value_biases: Optional[List[float]] = None,
        goal_weights: Optional[List[float]] = None,
        curiosity_mode: Optional[str] = None,
        wallet_address: Optional[str] = None,
        public_snippet: Optional[str] = None,
        capsule_id: Optional[str] = None,
        agent_memory: Optional[AgentMemory] = None,
        llm: Optional[object] = None,
        live_mode: bool = False,
    ):
        super().__init__(goal, values, tags, wallet_address, public_snippet, capsule_id)
        self.value_biases = value_biases or [0.0 for _ in range(len(values))]
        self.goal_weights = goal_weights or [1.0 for _ in range(len(values))]
        self.curiosity_mode = curiosity_mode or "neutral"
        self.agent_memory = agent_memory
        self.llm = llm
        self.live_mode = live_mode

    def snapshot_parameters(self) -> dict:
        """
        Take a snapshot of the current driftable parameters.
        """
        return {
            "value_biases": copy.deepcopy(self.value_biases),
            "goal_weights": copy.deepcopy(self.goal_weights),
            "curiosity_mode": self.curiosity_mode,
        }

    def drift_parameters(self, stress_factor: float = 0.1):
        """
        Mutate the driftable parameters to simulate memetic drift.
        :param stress_factor: Controls the magnitude of drift; higher means more change.
        """
        if self.live_mode and self.llm is not None:
            self._drift_parameters_live_mode()
            return

        if not EXPERIMENTAL_FEATURES.get("chaos_pack", False):
            logging.debug("Chaos pack feature disabled; skipping drift.")
            return

        if self.agent_memory is None:
            logging.warning("AgentMemory not set; cannot log drift.")
            return

        before_state = self.snapshot_parameters()

        # Drift value_biases: small random walk with stress factor scaling
        for i in range(len(self.value_biases)):
            change = random.uniform(-stress_factor, stress_factor)
            self.value_biases[i] += change
            # Clamp between -1.0 and 1.0
            self.value_biases[i] = max(-1.0, min(1.0, self.value_biases[i]))

        # Drift goal_weights: small random walk with stress factor scaling
        for i in range(len(self.goal_weights)):
            change = random.uniform(-stress_factor, stress_factor)
            self.goal_weights[i] += change
            # Clamp between 0.0 and 2.0
            self.goal_weights[i] = max(0.0, min(2.0, self.goal_weights[i]))

        # Drift curiosity_mode: probabilistic switch among modes
        curiosity_modes = ["neutral", "exploratory", "focused", "distracted"]
        if random.random() < stress_factor:
            current_index = curiosity_modes.index(
                self.curiosity_mode) if self.curiosity_mode in curiosity_modes else 0
            new_index = (current_index +
                         random.choice([-1, 1])) % len(curiosity_modes)
            self.curiosity_mode = curiosity_modes[new_index]

        after_state = self.snapshot_parameters()

        # Log drift event to AgentMemory
        self.log_drift(before_state, after_state)

    def log_drift(self, before_state: dict, after_state: dict):
        """
        Log the before and after states of the capsule parameters to AgentMemory.
        """
        if self.agent_memory is None:
            logging.warning("AgentMemory not set; cannot log drift.")
            return

        drift_log_entry = {
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "capsule_id": self.capsule_id,
            "before": before_state,
            "after": after_state,
        }
        # Assuming agent_memory has a method to log arbitrary events; if not, use add_trade_record or similar
        try:
            if hasattr(self.agent_memory, "log_capsule_drift"):
                self.agent_memory.log_capsule_drift(
                    self.capsule_id, drift_log_entry)
            else:
                # Fallback: log as a trade record with a special tag
                from memory.agent_memory import TradeRecord
                record = TradeRecord(
                    trade_item="capsule_drift",
                    outcome=json.dumps(drift_log_entry),
                    symbolic_tag="drift_event",
                    explanation="Memetic drift of capsule parameters"
                )
                self.agent_memory.add_trade_record(self.capsule_id, record)
            logging.info(
                f"Logged capsule drift for capsule_id {self.capsule_id}")
        except Exception as e:
            logging.error(f"Failed to log capsule drift: {e}")

    def capsule_diff_report(self) -> str:
        """
        Generate a diff report string for the last drift event for UI snapshot panels.
        """
        if self.agent_memory is None:
            logging.warning(
                "AgentMemory not set; cannot generate diff report.")
            return "No AgentMemory available."

        # Assuming agent_memory can provide last drift states
        try:
            if hasattr(self.agent_memory, "get_last_drift_states"):
                before, after = self.agent_memory.get_last_drift_states(
                    self.capsule_id)
            else:
                return "No drift states available."

            diffs = []
            for key in before:
                before_val = before[key]
                after_val = after[key]
                if before_val != after_val:
                    diffs.append(
                        f"{key} changed from {before_val} to {after_val}")

            return "\n".join(diffs) if diffs else "No changes detected."
        except Exception as e:
            logging.error(f"Failed to generate diff report: {e}")
            return f"Error generating diff report: {e}"

    def _drift_parameters_live_mode(self):
        """
        Use the LLM to generate dynamic output to mutate value weights or goal biases.
        Logs all prompts and completions in agent_memory with timestamp and correlation ID.
        """
        import uuid
        import datetime

        if self.llm is None:
            logging.warning("LLM client not set; cannot perform live drift.")
            return

        correlation_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()

        current_capsule = {
            "goal": self.goal,
            "values": self.values,
            "value_biases": self.value_biases,
            "goal_weights": self.goal_weights,
            "curiosity_mode": self.curiosity_mode,
        }

        prompt = f"Suggest new motivation drift for: {json.dumps(current_capsule)}"

        try:
            completion = self.llm.invoke(prompt)
        except Exception as e:
            logging.error(f"LLM invocation failed: {e}")
            return

        # Log prompt and completion to agent_memory
        if self.agent_memory is not None:
            log_entry = {
                "timestamp": timestamp,
                "correlation_id": correlation_id,
                "prompt": prompt,
                "completion": completion,
            }
            try:
                if hasattr(self.agent_memory, "log_llm_interaction"):
                    self.agent_memory.log_llm_interaction(
                        self.capsule_id, log_entry)
                else:
                    # Fallback: log as a trade record with a special tag
                    from memory.agent_memory import TradeRecord
                    record = TradeRecord(
                        trade_item="llm_interaction",
                        outcome=json.dumps(log_entry),
                        symbolic_tag="llm_log",
                        explanation="LLM prompt and completion log"
                    )
                    self.agent_memory.add_trade_record(self.capsule_id, record)
                logging.info(
                    f"Logged LLM interaction for capsule_id {self.capsule_id}")
            except Exception as e:
                logging.error(f"Failed to log LLM interaction: {e}")

        # Parse completion to update value_biases and goal_weights if possible
        try:
            parsed = json.loads(completion)
            if "value_biases" in parsed and isinstance(parsed["value_biases"], list):
                self.value_biases = parsed["value_biases"]
            if "goal_weights" in parsed and isinstance(parsed["goal_weights"], list):
                self.goal_weights = parsed["goal_weights"]
            if "curiosity_mode" in parsed and isinstance(parsed["curiosity_mode"], str):
                self.curiosity_mode = parsed["curiosity_mode"]
        except Exception as e:
            logging.warning(f"Failed to parse LLM completion: {e}")
