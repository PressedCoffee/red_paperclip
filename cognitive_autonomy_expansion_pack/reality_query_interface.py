import datetime
import time
import uuid
from typing import Any, Dict, Optional

# Assuming AgentMemory and trading logic modules are available
from memory.agent_memory import AgentMemory
from trading.trading_logic import TradeEvaluator
from ui.snapshot_panel import SnapshotPanel


class CapsuleRealityQueryInterface:
    """
    Abstracted interface for querying external knowledge using LLM-based structured hallucinations.
    Supports live_mode and simulated_mode with shared LLM client.
    Integrates with AgentMemory and trading logic.
    Logs query/response pairs to agent snapshot.
    """

    def __init__(self, llm=None, agent_memory=None, trading_logic=None,
                 live_mode=False, snapshot_panel=None):
        self.llm = llm
        self.agent_memory = agent_memory or (
            AgentMemory() if AgentMemory else None)
        self.trading_logic = trading_logic
        self.live_mode = live_mode
        self.snapshot_panel = snapshot_panel
        self.query_log = []
        self.query_history = []

    def query_reality(self, query: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Query external reality data source with live LLM or fallback simulation.
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        timestamp = time.time()

        if self.live_mode and self.llm:
            # Live LLM mode - real reasoning
            prompt = f"""You are an expert analyst providing real-world context for an autonomous AI agent.

Query: {query}

Provide a detailed, factual response that would help an AI agent make informed decisions.
Include relevant data, trends, and actionable insights.
Format your response as factual analysis."""

            result = self.llm.invoke(prompt)
            query_type = "live_llm_query"
        else:
            # Fallback simulation mode
            result = self._simulated_query(query)
            query_type = "simulated_query"

        # Create response structure
        response = {
            "query": query,
            "result": result,
            "timestamp": timestamp,
            "correlation_id": correlation_id,
            "live_mode": self.live_mode,
            "query_type": query_type
        }        # Log to agent memory
        if self.agent_memory:
            self.agent_memory.store_query_response(query, response)

        # Store in local history
        self.query_history.append(response)
        self._log_query_response(query, response, correlation_id)

        return response

    def _simulated_query(self, query: str) -> str:
        """
        Fallback simulation for reality queries when live_mode=False
        """
        simulated_responses = {
            "market": "Market conditions show moderate volatility with bullish trends in emerging tech sectors.",
            "economic": "Current economic indicators suggest stable growth with inflation concerns.",
            "social": "Social sentiment analysis indicates increased interest in AI and automation technologies.",
            "political": "Political climate shows focus on technology regulation and digital asset policies.",
            "trading": "Trading analysis suggests balanced portfolio approaches with risk diversification.",
            "blockchain": "Blockchain adoption continues growing with focus on scalability and sustainability.",
            "default": f"Simulated analysis for: {query}. Multiple factors suggest continued monitoring required."
        }

        # Simple keyword matching for simulation
        query_lower = query.lower()
        for key, response in simulated_responses.items():
            if key in query_lower:
                return response
        return simulated_responses["default"]

    def get_query_history(self) -> list:
        """Get all query history"""
        return self.query_history

    def _log_query_response(self, query: str, response: Dict[str, Any], correlation_id: str):
        """
        Log the query and response with timestamp and correlation ID.
        """
        log_entry = {
            "type": "llm_interaction",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "prompt": f"Reality Query: {query}",
            "completion": str(response["result"]),
            "live_mode": self.live_mode
        }

        if self.agent_memory:
            self.agent_memory.store_llm_interaction(log_entry)

        self.query_log.append(log_entry)

    def get_simulation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about query performance and patterns.
        """
        total_queries = len(self.query_history)
        live_queries = sum(
            1 for q in self.query_history if q.get("live_mode", False))
        simulated_queries = total_queries - live_queries

        return {
            "total_queries": total_queries,
            "live_queries": live_queries,
            "simulated_queries": simulated_queries,
            "query_types": list(set(q.get("query_type", "unknown") for q in self.query_history))
        }

    def clear_history(self):
        """Clear query history and logs"""
        self.query_history.clear()
        self.query_log.clear()

    def export_queries(self) -> Dict[str, Any]:
        """Export all queries and responses for analysis"""
        return {
            "queries": self.query_history,
            "logs": self.query_log,
            "stats": self.get_simulation_stats(),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
