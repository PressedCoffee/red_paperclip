import json
import os
import random
import sys
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the project root to sys.path BEFORE any local imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Try to import cognitive autonomy modules, create mocks if they don't exist
try:
    from cognitive_autonomy_expansion_pack.meta_reasoning_engine import GenesisMetaReasoner
    from cognitive_autonomy_expansion_pack.ugtt_module import CapsuleUGTT
    from cognitive_autonomy_expansion_pack.reality_query_interface import RealityQueryInterface
    from cognitive_autonomy_expansion_pack.self_modification_request import GenesisSelfModificationRequest
    print("✅ Successfully imported cognitive_autonomy_expansion_pack modules")
except ImportError as e:
    print(f"Warning: cognitive_autonomy_expansion_pack not found. Using mock implementations.")

    # Mock implementations for multi-agent simulation
    class GenesisMetaReasoner:
        def __init__(self, agent_id, memory):
            self.agent_id = agent_id
            self.memory = memory

        def perform_meta_reasoning(self):
            return f"Mock meta-reasoning for {self.agent_id}: Strategic patterns detected"

    class CapsuleUGTT:
        def __init__(self, agent_id):
            self.agent_id = agent_id

        def execute_strategy(self):
            return f"Mock UGTT strategy execution for {self.agent_id}"

        def generate_trade_proposal(self, other_agent_id):
            return {"item": "symbolic_token", "value": random.randint(1, 10)}

        def evaluate_payoff(self, trade_proposal, agent_id):
            return random.uniform(-2, 3)  # Random payoff between -2 and 3

        def compute_payoff(self, trade_proposal, agent_id):
            # Add diagnostic logging
            print(
                f"[Mock compute_payoff] Agent {agent_id} evaluating trade proposal: {trade_proposal}")
            value = trade_proposal.get("value", 0)
            if not isinstance(value, (int, float)):
                value = 0
            noise = random.gauss(0, 0.1)
            bias = 0.05
            payoff = value + noise + bias
            payoff = max(payoff, -1.0)
            print(
                f"[Mock compute_payoff] Agent {agent_id} computed payoff: {payoff:.3f}")
            return payoff

    class RealityQueryInterface:
        def __init__(self, agent_id):
            self.agent_id = agent_id

        def query_reality(self):
            return f"Mock reality query for {self.agent_id}: Market conditions stable"

    class GenesisSelfModificationRequest:
        def __init__(self, agent_id):
            self.agent_id = agent_id

        def attempt_self_modification(self):
            return f"Mock self-modification attempt for {self.agent_id}: Cognitive enhancement requested"

# Now import the rest of the modules
try:
    from agents.agent import Agent
    from agents.badge_xp_system import BadgeXPSystem, grant_xp
    from registry.capsule_registry import CapsuleRegistry
    from ui.snapshot_panel import SnapshotPanel
    from simulations.coalition_formation import CoalitionFormation
    print("Successfully imported local project modules")
    from memory.agent_memory import AgentMemory
except ImportError as e:
    if "pinecone" in str(e):
        print("Warning: pinecone module not found. Using mock implementations for local modules.")

        class Agent:
            def __init__(self, *args, **kwargs):
                pass

        class BadgeXPSystem:
            def __init__(self, *args, **kwargs):
                pass

        def grant_xp(agent_id, amount, reason):
            print(
                f"Mock grant_xp called for {agent_id} with amount {amount} for {reason}")

        class CapsuleRegistry:
            def create_capsule(self, capsule):
                pass

        class SnapshotPanel:
            pass

        class CoalitionFormation:
            def __init__(self, agents):
                self.agents = agents

            def propose_coalition(self, *args, **kwargs):
                return None

            def accept_coalition(self, *args, **kwargs):
                return False

            def update_xp_and_badges(self, *args, **kwargs):
                pass
            next_coalition_id = 1

        class AgentMemory:
            pass
    else:
        print(f"Failed to import local modules: {e}")
        print("   Make sure you're running from the project root or the modules exist")
        sys.exit(1)


LOG_FILE_PATH = "simulation_logs/multi_agent_session.json"
NUM_AGENTS = 10
SIMULATION_STEPS = 50
TRADE_PROPOSAL_PROBABILITY = 0.3  # Probability an agent proposes a trade in a step
# Probability an agent proposes a coalition in a step
COALITION_PROPOSAL_PROBABILITY = 0.15
# Probability an agent attempts self-modification in a step
SELF_MODIFICATION_PROBABILITY = 0.1

# Adjust number of agents for easier verification
NUM_AGENTS = 3


