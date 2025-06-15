from typing import Dict
from agents.agent import Agent
from trading.trading_logic import TradeEvaluator


def propose_trade(sender, receiver, offer):
    """
    Simulates a trade proposal between two agents.

    Args:
        sender: The agent proposing the trade
        receiver: The agent receiving the trade proposal
        offer: The item being offered

    Returns:
        dict: A dictionary containing the result of the trade proposal
    """
    # Simplified trade logic - in reality this would be more complex
    # and would involve evaluating the alignment with the agent's goals and values

    # Calculate a simple score based on tag matching
    score = 0.0
    receiver_tags = receiver.capsule_data.get("tags", [])
    receiver_values = receiver.capsule_data.get("values", [])

    for tag in offer.get("item_tags", []):
        if tag in receiver_tags:
            score += 0.3

    # Simple decision: accept if score is above threshold
    accepted = score > 0.2

    return {
        "accepted": accepted,
        "score": score,
        "proposal": offer
    }
