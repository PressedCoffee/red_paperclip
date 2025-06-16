#!/usr/bin/env python3
"""
Test script for Genesis Pad Deep Cognitive Hooks & Verbal Exchange
Tests self-modification, verbal exchange, and integrated negotiation
"""

from memory.agent_memory import AgentMemory
from registry.capsule_registry import CapsuleRegistry, Capsule
from negotiation.negotiation_module import NegotiationModule
from agents.badge_xp_system import BadgeXPSystem
from agents.goal_reevaluation_module import GoalReevaluationModule
from agents.agent import Agent, AgentIdentity
from cognitive_autonomy_expansion_pack.shared_llm_client import get_shared_llm
from cognitive_autonomy_expansion_pack.self_modification_request import GenesisSelfModificationRequest
import os
import sys
import datetime
import uuid
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGenesisPadEnhancements:
    """Test suite for Genesis Pad cognitive hooks and verbal exchange"""

    def __init__(self):
        self.test_results = {}
        self.setup_test_environment()

    def setup_test_environment(self):
        """Setup test environment with all necessary components"""
        print("🔧 Setting up test environment...")

        # Create capsule registry
        self.capsule_registry = CapsuleRegistry()

        # Create agent memories
        self.agent_memories = {}

        # Create test capsules
        self.create_test_capsules()

        # Create test agents
        self.create_test_agents()

        # Setup modules
        self.setup_modules()

        print("✅ Test environment ready!")

    def create_test_capsules(self):
        """Create test capsules for agents"""
        # Agent A: Tech-focused
        capsule_a = Capsule(
            goal="Develop innovative AI solutions",
            values={"innovation": 0.9, "efficiency": 0.8, "collaboration": 0.7},
            tags=["AI", "technology", "innovation"],
            capsule_id="agent_a_capsule"
        )

        # Agent B: Business-focused
        capsule_b = Capsule(
            goal="Build sustainable business models",
            values={"sustainability": 0.9,
                    "profitability": 0.8, "collaboration": 0.6},
            tags=["business", "sustainability", "growth"],
            capsule_id="agent_b_capsule"
        )

        # Agent C: Research-focused
        capsule_c = Capsule(
            goal="Advance scientific research",
            values={"knowledge": 0.9, "accuracy": 0.8, "innovation": 0.7},
            tags=["research", "science", "knowledge"],
            capsule_id="agent_c_capsule"
        )

        # Add to registry
        self.capsule_registry.add_capsule(capsule_a)
        self.capsule_registry.add_capsule(capsule_b)
        self.capsule_registry.add_capsule(capsule_c)

        self.test_capsules = {
            "agent_a": capsule_a,
            "agent_b": capsule_b,
            "agent_c": capsule_c
        }

    def create_test_agents(self):
        """Create test agents with the capsules"""
        self.test_agents = {}

        for agent_name, capsule in self.test_capsules.items():
            # Create agent memory
            agent_memory = AgentMemory(agent_id=agent_name)
            self.agent_memories[agent_name] = agent_memory

            # Create agent identity
            agent_identity = AgentIdentity(
                agent_id=agent_name,
                capsule_id=capsule.capsule_id
            )            # Create badge XP system
            badge_xp_system = BadgeXPSystem(self.capsule_registry)

            # Create agent
            agent = Agent(
                capsule_data=capsule.to_dict(),
                agent_identity=agent_identity,
                badge_xp_system=badge_xp_system
            )

            # Add memory reference to agent
            agent.memory = agent_memory

            self.test_agents[agent_name] = agent

    def setup_modules(self):
        """Setup cognitive and negotiation modules"""
        # Goal reevaluation module
        self.goal_module = GoalReevaluationModule(
            capsule_registry=self.capsule_registry,
            agent_memory=self.agent_memories["agent_a"]  # Use one as default
        )

        # Self-modification request module
        self.self_mod_module = GenesisSelfModificationRequest(
            capsule_registry=self.capsule_registry,
            goal_module=self.goal_module,
            agent_memory=self.agent_memories["agent_a"],
            live_mode=bool(os.environ.get("OPENAI_API_KEY"))
        )

        # Negotiation module
        self.negotiation_module = NegotiationModule(
            agent_memories=self.agent_memories
        )

        # LLM if available
        self.llm = get_shared_llm() if os.environ.get("OPENAI_API_KEY") else None

    def test_self_modification_approved(self):
        """Test successful self-modification request"""
        print("\n🧠 Testing Self-Modification (Approved)...")

        # Propose valid modification
        modification = {
            "goal": "Develop innovative AI solutions for sustainability",
            "values": {"innovation": 0.9, "efficiency": 0.8, "collaboration": 0.7, "sustainability": 0.6}
        }

        result = self.self_mod_module.propose_modification(
            capsule_id="agent_a_capsule",
            modification=modification,
            agent_id="agent_a"
        )

        success = result["status"] == "approved"
        self.test_results["self_modification_approved"] = success

        if success:
            print(f"✅ Self-modification approved: {result['correlation_id']}")
            print(f"   Modified fields: {len(result['modified_fields'])}")
            print(f"   Goal updated: {result['new_state']['goal']}")
        else:
            print(
                f"❌ Self-modification failed: {result.get('reason', 'Unknown')}")

        return success

    def test_self_modification_rejected(self):
        """Test rejected self-modification request"""
        print("\n🚫 Testing Self-Modification (Rejected)...")

        # Propose invalid modification (invalid field)
        modification = {
            "invalid_field": "This should not be allowed",
            "wallet_address": "0x123456789"  # Not allowed
        }

        result = self.self_mod_module.propose_modification(
            capsule_id="agent_b_capsule",
            modification=modification,
            agent_id="agent_b"
        )

        success = result["status"] == "rejected"
        self.test_results["self_modification_rejected"] = success

        if success:
            print(
                f"✅ Self-modification correctly rejected: {result['reason']}")
        else:
            print(
                f"❌ Self-modification should have been rejected but got: {result['status']}")

        return success

    def test_persuasion_pitch_generation(self):
        """Test persuasion pitch generation"""
        print("\n💬 Testing Persuasion Pitch Generation...")

        agent_a = self.test_agents["agent_a"]
        target_capsule = self.test_capsules["agent_b"]

        # Test with LLM if available
        pitch_result = agent_a.generate_persuasion_pitch(
            target_capsule=target_capsule,
            context="trade",
            llm=self.llm
        )

        success = (
            pitch_result["success"] and
            len(pitch_result["pitch"]) > 0 and
            "correlation_id" in pitch_result
        )

        self.test_results["pitch_generation"] = success

        if success:
            print(f"✅ Pitch generated successfully!")
            print(f"   Pitch: {pitch_result['pitch'][:100]}...")
            print(
                f"   Cost: {pitch_result['cost']} ({pitch_result['payment_method']})")
            print(f"   Correlation ID: {pitch_result['correlation_id']}")
        else:
            print(f"❌ Pitch generation failed")

        return success

    def test_trade_proposal_with_pitch(self):
        """Test trade proposal with integrated pitch"""
        print("\n🤝 Testing Trade Proposal with Pitch...")

        agent_a = self.test_agents["agent_a"]
        agent_b = self.test_agents["agent_b"]

        trade_details = {
            "offer": "AI development services",
            "request": "Business strategy consultation",
            "duration": "3 months"
        }

        proposal = self.negotiation_module.propose_trade_with_pitch(
            initiator_agent=agent_a,
            target_agent=agent_b,
            trade_details=trade_details,
            llm=self.llm
        )

        success = (
            proposal["type"] == "trade_proposal" and
            "pitch" in proposal and
            "acceptance_probability" in proposal and
            proposal["pitch"]["success"]
        )

        self.test_results["trade_with_pitch"] = success

        if success:
            print(f"✅ Trade proposal with pitch created!")
            print(
                f"   Acceptance probability: {proposal['acceptance_probability']:.2f}")
            print(f"   Pitch: {proposal['pitch']['pitch'][:80]}...")
            print(f"   Pitch cost: {proposal['pitch']['cost']}")
        else:
            print(f"❌ Trade proposal with pitch failed")

        return success

    def test_coalition_proposal_with_pitches(self):
        """Test coalition proposal with multiple pitches"""
        print("\n🤝 Testing Coalition Proposal with Pitches...")

        agent_a = self.test_agents["agent_a"]
        target_agents = [self.test_agents["agent_b"],
                         self.test_agents["agent_c"]]

        coalition_details = {
            "purpose": "AI research and business development collaboration",
            "duration": "6 months",
            "resource_sharing": True
        }

        proposal = self.negotiation_module.propose_coalition_with_pitch(
            initiator_agent=agent_a,
            target_agents=target_agents,
            coalition_details=coalition_details,
            llm=self.llm
        )

        success = (
            proposal["type"] == "coalition_proposal" and
            len(proposal["pitches"]) == 2 and
            all(p["pitch"]["success"] for p in proposal["pitches"])
        )

        self.test_results["coalition_with_pitches"] = success

        if success:
            print(f"✅ Coalition proposal with pitches created!")
            print(f"   Targets: {len(proposal['targets'])}")
            for i, pitch_data in enumerate(proposal["pitches"]):
                print(
                    f"   Pitch {i+1}: {pitch_data['pitch']['pitch'][:60]}...")
        else:
            print(f"❌ Coalition proposal with pitches failed")

        return success

    def test_memory_logging(self):
        """Test comprehensive memory logging"""
        print("\n📝 Testing Memory Logging...")

        agent_a_memory = self.agent_memories["agent_a"]

        # Check for various event types
        events = getattr(agent_a_memory, 'events', [])
        llm_interactions = getattr(agent_a_memory, 'llm_interactions', [])

        expected_event_types = [
            "self_modification_approved",
            "persuasion_pitch_generated",
            "trade_proposal_sent"
        ]

        found_event_types = set(event.get("event_type", "")
                                for event in events)

        success = len(events) > 0 and any(
            et in found_event_types for et in expected_event_types)
        self.test_results["memory_logging"] = success

        if success:
            print(f"✅ Memory logging working!")
            print(f"   Total events: {len(events)}")
            print(f"   LLM interactions: {len(llm_interactions)}")
            print(f"   Event types: {list(found_event_types)[:3]}")
        else:
            print(
                f"❌ Memory logging issues - Events: {len(events)}, Types: {found_event_types}")

        return success

    def test_capsule_alignment_calculation(self):
        """Test capsule alignment scoring"""
        print("\n🎯 Testing Capsule Alignment Calculation...")

        agent_a = self.test_agents["agent_a"]
        agent_b = self.test_agents["agent_b"]
        agent_c = self.test_agents["agent_c"]

        # Test alignment between different agent pairs
        alignment_ab = self.negotiation_module._calculate_capsule_alignment(
            agent_a, agent_b)
        alignment_ac = self.negotiation_module._calculate_capsule_alignment(
            agent_a, agent_c)
        alignment_bc = self.negotiation_module._calculate_capsule_alignment(
            agent_b, agent_c)

        # Agent A and C should have higher alignment (both innovation-focused)
        success = (
            0.0 <= alignment_ab <= 1.0 and
            0.0 <= alignment_ac <= 1.0 and
            0.0 <= alignment_bc <= 1.0 and
            alignment_ac > alignment_bc  # A-C should be more aligned than B-C
        )

        self.test_results["capsule_alignment"] = success

        if success:
            print(f"✅ Capsule alignment calculation working!")
            print(f"   A-B alignment: {alignment_ab:.3f}")
            print(f"   A-C alignment: {alignment_ac:.3f}")
            print(f"   B-C alignment: {alignment_bc:.3f}")
        else:
            print(f"❌ Capsule alignment calculation issues")

        return success

    def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 Starting Genesis Pad Enhancement Tests")
        print("=" * 60)

        tests = [
            self.test_self_modification_approved,
            self.test_self_modification_rejected,
            self.test_persuasion_pitch_generation,
            self.test_trade_proposal_with_pitch,
            self.test_coalition_proposal_with_pitches,
            self.test_memory_logging,
            self.test_capsule_alignment_calculation
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
                self.test_results[test.__name__] = False

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)

        print(f"Tests passed: {passed}/{total}")
        print(f"Success rate: {passed/total*100:.1f}%")

        if passed == total:
            print("🎉 ALL TESTS PASSED! Genesis Pad enhancements are working perfectly!")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")

        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")

        return self.test_results


def main():
    """Main test execution"""
    try:
        tester = TestGenesisPadEnhancements()
        results = tester.run_all_tests()
        return results
    except Exception as e:
        print(f"❌ Test suite failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return {}


if __name__ == "__main__":
    results = main()