def ensure_log_file():
    if not os.path.exists("simulation_logs"):
        os.makedirs("simulation_logs")
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w") as f:
            json.dump({}, f)


def migrate_old_logs():
    """
    Migrate old logs replacing 'fair_share' keys with 'payoff_shares' to avoid KeyError.
    """
    if not os.path.exists(LOG_FILE_PATH):
        return
    try:
        with open(LOG_FILE_PATH, "r") as f:
            logs = json.load(f)
        changed = False
        for agent_id, steps in logs.items():
            for step, actions in steps.items():
                for action in actions:
                    if "fair_share" in action:
                        action["payoff_shares"] = action.pop("fair_share")
                        changed = True
        if changed:
            with open(LOG_FILE_PATH, "w") as f:
                json.dump(logs, f, indent=2)
            print("Migrated old logs: replaced 'fair_share' with 'payoff_shares'")
    except Exception as e:
        print(f"Error migrating logs: {e}")


def log_action(agent_id: str, step: int, action: Dict[str, Any]):
    """
    Log an action for an agent at a given step.
    The log file is structured as:
    {
        "agent_id": {
            "step": [actions...]
        }
    }
    """
    try:
        with threading.Lock():
            if os.path.exists(LOG_FILE_PATH):
                with open(LOG_FILE_PATH, "r") as f:
                    logs = json.load(f)
            else:
                logs = {}

            agent_logs = logs.get(agent_id, {})
            step_logs = agent_logs.get(str(step), [])
            step_logs.append(action)
            agent_logs[str(step)] = step_logs
            logs[agent_id] = agent_logs

            with open(LOG_FILE_PATH, "w") as f:
                json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Error logging action for agent {agent_id} at step {step}: {e}")


class AutonomousAgent:
    def __init__(self, agent_id: str, goal: str, tags: List[str]):
        self.agent_id = agent_id
        self.goal = goal
        self.tags = tags

        # Initialize components
        # Use mock memory to avoid pinecone dependency
        self.memory = None
        self.capsule_registry = CapsuleRegistry()
        self.meta_reasoner = GenesisMetaReasoner(agent_id, self.memory)
        self.reality_query = RealityQueryInterface(agent_id)
        self.ugtt = CapsuleUGTT(agent_id)
        self.self_modification = GenesisSelfModificationRequest(agent_id)
        self.badge_xp_system = BadgeXPSystem(agent_id)

        # Initialize agent with a Genesis Capsule
        self.genesis_capsule = {
            "agent_id": self.agent_id,
            "goal": self.goal,
            "tags": self.tags,
        }
        self.capsule_registry.create_capsule(self.genesis_capsule)

    def run_step(self, step: int):
        # Meta-reasoning
        meta_reasoning_result = self.meta_reasoner.perform_meta_reasoning()
        log_action(self.agent_id, step, {
                   "action": "meta_reasoning", "result": meta_reasoning_result})

        # Reality query
        reality_result = self.reality_query.query_reality()
        log_action(self.agent_id, step, {
                   "action": "reality_query", "result": reality_result})

        # UGTT strategy
        ugtt_result = self.ugtt.execute_strategy()
        log_action(self.agent_id, step, {
                   "action": "ugtt_strategy", "result": ugtt_result})

        # Occasional self-modification
        if random.random() < SELF_MODIFICATION_PROBABILITY:
            self_mod_result = self.self_modification.attempt_self_modification()
            log_action(self.agent_id, step, {
                       "action": "self_modification", "result": self_mod_result})

    def propose_trade(self, other_agent: "AutonomousAgent", step: int) -> Dict[str, Any]:
        """
        Propose a symbolic trade to another agent.
        Returns a dict with trade details and acceptance status.
        """
        try:
            # Generate a symbolic trade proposal using CapsuleUGTT payoffs
            trade_proposal = self.ugtt.generate_trade_proposal(
                other_agent.agent_id)

            # Evaluate trade payoff for self and other agent
            self_payoff = self.ugtt.compute_payoff(
                trade_proposal, self.agent_id)
            other_payoff = other_agent.ugtt.compute_payoff(
                trade_proposal, other_agent.agent_id)

            # Decide acceptance based on payoffs (accept if payoff positive for both)
            total_payoff = self_payoff + other_payoff
            accepted = total_payoff > -0.1

            reason = ""
            if accepted:
                # Update XP and badges for both agents
                # Arbitrary XP for accepted trade
                grant_xp(self.agent_id, 10, "Accepted trade payoff")
                grant_xp(other_agent.agent_id, 10, "Accepted trade payoff")
                reason = f"Trade accepted: total payoff {total_payoff:.2f} > -0.1."
            else:
                reason = f"Trade rejected: total payoff {total_payoff:.2f} <= -0.1."

            # Log trade proposal and result
            trade_log = {
                "action": "trade_proposal",
                "from_agent": self.agent_id,
                "to_agent": other_agent.agent_id,
                "trade_proposal": trade_proposal,
                "self_payoff": self_payoff,
                "other_payoff": other_payoff,
                "accepted": accepted,
                "reason": reason,
                "coalition_id": None,
            }
            log_action(self.agent_id, step, trade_log)
            log_action(other_agent.agent_id, step, trade_log)

            return trade_log
        except Exception as e:
            error_log = {
                "action": "trade_proposal_error",
                "from_agent": self.agent_id,
                "to_agent": other_agent.agent_id,
                "error": str(e),
            }
            log_action(self.agent_id, step, error_log)
            return error_log


