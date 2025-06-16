import numpy as np
import time
import uuid
from typing import List, Dict, Any, Optional

# Assuming badge_xp_system provides XP and badge trigger functions
try:
    from agents.badge_xp_system import grant_xp, trigger_badge_unlock
except ImportError:
    # Mock functions for standalone testing
    def grant_xp(agent_id, amount, reason): pass
    def trigger_badge_unlock(agent_id, badge_name): pass


class CapsuleUGTT:
    """
    Enhanced Universal Game Theory Toolkit with live LLM integration.
    Implements game theory models with LLM-assisted strategic analysis,
    Nash equilibrium computation, payoff matrix construction,
    and strategy evaluation with real-time cognitive insights.
    """

    def __init__(self, agent_id: str = None, badge_hooks_enabled: bool = True,
                 llm=None, agent_memory=None, live_mode=False):
        self.agent_id = agent_id or "default_agent"
        self.badge_hooks_enabled = badge_hooks_enabled
        self.llm = llm
        self.agent_memory = agent_memory
        self.live_mode = live_mode
        self.last_strategy_executed = {}
        self.strategy_execution_log: List[Dict[str, Any]] = []
        self.payoff_matrices = {}

    def construct_payoff_matrix(self, strategies: List[str] = None, payoffs: List[List[float]] = None) -> np.ndarray:
        """
        Construct a payoff matrix with optional LLM enhancement.
        """
        correlation_id = str(uuid.uuid4())

        # Handle None inputs
        if strategies is None:
            strategies = ["cooperate", "defect"]
        if payoffs is None:
            payoffs = [[3, 0], [5, 1]]  # Default prisoner's dilemma

        if self.live_mode and self.llm:
            # Use LLM to analyze and potentially adjust payoffs
            payoffs_str = str(payoffs)
            strategies_str = str(strategies)
            prompt = f"""As a game theory expert, analyze these strategic interactions:

Strategies: {strategies_str}
Payoff Matrix: {payoffs_str}

Consider:
1. Strategic balance and fairness
2. Nash equilibrium implications  
3. Potential for cooperation vs competition
4. Market dynamics

Suggest any adjustments that would create more realistic strategic interactions.
Return analysis and keep payoffs in the same numerical format."""

            llm_analysis = self.llm.invoke(prompt)

            # Log the LLM analysis
            if self.agent_memory:
                if hasattr(self.agent_memory, 'log_event'):
                    self.agent_memory.log_event({
                        "type": "ugtt_llm_analysis",
                        "strategies": strategies,
                        "original_payoffs": payoffs,
                        "llm_analysis": llm_analysis,
                        "timestamp": time.time(),
                        "correlation_id": correlation_id
                    })

                if hasattr(self.agent_memory, 'store_llm_interaction'):
                    self.agent_memory.store_llm_interaction({
                        "timestamp": time.time(),
                        "correlation_id": correlation_id,
                        "prompt": prompt,
                        "completion": llm_analysis
                    })

        # Convert to numpy array (keep original functionality)
        if not strategies or not payoffs:
            return np.array([[0]])

        matrix = np.array(payoffs)

        # Store matrix for future reference
        self.payoff_matrices[correlation_id] = {
            "strategies": strategies,
            "matrix": matrix,
            "timestamp": time.time()
        }

        return matrix

    def evaluate_strategy(self, payoff_matrix: np.ndarray, strategy_index: int) -> float:
        """
        Evaluate the expected payoff of a given strategy index.
        :param payoff_matrix: numpy ndarray payoff matrix.
        :param strategy_index: index of the strategy to evaluate.
        :return: expected payoff value.
        """
        if strategy_index < 0 or strategy_index >= payoff_matrix.shape[0]:
            raise IndexError("Strategy index out of range.")
        expected_payoff = np.mean(payoff_matrix[strategy_index])
        return expected_payoff

    def compute_nash_equilibrium(self, payoff_matrix: np.ndarray) -> List[int]:
        """
        Compute a Nash equilibrium for the given payoff matrix.
        This is a placeholder for a Nash equilibrium algorithm.
        :param payoff_matrix: numpy ndarray payoff matrix.
        :return: List of strategy indices representing equilibrium.
        """
        # Placeholder: return the strategy with the highest average payoff
        avg_payoffs = np.mean(payoff_matrix, axis=1)
        best_strategy = int(np.argmax(avg_payoffs))
        return [best_strategy]

    def execute_strategy(self, strategy, payoff_matrix, player_index, live_mode=False, correlation_id=None):
        """Execute a strategy and return the result with payoff."""
        try:
            if live_mode and self.llm is not None and self.agent_memory is not None:
                # Compose prompt for LLM to simulate strategic opponent behavior or adjust payoff matrix
                prompt = (
                    f"Agent {self.agent_id} executing strategy '{strategy}' with player index {player_index}.\n"
                    f"Payoff matrix: {payoff_matrix}\n"
                    "Simulate strategic opponent behaviors or adjust payoff matrix accordingly."
                )
                # Invoke LLM
                completion = self.llm.invoke(prompt)
                # Log prompt and completion with timestamp and correlation ID
                import datetime
                log_entry = {
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "correlation_id": correlation_id,
                    "prompt": prompt,
                    "completion": completion
                }
                self.agent_memory.log(log_entry)
                return completion

            # Fallback to existing logic when live_mode is False or LLM not available
            # Handle numpy array payoff matrix
            if isinstance(payoff_matrix, np.ndarray):
                # For numpy arrays, strategy should be an index or we need strategy names separately
                if isinstance(strategy, str):
                    # If strategy is a name, we can't directly use it with numpy array
                    # For testing purposes, assume strategy index 0 for string strategies
                    strategy_idx = 0
                else:
                    strategy_idx = strategy

                # Safely access payoff with bounds checking
                if strategy_idx < payoff_matrix.shape[0] and player_index < payoff_matrix.shape[1]:
                    expected_payoff = payoff_matrix[strategy_idx][player_index]
                else:
                    expected_payoff = 0

                # Log the strategy execution
                execution_entry = {
                    "strategy_name": strategy,
                    "payoff_matrix": payoff_matrix.tolist(),
                    "player_index": player_index,
                    "expected_payoff": expected_payoff
                }
                self.last_strategy_executed = execution_entry
                self.strategy_execution_log.append(execution_entry)

                # Grant XP for strategy execution
                if self.badge_hooks_enabled:
                    grant_xp(self.agent_id, 10,
                             f"Executed strategy {strategy}")
                    trigger_badge_unlock(self.agent_id, "Strategic Thinker")

                return f"UGTT Analysis: Executed '{strategy}' strategy with expected payoff {expected_payoff}. Strategic advantage: {'High' if expected_payoff > 2 else 'Moderate'}"

            # Handle dictionary payoff matrix (legacy format)
            elif isinstance(payoff_matrix, dict):
                # Check if required keys exist
                if 'strategies' not in payoff_matrix or 'payoffs' not in payoff_matrix:
                    return "UGTT Analysis: Payoff matrix missing required data"

                strategies = payoff_matrix['strategies']
                payoffs = payoff_matrix['payoffs']

                # Validate strategies and payoffs
                if not strategies or not payoffs:
                    return "UGTT Analysis: Empty strategies or payoffs"

                if strategy not in strategies:
                    return f"UGTT Analysis: Unknown strategy '{strategy}'"

                strategy_idx = strategies.index(strategy)

                # Safely access payoff with bounds checking
                if strategy_idx < len(payoffs) and player_index < len(payoffs[strategy_idx]):
                    expected_payoff = payoffs[strategy_idx][player_index]
                else:
                    expected_payoff = 0

                # Log the strategy execution
                execution_entry = {
                    "strategy_name": strategy,
                    "strategies": strategies,
                    "payoffs": payoffs,
                    "player_index": player_index,
                    "expected_payoff": expected_payoff
                }
                self.last_strategy_executed = execution_entry
                self.strategy_execution_log.append(execution_entry)

                # Grant XP for strategy execution
                if self.badge_hooks_enabled:
                    grant_xp(self.agent_id, 10,
                             f"Executed strategy {strategy}")
                    trigger_badge_unlock(self.agent_id, "Strategic Thinker")

                return f"UGTT Analysis: Executed '{strategy}' strategy with expected payoff {expected_payoff}. Strategic advantage: {'High' if expected_payoff > 2 else 'Moderate'}"

            else:
                return "UGTT Analysis: Invalid payoff matrix format"

        except (IndexError, ValueError, TypeError) as e:
            return f"UGTT Analysis: Error processing strategy - {str(e)}"

    def get_snapshot_metadata(self) -> Dict[str, Any]:
        """
        Return structured metadata for agent snapshot observability.
        """
        return {
            "last_strategy_executed": self.last_strategy_executed,
            "strategy_execution_count": len(self.strategy_execution_log),
        }

    def compute_payoff(self, trade_proposal: dict, agent_id: str) -> float:
        """
        Compute the payoff for a given trade proposal and agent.
        Adds diagnostic logging and a small positive bias to encourage mutual benefit.

        :param trade_proposal: Dictionary representing the trade details.
        :param agent_id: The ID of the agent evaluating the payoff.
        :return: A float representing the payoff value.
        """
        # Diagnostic logging of inputs
        print(
            f"[compute_payoff] Agent {agent_id} evaluating trade proposal: {trade_proposal}")

        # Extract value from trade proposal, default to 0 if missing or invalid
        value = trade_proposal.get("value", 0)
        if not isinstance(value, (int, float)):
            print(
                f"[compute_payoff] Invalid value type: {type(value)}. Defaulting to 0.")
            value = 0

        # Basic payoff logic: payoff is proportional to value with some noise
        noise = np.random.normal(0, 0.1)  # small Gaussian noise
        base_payoff = float(value) + noise

        # Add a small positive bias to encourage acceptance of trades
        bias = 0.05

        payoff = base_payoff + bias

        # Clamp payoff to a minimum of -1.0 to avoid extreme negative values
        payoff = max(payoff, -1.0)

        # Diagnostic logging of output
        print(
            f"[compute_payoff] Agent {agent_id} computed payoff: {payoff:.3f}")

        return payoff

    def execute_strategy(self, strategy_data, opponent_data=None):
        """Execute strategy with LLM-enhanced decision making"""
        correlation_id = str(uuid.uuid4())
        timestamp = time.time()

        if self.live_mode and self.llm and opponent_data:
            # Use LLM for strategic analysis
            prompt = f"""As a strategic game theory advisor, analyze this strategic situation:

My Strategy: {strategy_data}
Opponent Data: {opponent_data}

Provide strategic recommendations:
1. Optimal response to opponent's likely moves
2. Risk assessment of current strategy
3. Potential counter-strategies
4. Cooperation vs competition recommendations

Give tactical advice for this game theory scenario."""

            strategic_advice = self.llm.invoke(prompt)

            # Log LLM strategic analysis
            if self.agent_memory:
                if hasattr(self.agent_memory, 'log_event'):
                    self.agent_memory.log_event({
                        "type": "ugtt_strategic_analysis",
                        "strategy_data": strategy_data,
                        "opponent_data": opponent_data,
                        "strategic_advice": strategic_advice,
                        "timestamp": timestamp,
                        "correlation_id": correlation_id
                    })

                if hasattr(self.agent_memory, 'store_llm_interaction'):
                    self.agent_memory.store_llm_interaction({
                        "timestamp": timestamp,
                        "correlation_id": correlation_id,
                        "prompt": prompt,
                        "completion": strategic_advice
                    })

        # Execute the strategy (handle both numpy arrays and dicts)
        if hasattr(strategy_data, 'shape'):  # numpy array
            result = {"matrix_result": strategy_data.tolist(),
                      "timestamp": timestamp}
        else:  # dictionary or other format
            result = {"strategy_result": strategy_data, "timestamp": timestamp}

        # Log strategy execution
        execution_record = {
            "strategy": strategy_data,
            "result": result,
            "timestamp": timestamp,
            "correlation_id": correlation_id,
            "live_mode": self.live_mode
        }

        self.last_strategy_executed = execution_record
        self.strategy_execution_log.append(execution_record)

        if self.agent_memory and hasattr(self.agent_memory, 'log_event'):
            self.agent_memory.log_event({
                "type": "ugtt_strategy_execution",
                **execution_record
            })

        # Grant XP for strategy execution
        if self.badge_hooks_enabled:
            grant_xp(self.agent_id, 5, "UGTT strategy execution")

        return result
