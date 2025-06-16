#!/usr/bin/env python3
"""
Test script for LLM Integration across Cognitive Autonomy Expansion Pack
Tests both live mode and fallback functionality
"""

from cognitive_autonomy_expansion_pack.llm_integration import (
    create_llm_enabled_cognitive_pack,
    demo_cognitive_reasoning,
    get_cognitive_status
)
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


try:
    from memory.agent_memory import AgentMemory
except ImportError:
    # Mock AgentMemory for testing
    class AgentMemory:
        def __init__(self):
            self.events = []
            self.llm_interactions = []

        def log_event(self, event):
            self.events.append(event)
            print(f"[MEMORY] Event logged: {event.get('type', 'unknown')}")

        def store_llm_interaction(self, interaction):
            self.llm_interactions.append(interaction)
            print(
                f"[MEMORY] LLM interaction stored: {interaction.get('correlation_id', 'unknown')}")

        def get_reasoning_history(self):
            return [{"strategy": "test", "outcome": "success"}]


def test_llm_integration():
    """Test the complete LLM integration"""

    print("🧠 Testing Cognitive Autonomy Expansion Pack LLM Integration")
    print("=" * 60)

    # Test with mock memory
    test_memory = AgentMemory()

    # Check for OpenAI API key
    has_openai_key = bool(os.environ.get("OPENAI_API_KEY"))
    print(
        f"🔑 OpenAI API Key: {'✅ Found' if has_openai_key else '❌ Not found'}")

    if has_openai_key:
        print("🚀 Testing LIVE MODE with real LLM")
        live_results = demo_cognitive_reasoning(test_memory, live_mode=True)

        print("\n📊 Live Mode Results:")
        for component, result in live_results.items():
            print(f"  {component}: {str(result)[:100]}...")
    else:
        print("⚠️ No OpenAI API key - testing fallback mode only")

    print("\n🔄 Testing FALLBACK MODE")
    fallback_results = demo_cognitive_reasoning(test_memory, live_mode=False)

    print("\n📊 Fallback Mode Results:")
    for component, result in fallback_results.items():
        print(f"  {component}: {str(result)[:100]}...")

    # Test component creation
    print("\n🔧 Testing Component Creation...")
    cognitive_pack = create_llm_enabled_cognitive_pack(
        agent_memory=test_memory,
        live_mode=has_openai_key,
        agent_id="test_agent"
    )

    print(f"📦 Created components: {list(cognitive_pack.keys())}")

    # Test individual components
    print("\n🧪 Testing Individual Components...")

    # Test Reality Query
    if 'reality_query' in cognitive_pack:
        print("🔍 Reality Query Test:")
        rq_result = cognitive_pack['reality_query'].query_reality(
            "Test market analysis")
        print(
            f"   Query result: {rq_result.get('result', 'No result')[:50]}...")
        print(f"   Live mode: {rq_result.get('live_mode', False)}")

    # Test Meta Reasoning
    if 'meta_reasoner' in cognitive_pack:
        print("🤔 Meta Reasoning Test:")
        mr_result = cognitive_pack['meta_reasoner'].analyze_reasoning_patterns(
            ["decision_1", "decision_2"]
        )
        print(
            f"   Analysis: {mr_result.get('analysis', 'No analysis')[:50]}...")
        print(f"   Analysis type: {mr_result.get('analysis_type', 'unknown')}")

    # Test UGTT
    if 'ugtt_module' in cognitive_pack:
        print("🎯 UGTT Test:")
        ugtt = cognitive_pack['ugtt_module']
        matrix = ugtt.construct_payoff_matrix(
            ["cooperate", "defect"], [[3, 0], [5, 1]])
        print(f"   Matrix shape: {matrix.shape}")
        strategy_result = ugtt.execute_strategy({"type": "test_strategy"})
        print(
            f"   Strategy executed: {strategy_result.get('strategy_result', 'No result')}")

    print("\n📋 Memory Event Summary:")
    print(f"   Total events: {len(test_memory.events)}")
    print(f"   LLM interactions: {len(test_memory.llm_interactions)}")

    if test_memory.events:
        print("   Event types:", [e.get('type')
              for e in test_memory.events[-3:]])

    print("\n✅ LLM Integration Test Complete!")

    return {
        "has_openai_key": has_openai_key,
        "components_created": list(cognitive_pack.keys()),
        "total_events": len(test_memory.events),
        "llm_interactions": len(test_memory.llm_interactions)
    }


if __name__ == "__main__":
    try:
        results = test_llm_integration()
        print(f"\n🎯 Final Results: {results}")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
