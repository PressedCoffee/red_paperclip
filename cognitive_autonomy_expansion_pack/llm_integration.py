"""
LLM Integration Helper for Cognitive Autonomy Expansion Pack
Provides unified LLM setup and agent integration utilities
"""

import os
from typing import Dict, Any, Optional
from .shared_llm_client import get_shared_llm

try:
    from .reality_query_interface import CapsuleRealityQueryInterface
    from .meta_reasoning_engine import GenesisMetaReasoner
    from .ugtt_module import CapsuleUGTT
    from .self_modification_request import GenesisSelfModificationRequest
    from .meta_capsule_drift_engine import MetaCapsule
except ImportError as e:
    print(f"Warning: Could not import all cognitive modules: {e}")


def create_llm_enabled_cognitive_pack(agent_memory=None, live_mode=True, agent_id="default", capsule_registry=None, goal_module=None) -> Dict[str, Any]:
    """Create a complete cognitive autonomy pack with shared LLM"""

    # Get shared LLM client
    shared_llm = get_shared_llm() if live_mode and os.environ.get(
        "OPENAI_API_KEY") else None

    # Create all modules with shared LLM
    components = {}

    try:
        components['reality_query'] = CapsuleRealityQueryInterface(
            llm=shared_llm,
            agent_memory=agent_memory,
            live_mode=live_mode
        )
    except Exception as e:
        print(f"Warning: Could not create reality_query: {e}")

    try:
        components['meta_reasoner'] = GenesisMetaReasoner(
            llm=shared_llm,
            agent_memory=agent_memory,
            live_mode=live_mode
        )
    except Exception as e:
        print(f"Warning: Could not create meta_reasoner: {e}")

    try:
        components['ugtt_module'] = CapsuleUGTT(
            agent_id=agent_id,
            llm=shared_llm,
            agent_memory=agent_memory,
            live_mode=live_mode
        )
    except Exception as e:
        print(f"Warning: Could not create ugtt_module: {e}")

    # Add self-modification module with proper dependencies
    try:
        if capsule_registry and goal_module:
            components['self_modification'] = GenesisSelfModificationRequest(
                capsule_registry=capsule_registry,
                goal_module=goal_module,
                agent_memory=agent_memory,
                llm=shared_llm,
                live_mode=live_mode
            )
        else:
            print(
                "Info: GenesisSelfModificationRequest requires capsule_registry and goal_module")
    except Exception as e:
        print(f"Info: GenesisSelfModificationRequest creation failed: {e}")

    try:
        # MetaCapsule requires goal, values, and tags - create a basic example
        components['drift_engine'] = MetaCapsule(
            goal="cognitive_exploration",
            values={"curiosity": 0.8, "collaboration": 0.7, "efficiency": 0.6},
            tags=["cognitive", "autonomous", "adaptive"],
            agent_memory=agent_memory,
            llm=shared_llm,
            live_mode=live_mode
        )
    except Exception as e:
        print(f"Info: MetaCapsule not yet fully integrated: {e}")

    return components


def add_llm_to_agent(agent, live_mode=True, agent_id=None):
    """Add LLM-enabled cognitive autonomy to an existing agent"""

    if agent_id is None:
        agent_id = getattr(agent, 'agent_id', 'unknown_agent')

    # Create cognitive components
    cognitive_pack = create_llm_enabled_cognitive_pack(
        agent_memory=getattr(agent, 'memory', None),
        live_mode=live_mode,
        agent_id=agent_id
    )

    # Add to agent
    for component_name, component in cognitive_pack.items():
        if component:
            setattr(agent, component_name, component)

    # Add shared LLM property
    agent.llm = get_shared_llm() if live_mode and os.environ.get(
        "OPENAI_API_KEY") else None
    agent.cognitive_live_mode = live_mode

    return agent


def demo_cognitive_reasoning(agent_memory=None, live_mode=True):
    """Demonstrate live cognitive reasoning capabilities"""

    print(f"🧠 Cognitive Autonomy Demo (Live Mode: {live_mode})")
    print("=" * 50)

    # Create cognitive pack
    cognitive_pack = create_llm_enabled_cognitive_pack(
        agent_memory=agent_memory,
        live_mode=live_mode
    )

    results = {}

    # Test Reality Query
    if 'reality_query' in cognitive_pack:
        print("🔍 Testing Reality Query Interface...")
        reality_result = cognitive_pack['reality_query'].query_reality(
            "What are current trends in AI and autonomous systems?"
        )
        results['reality_query'] = reality_result
        print(f"Result: {reality_result['result'][:100]}...")
        print()

    # Test Meta Reasoning
    if 'meta_reasoner' in cognitive_pack:
        print("🤔 Testing Meta Reasoning Engine...")
        meta_result = cognitive_pack['meta_reasoner'].analyze_reasoning_patterns(
            ["trade_decision_1", "coalition_choice_2", "risk_assessment_3"]
        )
        results['meta_reasoning'] = meta_result
        print(f"Analysis: {meta_result['analysis'][:100]}...")
        print()

    # Test UGTT
    if 'ugtt_module' in cognitive_pack:
        print("🎯 Testing UGTT Module...")
        payoff_matrix = cognitive_pack['ugtt_module'].construct_payoff_matrix()
        strategy_result = cognitive_pack['ugtt_module'].execute_strategy(
            {"strategy": "cooperative", "confidence": 0.8},
            {"opponent_strategy": "competitive",
                "history": ["defect", "cooperate"]}
        )
        results['ugtt'] = strategy_result
        print(f"Strategy Result: {strategy_result}")
        print()

    print("✅ Cognitive Autonomy Demo Complete!")
    return results


def get_cognitive_status(agent) -> Dict[str, Any]:
    """Get status of cognitive autonomy components for an agent"""

    status = {
        "llm_enabled": hasattr(agent, 'llm') and agent.llm is not None,
        "live_mode": getattr(agent, 'cognitive_live_mode', False),
        "components": {}
    }

    # Check each cognitive component
    cognitive_components = [
        'reality_query', 'meta_reasoner', 'ugtt_module',
        'self_modification', 'drift_engine'
    ]

    for component_name in cognitive_components:
        if hasattr(agent, component_name):
            component = getattr(agent, component_name)
            status['components'][component_name] = {
                "available": True,
                "live_mode": getattr(component, 'live_mode', False),
                "llm_enabled": hasattr(component, 'llm') and component.llm is not None
            }
        else:
            status['components'][component_name] = {"available": False}

    return status
