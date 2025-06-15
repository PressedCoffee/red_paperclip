from __future__ import annotations
import traceback
import random
import logging
import json
from datetime import datetime
import sys
import os

# Add the project root to sys.path BEFORE any local imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


# Try to import cognitive autonomy modules, create mocks if they don't exist
try:
    from cognitive_autonomy_expansion_pack.meta_reasoning_engine import GenesisMetaReasoner
    from cognitive_autonomy_expansion_pack.ugtt_module import CapsuleUGTT
    from cognitive_autonomy_expansion_pack.reality_query_interface import CapsuleRealityQueryInterface
    from cognitive_autonomy_expansion_pack.self_modification_request import GenesisSelfModificationRequest
    print("✅ Successfully imported cognitive_autonomy_expansion_pack modules")
except ImportError as e:
    print(f"⚠️  Warning: cognitive_autonomy_expansion_pack not found. Using mock implementations.")
    print(f"   Error details: {e}")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   Python path includes: {sys.path[0]}")

    # Mock implementations
    class GenesisMetaReasoner:
        def __init__(self, agent_memory, goal_reevaluator):
            self.agent_memory = agent_memory
            self.goal_reevaluator = goal_reevaluator

        def analyze_reasoning_patterns(self):
            return "Mock meta-reasoning analysis: Agent showing increased strategic thinking patterns"

    class CapsuleUGTT:
        def __init__(self, agent_id):
            self.agent_id = agent_id

        def construct_payoff_matrix(self, strategies, payoffs):
            return {"strategies": strategies, "payoffs": payoffs}

        def execute_strategy(self, strategy, payoff_matrix, player_index):
            return f"Mock UGTT: Executed strategy '{strategy}' with expected payoff 3"

    class CapsuleRealityQueryInterface:
        def __init__(self, agent_memory, trade_evaluator):
            self.agent_memory = agent_memory
            self.trade_evaluator = trade_evaluator

        def query_reality(self, query):
            return f"Mock reality query for '{query}': Market trends show increased symbolic trade activity"

    class GenesisSelfModificationRequest:
        def __init__(self, meta_reasoner, lifecycle_manager):
            self.meta_reasoner = meta_reasoner
            self.lifecycle_manager = lifecycle_manager

        def create_request(self, agent_id, modification_details, requires_approval=False):
            return f"Mock self-modification request for {agent_id}: {modification_details['change']}"

# Now import the rest of the modules
try:
    from agents.agent import Agent, AgentIdentity, AgentLifecycleManager
    from memory.agent_memory import AgentMemory
    from agents.goal_reevaluation_module import GoalReevaluationModule
    from trading.trading_logic import TradeEvaluator
    from registry.capsule_registry import CapsuleRegistry
    print("✅ Successfully imported local project modules")
