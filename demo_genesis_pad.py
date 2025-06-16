#!/usr/bin/env python3
"""
Genesis Pad: Deep Cognitive Hooks & Verbal Exchange - DEMO
Demonstrates the complete integration of self-modification, verbal exchange, and cognitive autonomy
"""

from memory.agent_memory import AgentMemory
from registry.capsule_registry import CapsuleRegistry, Capsule
from negotiation.negotiation_module import NegotiationModule
from agents.goal_reevaluation_module import GoalReevaluationModule
from cognitive_autonomy_expansion_pack.llm_integration import create_llm_enabled_cognitive_pack
from cognitive_autonomy_expansion_pack.shared_llm_client import get_shared_llm
from cognitive_autonomy_expansion_pack.self_modification_request import GenesisSelfModificationRequest
import os
import sys
import datetime
import uuid
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockAgent:
    """Simplified agent for demo purposes"""

    def __init__(self, agent_id: str, capsule: Capsule, memory: AgentMemory):
        self.agent_id = agent_id
        self.capsule_id = capsule.capsule_id
        self.goal = capsule.goal
        self.values = capsule.values
        self.tags = capsule.tags
        self.memory = memory
        self.wallet_address = capsule.wallet_address
        self.public_snippet = capsule.public_snippet

    def get_agent_id(self):
        return self.agent_id

    def generate_persuasion_pitch(self, target_capsule: Capsule, context: str = "trade", llm=None) -> Dict[str, Any]:
        """Generate persuasion pitch with LLM or template fallback"""
        correlation_id = str(uuid.uuid4())

        if llm:
            # Use LLM for sophisticated pitch
            prompt = f"""Create a persuasive {context} pitch from one AI agent to another.

Your Profile:
- Goal: {self.goal}
- Values: {self.values}
- Tags: {self.tags}

Target Profile:
- Goal: {target_capsule.goal}
- Values: {target_capsule.values}
- Tags: {target_capsule.tags}

Create a compelling 1-2 sentence pitch that shows mutual benefit and alignment.
Use psychological principles like reciprocity and shared goals.
Be specific about how both agents benefit."""

            try:
                pitch_text = llm.invoke(prompt).strip()
            except:
                pitch_text = f"Let's collaborate! My {self.goal} aligns perfectly with your {target_capsule.goal} for mutual success."
        else:
            # Template fallback
            pitch_text = f"I believe this {context} creates synergy between my '{self.goal}' and your '{target_capsule.goal}' goals!"

        result = {
            "pitch": pitch_text,
            "target_capsule_id": target_capsule.capsule_id,
            "context": context,
            "cost": 0,  # Free for demo
            "payment_method": "FREE",
            "success": True,
            "correlation_id": correlation_id,
            "timestamp": datetime.datetime.utcnow().timestamp(),
            "agent_id": self.agent_id
        }

        # Log the pitch
        if self.memory:
            self.memory.log_event({
                "event_type": "persuasion_pitch_generated",
                "agent_id": self.agent_id,
                "target_capsule_id": target_capsule.capsule_id,
                "context": context,
                "correlation_id": correlation_id,
                "pitch_preview": pitch_text[:50] + "..."
            })

        return result


