#!/usr/bin/env python3
"""
Simplified test for Genesis Pad Self-Modification functionality
Tests the core self-modification without complex agent dependencies
"""

from memory.agent_memory import AgentMemory
from registry.capsule_registry import CapsuleRegistry, Capsule
from agents.goal_reevaluation_module import GoalReevaluationModule
from cognitive_autonomy_expansion_pack.shared_llm_client import get_shared_llm
from cognitive_autonomy_expansion_pack.self_modification_request import GenesisSelfModificationRequest
import os
import sys
import datetime
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_self_modification():
    """Test the self-modification functionality"""
    print("🧠 Testing Genesis Self-Modification Request")
    print("=" * 50)

    # Setup components
    capsule_registry = CapsuleRegistry()
    agent_memory = AgentMemory(agent_id="test_agent")
    goal_module = GoalReevaluationModule(capsule_registry, agent_memory)

    # Create test capsule
    test_capsule = Capsule(
        goal="Develop AI solutions",
        values={"innovation": 0.8, "efficiency": 0.7},
        tags=["AI", "technology"],
        capsule_id="test_capsule"
    )
    capsule_registry.add_capsule(test_capsule)

    # Create self-modification module
    llm = get_shared_llm() if os.environ.get("OPENAI_API_KEY") else None
    self_mod = GenesisSelfModificationRequest(
        capsule_registry=capsule_registry,
        goal_module=goal_module,
        agent_memory=agent_memory,
        llm=llm,
        live_mode=bool(llm)
    )

    print(f"🔑 LLM Available: {bool(llm)}")
    print(f"🎯 Live Mode: {bool(llm)}")

    # Test 1: Valid modification (should be approved)
    print("\n✅ Test 1: Valid Modification")
    valid_modification = {
        "goal": "Develop innovative AI solutions for sustainability",
        "values": {"innovation": 0.9, "efficiency": 0.8, "sustainability": 0.7},
        "tags": ["AI", "technology", "sustainability"]
    }

    result = self_mod.propose_modification(
        capsule_id="test_capsule",
        modification=valid_modification,
        agent_id="test_agent"
    )

    print(f"Status: {result['status']}")
    if result['status'] == 'approved':
        print(f"Modified fields: {len(result['modified_fields'])}")
        print(f"New goal: {result['new_state']['goal']}")
        print(f"Correlation ID: {result['correlation_id']}")
    else:
        print(f"Reason: {result.get('reason', 'Unknown')}")

    # Test 2: Invalid modification (should be rejected)
    print("\n❌ Test 2: Invalid Modification")
    invalid_modification = {
        "invalid_field": "This should not work",
        "wallet_address": "0x123"
    }

    result2 = self_mod.propose_modification(
        capsule_id="test_capsule",
        modification=invalid_modification,
        agent_id="test_agent"
    )

    print(f"Status: {result2['status']}")
    print(f"Reason: {result2.get('reason', 'Unknown')}")

    # Test 3: Non-existent capsule
    print("\n🔍 Test 3: Non-existent Capsule")
    result3 = self_mod.propose_modification(
        capsule_id="nonexistent",
        modification={"goal": "test"},
        agent_id="test_agent"
    )

    print(f"Status: {result3['status']}")
    print(f"Reason: {result3.get('reason', 'Unknown')}")

    # Check memory logging
    print("\n📝 Memory Events:")
    events = getattr(agent_memory, 'events', [])
    print(f"Total events logged: {len(events)}")

    if events:
        for i, event in enumerate(events[-3:], 1):  # Show last 3 events
            print(
                f"  {i}. {event.get('event_type', 'unknown')} at {event.get('timestamp', 'unknown')}")

    # Summary
    test1_pass = result['status'] == 'approved'
    test2_pass = result2['status'] == 'rejected'
    test3_pass = result3['status'] == 'error'
    memory_pass = len(events) > 0

    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Valid modification: {'PASS' if test1_pass else 'FAIL'}")
    print(f"❌ Invalid modification: {'PASS' if test2_pass else 'FAIL'}")
    print(f"🔍 Nonexistent capsule: {'PASS' if test3_pass else 'FAIL'}")
    print(f"📝 Memory logging: {'PASS' if memory_pass else 'FAIL'}")

    all_pass = all([test1_pass, test2_pass, test3_pass, memory_pass])
    print(
        f"\n🎯 Overall: {'ALL TESTS PASSED! 🎉' if all_pass else 'Some tests failed ⚠️'}")

    return {
        "valid_modification": test1_pass,
        "invalid_modification": test2_pass,
        "nonexistent_capsule": test3_pass,
        "memory_logging": memory_pass,
        "overall": all_pass
    }


if __name__ == "__main__":
    try:
        results = test_self_modification()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