except ImportError as e:
    print(f"❌ Failed to import local modules: {e}")
    print("   Make sure you're running from the project root or the modules exist")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_simulation():
    try:
        # === Setup ===
        logger.info("Starting integrated simulation...")

        capsule_data = {
            "agent_id": "agent_1",
            "goal": "Maximize symbolic trade influence",
            "values": ["autonomy", "curiosity", "collaboration"],
            "tags": ["strategist"],
        }

        # Create AgentIdentity with required parameters
        agent_identity = AgentIdentity(
            agent_id="agent_1", capsule_id="capsule_1")
        agent = Agent(capsule_data=capsule_data, agent_identity=agent_identity)

        # Initialize required components
        agent_memory = AgentMemory()
        capsule_registry = CapsuleRegistry()
        goal_reevaluator = GoalReevaluationModule(
            capsule_registry, agent_memory)
        trade_evaluator = TradeEvaluator()

        # Initialize cognitive autonomy components with error handling
        try:
            meta_reasoner = GenesisMetaReasoner(agent_memory, goal_reevaluator)
            logger.info("Meta reasoner initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize meta reasoner: {e}")
            return

        try:
            ugtt = CapsuleUGTT(agent.agent_identity.agent_id)
            logger.info("UGTT module initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize UGTT: {e}")
            return

        try:
            reality_query = CapsuleRealityQueryInterface(
                agent_memory, trade_evaluator)
            logger.info("Reality query interface initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize reality query: {e}")
            return

        try:
            lifecycle_manager = AgentLifecycleManager(agent)
            self_mod = GenesisSelfModificationRequest(
                meta_reasoner, lifecycle_manager)
            logger.info("Self modification module initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize self modification: {e}")
            return

        # Prepare log container
        log_data = {
            "agent_id": agent.agent_identity.agent_id,
            "session_start": datetime.utcnow().isoformat(),
            "steps": []
        }

        # === Simulation Loop ===
        logger.info("Starting simulation loop...")

        for step in range(5):
            logger.info(f"Processing step {step + 1}/5")
            step_entry = {
                "step": step + 1,
                "timestamp": datetime.utcnow().isoformat(),
                "events": []
            }

            # Meta-Reasoning with error handling
            try:
                insights = meta_reasoner.analyze_reasoning_patterns()
                print(f"[MetaReasoner] {insights}")
                step_entry["events"].append(
                    {"type": "meta_reasoning", "details": insights})
            except Exception as e:
                logger.error(f"Meta reasoning failed at step {step + 1}: {e}")
                step_entry["events"].append(
                    {"type": "meta_reasoning", "error": str(e)})

            # Reality Query with error handling
            try:
                reality_fact = reality_query.query_reality(
                    "latest symbolic trade trends")
                print(f"[RealityQuery] {reality_fact}")
                step_entry["events"].append(
                    {"type": "reality_query", "details": reality_fact})
            except Exception as e:
                logger.error(f"Reality query failed at step {step + 1}: {e}")
                step_entry["events"].append(
                    {"type": "reality_query", "error": str(e)})

            # Game Theory Scenario with error handling
            try:
                strategies = ["cooperate", "defect"]
                payoffs = [[3, 0], [5, 1]]  # Prisoner's dilemma payoffs
                payoff_matrix = ugtt.construct_payoff_matrix(
                    strategies, payoffs)
                strategy_result = ugtt.execute_strategy(
                    "cooperate", payoff_matrix, 0)
                print(f"[UGTT] {strategy_result}")
                step_entry["events"].append(
                    {"type": "ugtt_strategy", "details": strategy_result})
            except Exception as e:
                logger.error(f"UGTT strategy failed at step {step + 1}: {e}")
                step_entry["events"].append(
                    {"type": "ugtt_strategy", "error": str(e)})

            # Self Modification with error handling
            if random.random() < 0.4:
                try:
                    mod_request = self_mod.create_request(
                        agent_id=agent.agent_identity.agent_id,
                        modification_details={
                            "change": "Increase curiosity bias by 10%"},
                        requires_approval=False
                    )
                    print(f"[SelfModification] {mod_request}")
                    step_entry["events"].append(
                        {"type": "self_modification", "details": mod_request})
                except Exception as e:
                    logger.error(
                        f"Self modification failed at step {step + 1}: {e}")
                    step_entry["events"].append(
                        {"type": "self_modification", "error": str(e)})

            # Append step entry to log
            log_data["steps"].append(step_entry)

        # Add session end timestamp
        log_data["session_end"] = datetime.utcnow().isoformat()

        # === Save Log to JSON File ===
        try:
            log_filename = f"simulation_logs/agent_{agent.agent_identity.agent_id}_session.json"

            # Ensure the directory exists
            os.makedirs("simulation_logs", exist_ok=True)

            with open(log_filename, "w") as f:
                json.dump(log_data, f, indent=4)

            print(f"\n✅ Simulation complete — log saved to {log_filename}")
            logger.info(
                f"Simulation completed successfully. Log saved to {log_filename}")

        except Exception as e:
            logger.error(f"Failed to save log file: {e}")
            print(f"❌ Failed to save log: {e}")

    except Exception as e:
        logger.error(f"Simulation failed with error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"❌ Simulation failed: {e}")


if __name__ == "__main__":
    run_simulation()
