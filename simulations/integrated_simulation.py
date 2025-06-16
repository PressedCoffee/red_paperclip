import json
from registry.capsule_registry import CapsuleRegistry
import random
from datetime import datetime
from cognitive_autonomy_expansion_pack.meta_reasoning_engine import GenesisMetaReasoner
from cognitive_autonomy_expansion_pack.ugtt_module import CapsuleUGTT
from cognitive_autonomy_expansion_pack.reality_query_interface import CapsuleRealityQueryInterface
from cognitive_autonomy_expansion_pack.self_modification_request import GenesisSelfModificationRequest
from agents.agent import Agent, AgentIdentity, AgentLifecycleManager
from memory.agent_memory import AgentMemory
from agents.goal_reevaluation_module import GoalReevaluationModule
from trading.trading_logic import TradeEvaluator
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


# === Setup ===

capsule_data = {
    "agent_id": "agent_1",
    "goal": "Maximize symbolic trade influence",
    "values": ["autonomy", "curiosity", "collaboration"],
    "tags": ["strategist"],
}

# Create AgentIdentity with required parameters
agent_identity = AgentIdentity(agent_id="agent_1", capsule_id="capsule_1")
agent = Agent(capsule_data=capsule_data, agent_identity=agent_identity)

# Initialize required components
agent_memory = AgentMemory()
capsule_registry = CapsuleRegistry()
goal_reevaluator = GoalReevaluationModule(capsule_registry, agent_memory)
trade_evaluator = TradeEvaluator()

# Initialize cognitive autonomy components
meta_reasoner = GenesisMetaReasoner(agent_memory, goal_reevaluator)
ugtt = CapsuleUGTT(agent.agent_identity.agent_id)
reality_query = CapsuleRealityQueryInterface(agent_memory, trade_evaluator)

# For self_modification, use the real lifecycle manager
lifecycle_manager = AgentLifecycleManager(capsule_registry)
agent_memory = AgentMemory()
goal_module = GoalReevaluationModule(capsule_registry, agent_memory)
self_mod = GenesisSelfModificationRequest(
    capsule_registry=capsule_registry,
    goal_module=goal_module,
    agent_memory=agent_memory,
    meta_reasoner=meta_reasoner,
    lifecycle_manager=lifecycle_manager
)

# Prepare log container
log_data = {
    "agent_id": agent.agent_identity.agent_id,
    "session_start": datetime.utcnow().isoformat(),
    "steps": []
}

# === Simulation Loop ===

for step in range(5):
    step_entry = {
        "step": step + 1,
        "timestamp": datetime.utcnow().isoformat(),
        "events": []
    }

    # Meta-Reasoning
    insights = meta_reasoner.analyze_reasoning_patterns()
    print(f"[MetaReasoner] {insights}")
    step_entry["events"].append(
        {"type": "meta_reasoning", "details": insights})

    # Reality Query
    reality_fact = reality_query.query_reality("latest symbolic trade trends")
    print(f"[RealityQuery] {reality_fact}")
    step_entry["events"].append(
        {"type": "reality_query", "details": reality_fact})

    # Game Theory Scenario - create a simple payoff matrix for demonstration
    strategies = ["cooperate", "defect"]
    payoffs = [[3, 0], [5, 1]]  # Prisoner's dilemma payoffs
    payoff_matrix = ugtt.construct_payoff_matrix(strategies, payoffs)
    strategy_result = ugtt.execute_strategy("cooperate", payoff_matrix, 0)
    print(f"[UGTT] {strategy_result}")
    step_entry["events"].append(
        {"type": "ugtt_strategy", "details": strategy_result})

    # Self Modification (probabilistic)
    if random.random() < 0.4:
        mod_request = self_mod.create_request(
            agent_id=agent.agent_identity.agent_id,
            modification_details={"change": "Increase curiosity bias by 10%"},
            requires_approval=False
        )
        print(f"[SelfModification] {mod_request}")
        step_entry["events"].append(
            {"type": "self_modification", "details": mod_request})

    # Append step entry to log
    log_data["steps"].append(step_entry)

# Add session end timestamp
log_data["session_end"] = datetime.utcnow().isoformat()

# === Save Log to JSON File ===

log_filename = f"simulation_logs/agent_{agent.agent_identity.agent_id}_session.json"

# Ensure the directory exists
os.makedirs("simulation_logs", exist_ok=True)

with open(log_filename, "w") as f:
    json.dump(log_data, f, indent=4)

print(f"\n✅ Simulation complete — log saved to {log_filename}")