def create_agents(num_agents: int) -> List[AutonomousAgent]:
    agents = []
    for i in range(num_agents):
        agent_id = f"agent_{i+1}"
        goal = f"Goal for {agent_id}"
        tags = [f"tag_{i+1}", "autonomous", "simulation"]
        agent = AutonomousAgent(agent_id, goal, tags)
        agents.append(agent)
    return agents


def run_simulation():
    ensure_log_file()
    migrate_old_logs()
    agents = create_agents(NUM_AGENTS)
    coalition_manager = CoalitionFormation(agents)

    for step in range(1, SIMULATION_STEPS + 1):
        # Run each agent's step
        for agent in agents:
            agent.run_step(step)

        # Randomly propose coalitions between agents
        for agent in agents:
            if random.random() < COALITION_PROPOSAL_PROBABILITY:
                # Select candidate agents randomly (excluding self)
                candidate_agents = random.sample(
                    [a.agent_id for a in agents if a.agent_id != agent.agent_id],
                    k=min(2, len(agents) - 1)
                )
                proposal = coalition_manager.propose_coalition(
                    agent.agent_id, candidate_agents)
                if proposal:
                    # For simplicity, auto-accept coalition proposals
                    accepted = coalition_manager.accept_coalition(proposal)
                    if accepted:
                        # Update XP and badges for coalition members
                        badge_xp_systems = {
                            a.agent_id: a.badge_xp_system for a in agents}
                        coalition_manager.update_xp_and_badges(
                            proposal, badge_xp_systems)

                        # Log coalition proposal and acceptance
                        coalition_log = {
                            "action": "coalition_formation",
                            "coalition_id": proposal.get("coalition_id", "unknown"),
                            "members": proposal.get("members", []),
                            "pooled_payoff": proposal.get("pooled_payoff", 0),
                            # Use empty dict as default to avoid KeyError
                            "payoff_shares": proposal.get("payoff_shares", {}),
                            "accepted": True,
                        }
                        for member_id in proposal.get("members", []):
                            log_action(member_id, step, coalition_log)

                        # Increment coalition ID for next proposal
                        coalition_manager.next_coalition_id += 1

        # Randomly propose trades between agents
        for agent in agents:
            if random.random() < TRADE_PROPOSAL_PROBABILITY:
                # Choose a random other agent to propose trade to
                other_agent = random.choice(
                    [a for a in agents if a.agent_id != agent.agent_id])
                trade_log = agent.propose_trade(other_agent, step)
                # Add coalition_id to trade log if agent is in coalition
                coalition_id = getattr(
                    coalition_manager, "agent_to_coalition", None)
                if coalition_id is not None:
                    coalition_id = coalition_id.get(agent.agent_id)
                if coalition_id is not None:
                    trade_log["coalition_id"] = coalition_id
                    # Update logs with coalition_id
                    log_action(agent.agent_id, step, trade_log)
                    log_action(other_agent.agent_id, step, trade_log)

        # Save interaction graph snapshot per step
        interaction_graph_snapshot = {
            "step": step,
            "coalitions": {},
            "agents": [agent.agent_id for agent in agents],
        }
        snapshot_dir = "simulation_logs/interaction_graph_snapshots"
        if not os.path.exists(snapshot_dir):
            os.makedirs(snapshot_dir)
        snapshot_path = os.path.join(snapshot_dir, f"step_{step}.json")
        with open(snapshot_path, "w") as f:
            json.dump(interaction_graph_snapshot, f, indent=2)

        # Sleep briefly to simulate time passing (optional)
        time.sleep(0.1)


if __name__ == "__main__":
    print(
        f"Starting multi-agent interaction simulation with {NUM_AGENTS} agents for {SIMULATION_STEPS} steps.")
    run_simulation()
    print(f"Simulation complete. Logs saved to {LOG_FILE_PATH}.")