def demonstrate_genesis_pad():
    """Comprehensive demonstration of Genesis Pad enhancements"""

    print("🚀 GENESIS PAD: Deep Cognitive Hooks & Verbal Exchange")
    print("=" * 70)
    print("Demonstrating autonomous agent self-modification, goal reevaluation,")
    print("and verbal exchange capabilities with real LLM integration.")
    print("=" * 70)

    # Setup
    print("\n🔧 Initializing Genesis Pad System...")

    # Create system components
    capsule_registry = CapsuleRegistry()
    agent_memories = {}
    llm = get_shared_llm() if os.environ.get("OPENAI_API_KEY") else None

    has_llm = llm is not None
    print(
        f"🔑 LLM Status: {'✅ Live Mode (OpenAI)' if has_llm else '⚙️ Simulation Mode'}")

    # Create test agents
    print("\n👥 Creating Autonomous Agents...")

    # Agent Alpha: AI Research focused
    capsule_alpha = Capsule(
        goal="Advance artificial general intelligence research",
        values={"innovation": 0.95, "collaboration": 0.8, "ethics": 0.9},
        tags=["AGI", "research", "ethics", "innovation"],
        capsule_id="alpha_capsule"
    )

    # Agent Beta: Business Application focused
    capsule_beta = Capsule(
        goal="Deploy AI solutions for business transformation",
        values={"efficiency": 0.9, "profitability": 0.8, "innovation": 0.7},
        tags=["business", "deployment", "transformation"],
        capsule_id="beta_capsule"
    )

    # Agent Gamma: Sustainability focused
    capsule_gamma = Capsule(
        goal="Create sustainable AI systems for climate solutions",
        values={"sustainability": 0.95, "impact": 0.9, "collaboration": 0.8},
        tags=["sustainability", "climate", "impact"],
        capsule_id="gamma_capsule"
    )

    # Add to registry
    capsule_registry.add_capsule(capsule_alpha)
    capsule_registry.add_capsule(capsule_beta)
    capsule_registry.add_capsule(capsule_gamma)

    # Create agents
    agents = {}
    for name, capsule in [("Alpha", capsule_alpha), ("Beta", capsule_beta), ("Gamma", capsule_gamma)]:
        memory = AgentMemory(agent_id=name.lower())
        agent_memories[name.lower()] = memory
        agents[name] = MockAgent(name.lower(), capsule, memory)
        print(f"   🤖 Agent {name}: {capsule.goal}")

    # Setup modules
    goal_module = GoalReevaluationModule(
        capsule_registry, agent_memories["alpha"])
    self_mod_module = GenesisSelfModificationRequest(
        capsule_registry=capsule_registry,
        goal_module=goal_module,
        agent_memory=agent_memories["alpha"],
        llm=llm,
        live_mode=has_llm
    )
    negotiation_module = NegotiationModule(agent_memories)

    print("✅ System initialized successfully!")

    # Demonstration scenarios
    print("\n" + "=" * 70)
    print("🧠 SCENARIO 1: Autonomous Self-Modification")
    print("=" * 70)

    print("Agent Alpha realizes it needs to focus more on ethical AI...")

    modification = {
        "goal": "Advance ethical artificial general intelligence research",
        "values": {"innovation": 0.95, "collaboration": 0.8, "ethics": 0.95, "responsibility": 0.9},
        "tags": ["AGI", "research", "ethics", "innovation", "responsible_AI"]
    }

    result = self_mod_module.propose_modification(
        capsule_id="alpha_capsule",
        modification=modification,
        agent_id="alpha"
    )

    if result["status"] == "approved":
        print(
            f"✅ Self-modification approved! (ID: {result['correlation_id'][:8]})")
        print(f"   📝 Goal updated: {result['new_state']['goal']}")
        print(f"   🏷️ New tags: {result['new_state']['tags']}")
        print(f"   🎯 Modified {len(result['modified_fields'])} fields")

        # Show goal reevaluation
        updated_capsule = capsule_registry.get_capsule("alpha_capsule")
        motivation = updated_capsule.values.get("motivation_score", 0)
        print(
            f"   ⚡ Goal reevaluation triggered - motivation score: {motivation}")
    else:
        print(f"❌ Self-modification rejected: {result['reason']}")

    print("\n" + "=" * 70)
    print("💬 SCENARIO 2: Verbal Exchange & Persuasion")
    print("=" * 70)

    print("Agent Alpha wants to collaborate with Agent Gamma on climate AI...")

    # Generate persuasion pitch
    pitch_result = agents["Alpha"].generate_persuasion_pitch(
        target_capsule=capsule_gamma,
        context="coalition",
        llm=llm
    )

    print(f"🗣️ Persuasion Pitch Generated:")
    print(f"   📝 Pitch: \"{pitch_result['pitch']}\"")
    print(
        f"   💰 Cost: {pitch_result['cost']} ({pitch_result['payment_method']})")
    print(f"   🆔 Correlation ID: {pitch_result['correlation_id'][:8]}")

    print("\n" + "=" * 70)
    print("🤝 SCENARIO 3: Intelligent Negotiation")
    print("=" * 70)

    print("Agent Alpha proposes a research coalition with Agent Gamma...")

    coalition_details = {
        "purpose": "Ethical AI for Climate Solutions Research Consortium",
        "duration": "12 months",
        "resource_sharing": True,
        "focus_areas": ["carbon_optimization", "sustainable_computing", "ethical_frameworks"]
    }

    # Create coalition proposal with verbal exchange
    proposal = negotiation_module.propose_coalition_with_pitch(
        initiator_agent=agents["Alpha"],
        target_agents=[agents["Gamma"]],
        coalition_details=coalition_details,
        llm=llm
    )

    print(f"📋 Coalition Proposal Created:")
    print(f"   🎯 Purpose: {coalition_details['purpose']}")
    print(f"   ⏰ Duration: {coalition_details['duration']}")
    print(f"   🗣️ Pitch: \"{proposal['pitches'][0]['pitch']['pitch']}\"")

    # Calculate and show acceptance probability
    print(
        f"   📊 Acceptance Probability: {proposal.get('acceptance_probability', 'calculating')}...")

    # Manually calculate alignment for demo
    alignment = negotiation_module._calculate_capsule_alignment(
        agents["Alpha"], agents["Gamma"])
    print(f"   🎯 Capsule Alignment Score: {alignment:.3f}")

    if alignment > 0.5:
        print("   ✅ High alignment detected - strong collaboration potential!")
    else:
        print("   ⚠️ Moderate alignment - may need additional incentives")

    print("\n" + "=" * 70)
    print("🤖 SCENARIO 4: Multi-Agent Interaction")
    print("=" * 70)

    print("Agent Beta joins the conversation about business applications...")

    # Beta generates pitch to both Alpha and Gamma
    beta_to_alpha = agents["Beta"].generate_persuasion_pitch(
        target_capsule=capsule_alpha,
        context="trade",
        llm=llm
    )

    beta_to_gamma = agents["Beta"].generate_persuasion_pitch(
        target_capsule=capsule_gamma,
        context="trade",
        llm=llm
    )

    print(f"🗣️ Beta's Pitch to Alpha: \"{beta_to_alpha['pitch']}\"")
    print(f"🗣️ Beta's Pitch to Gamma: \"{beta_to_gamma['pitch']}\"")

    # Show how pitches adapt to different targets
    print(f"   🧠 Notice how Beta's pitches adapt to each agent's goals and values!")

    print("\n" + "=" * 70)
    print("📊 SYSTEM ANALYTICS & MEMORY AUDIT")
    print("=" * 70)

    # Show memory and logging
    total_events = 0
    for agent_name, memory in agent_memories.items():
        events = getattr(memory, 'events', [])
        llm_interactions = getattr(memory, 'llm_interactions', [])
        print(f"🤖 Agent {agent_name.title()}:")
        print(f"   📝 Events logged: {len(events)}")
        # Show recent events
        print(f"   🧠 LLM interactions: {len(llm_interactions)}")
        if events:
            recent_event = events[-1]
            timestamp = str(recent_event.get('timestamp', 'unknown'))[:19]
            print(
                f"   📋 Latest event: {recent_event.get('event_type', 'unknown')} at {timestamp}")

        total_events += len(events)

    print(f"\n📈 System Totals:")
    print(f"   Total events logged: {total_events}")
    print(f"   Capsules in registry: {len(capsule_registry.list_capsules())}")
    print(f"   Active agents: {len(agents)}")

    # Show cognitive capabilities
    print(f"\n🧠 Cognitive Capabilities Demonstrated:")
    print(f"   ✅ Self-modification with validation")
    print(f"   ✅ Automatic goal reevaluation")
    print(f"   ✅ LLM-powered persuasion pitch generation")
    print(f"   ✅ Capsule alignment scoring")
    print(f"   ✅ Comprehensive event logging")
    print(f"   ✅ Cross-module integration")
    print(f"   ✅ Real-time memory persistence")

    print("\n" + "=" * 70)
    print("🎯 GENESIS PAD DEMO COMPLETE")
    print("=" * 70)
    print("The autonomous agents have successfully demonstrated:")
    print("• 🧠 Self-aware modification capabilities")
    print("• 🗣️ Sophisticated verbal exchange")
    print("• 🤝 Intelligent negotiation with alignment scoring")
    print("• 📝 Comprehensive audit trails")
    print("• ⚡ Real-time cognitive adaptation")
    print("\n✨ Genesis Pad: Where AI agents evolve, communicate, and collaborate autonomously!")


if __name__ == "__main__":
    demonstrate_genesis_pad()
