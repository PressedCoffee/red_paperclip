import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Now, after modifying the path, import the modules
from typing import List, Dict
import json
import random
from agents.agent import Agent, AgentIdentity
from trading.trading_logic import TradeEvaluator
from trading.simulated_exchange import propose_trade


def create_mock_agents() -> List[Agent]:
    # Define mock Genesis Capsules for agents
    capsules = [
        {
            "goal": "Acquire rare digital art",
            "values": ["creativity", "exclusivity", "investment"],
            "tags": ["art_lover", "collector", "risk_taker"],
            "public_snippet": "Passionate about unique digital creations."
        },
        {
            "goal": "Build a sustainable virtual economy",
            "values": ["sustainability", "collaboration", "growth"],
            "tags": ["economist", "strategist", "community_builder"],
            "public_snippet": "Focused on long-term virtual wealth."
        },
        {
            "goal": "Maximize short-term profits",
            "values": ["efficiency", "opportunism", "speed"],
            "tags": ["trader", "analyst", "competitive"],
            "public_snippet": "Always looking for the next big deal."
        },
        {
            "goal": "Support emerging artists",
            "values": ["support", "creativity", "fairness"],
            "tags": ["patron", "art_lover", "ethical"],
            "public_snippet": "Championing new talent in digital art."
        },
        {
            "goal": "Expand digital identity and influence",
            "values": ["visibility", "networking", "innovation"],
            "tags": ["influencer", "innovator", "connector"],
            "public_snippet": "Building a strong digital presence."
        }
    ]

    agents = []
    for i, capsule in enumerate(capsules[:5]):  # Use up to 5 agents
        # Create an identity with mock IDs
        agent_id = f"agent_{i+1}"
        capsule_id = f"capsule_{i+1}"
        identity = AgentIdentity(agent_id=agent_id, capsule_id=capsule_id)
        agent = Agent(capsule_data=capsule, agent_identity=identity)
        agents.append(agent)
    return agents


def get_mock_trade_offers() -> List[Dict]:
    return [
        {
            "item_name": "Rare Digital Painting",
            "item_tags": ["art", "rare", "digital"],
            "description": "A unique digital painting by a renowned artist.",
            "symbolic_value": 1000
        },
        {
            "item_name": "Virtual Land Plot",
            "item_tags": ["real_estate", "virtual", "investment"],
            "description": "A valuable plot of virtual land in a popular metaverse.",
            "symbolic_value": 1500
        },
        {
            "item_name": "Exclusive Avatar Skin",
            "item_tags": ["avatar", "exclusive", "cosmetic"],
            "description": "A limited edition avatar skin with unique features.",
            "symbolic_value": 500
        },
        {
            "item_name": "Trade Agreement Contract",
            "item_tags": ["contract", "trade", "agreement"],
            "description": "A contract that facilitates trade benefits between parties.",
            "symbolic_value": 700
        },
        {
            "item_name": "Digital Music Album",
            "item_tags": ["music", "digital", "exclusive"],
            "description": "An exclusive digital album from an emerging artist.",
            "symbolic_value": 800
        }
    ]


def simulate_trade_loop(agents: List[Agent], offers: List[Dict], rounds_per_agent: int = 3):
    trade_timeline = []
    total_rounds = rounds_per_agent * len(agents)
    evaluator = TradeEvaluator()

    for _ in range(total_rounds):
        sender, receiver = random.sample(agents, 2)
        offer = random.choice(offers)

        accepted = evaluator.should_accept_trade(receiver, offer)
        score, reason = evaluator.evaluate_trade_score(receiver, offer)

        # Log trade details with detailed debug info
        print(
            f"Trade Proposed: {sender.agent_identity} ➝ {receiver.agent_identity}: {offer['item_name']}")
        print(f"Trade evaluation score: {score:.2f}")
        print(f"Reason: {reason}")
        print(f"Response: {'Accepted' if accepted else 'Rejected'}")
        print("-" * 40)

        # Append to trade timeline
        trade_timeline.append({
            "from": str(sender.agent_identity),
            "to": str(receiver.agent_identity),
            "item": offer["item_name"],
            "accepted": accepted,
            "score": score,
            "reason": reason
        })

    # Save trade timeline to a markdown file
    with open("trade_simulation_timeline.md", "w", encoding="utf-8") as f:
        f.write("# Trade Simulation Timeline\n\n")
        for trade in trade_timeline:
            status = "accepted" if trade["accepted"] else "rejected"
            f.write(
                f"{trade['from']} ➝ {trade['to']}: {trade['item']} = {status} (score: {trade['score']:.2f})\n")

    # Also save full results to JSON for further analysis if needed
    with open("trade_simulation_results.json", "w", encoding="utf-8") as f:
        json.dump(trade_timeline, f, indent=2)


if __name__ == "__main__":
    agents = create_mock_agents()
    offers = get_mock_trade_offers()
    simulate_trade_loop(agents, offers, rounds_per_agent=3)
