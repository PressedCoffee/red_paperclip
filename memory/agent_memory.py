from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any
import os
import sys
import types
from dotenv import load_dotenv
from datetime import datetime

# Mock pinecone module to avoid import errors if pinecone is not installed
mock_pinecone = types.ModuleType("pinecone")
sys.modules["pinecone"] = mock_pinecone


# Load environment variables from .env file
load_dotenv()


class TradeRecord:
    """
    Represents a single trade record for an agent.
    """

    def __init__(self, trade_item: str, outcome: str, symbolic_tag: str, explanation: str):
        self.trade_item = trade_item
        self.outcome = outcome
        self.symbolic_tag = symbolic_tag
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the trade record to a dictionary representation.
        """
        return {
            "trade_item": self.trade_item,
            "outcome": self.outcome,
            "symbolic_tag": self.symbolic_tag,
            "explanation": self.explanation,
        }


class AgentMemory:
    """
    Maintains a list of trade records for each agent and interfaces with Pinecone for memory storage.
    """

    def __init__(self, agent_id=None):
        self.agent_id = agent_id or "default_agent"
        # Dictionary mapping agent identifiers to their list of trade records
        # Initialize Pinecone client
        self.agent_trade_history: Dict[str, List[TradeRecord]] = {}
        # Negotiation history and reputation hooks
        self.negotiation_history: List[dict] = []
        self.reputation_score: float = 1.0  # neutral baseline
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        # Initialize Pinecone connection here if needed
        # Use agent_id as namespace for Pinecone isolation
        self.pinecone_namespace = self.agent_id

    def add_trade_record(self, agent_id: str, trade_record: TradeRecord):
        """
        Add a trade record for an agent.
        """
        if agent_id not in self.agent_trade_history:
            self.agent_trade_history[agent_id] = []
        self.agent_trade_history[agent_id].append(trade_record)

    def get_trade_history(self, agent_id: str) -> List[TradeRecord]:
        """
        Get the trade history for an agent.
        """
        return self.agent_trade_history.get(agent_id, [])

    def clear_trade_history(self, agent_id: str):
        """
        Clear the trade history for an agent.
        """
        if agent_id in self.agent_trade_history:
            del self.agent_trade_history[agent_id]

    def log_negotiation_result(self, outcome: dict):
        """
        Log a negotiation outcome to the agent's negotiation history.
        """
        self.negotiation_history.append(outcome)

    def get_reputation(self) -> float:
        """
        Get the agent's current reputation score.
        """
        return self.reputation_score

    def update_reputation(self, delta: float):
        """
        Update the agent's reputation score by a delta amount.
        """
        self.reputation_score += delta
        # Clamp reputation to a reasonable range, e.g., 0.0 to 5.0
        self.reputation_score = max(0.0, min(self.reputation_score, 5.0))

    def get_reasoning_history(self):
        """Get the history of reasoning patterns for meta-analysis."""
        # Return existing reasoning history or create a basic one
        if hasattr(self, 'reasoning_history'):
            return self.reasoning_history
        else:
            # Initialize with some sample reasoning patterns
            self.reasoning_history = [
                {"pattern": "goal_alignment", "frequency": 5, "effectiveness": 0.8},
                {"pattern": "strategic_planning",
                    "frequency": 3, "effectiveness": 0.7},
                {"pattern": "adaptive_learning",
                    "frequency": 4, "effectiveness": 0.9}
            ]
            return self.reasoning_history

    def store_query_response(self, query, response):
        """Store a reality query and its response for future reference."""
        if not hasattr(self, 'query_history'):
            self.query_history = []

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "response": response
        }
        self.query_history.append(entry)

        # Keep only the last 50 queries to prevent memory bloat
        if len(self.query_history) > 50:
            self.query_history = self.query_history[-50:]

        return entry

    def add_reasoning_pattern(self, pattern_name, effectiveness=0.5):
        """Add a new reasoning pattern to the history."""
        if not hasattr(self, 'reasoning_history'):
            self.reasoning_history = []

        # Check if pattern already exists
        for pattern in self.reasoning_history:
            if pattern["pattern"] == pattern_name:
                pattern["frequency"] += 1
                pattern["effectiveness"] = (
                    pattern["effectiveness"] + effectiveness) / 2
                return

        # Add new pattern
        self.reasoning_history.append({
            "pattern": pattern_name,
            "frequency": 1,
            "effectiveness": effectiveness
        })

    def store_llm_interaction(self, interaction):
        """Store LLM interaction with timestamp and correlation ID for audit trail."""
        if not hasattr(self, 'llm_interactions'):
            self.llm_interactions = []

        self.llm_interactions.append(interaction)

        # Keep only the last 100 interactions to prevent memory bloat
        if len(self.llm_interactions) > 100:
            self.llm_interactions = self.llm_interactions[-100:]

        return interaction

    def log_event(self, event):
        """Log a general event for tracking agent activities."""
        if not hasattr(self, 'events'):
            self.events = []

        event_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            **event
        }
        self.events.append(event_entry)

        # Keep only the last 200 events
        if len(self.events) > 200:
            self.events = self.events[-200:]

        return event_entry
