from typing import Any, Dict, List, Optional


class BlockchainOpsSimulator:
    """
    Simulates symbolic on-chain consequences for trades.
    Logs blockchain operations as memory events with symbolic metadata tags.
    """

    def __init__(self):
        # Store simulated blockchain events
        self.blockchain_events: List[Dict[str, Any]] = []

    def simulate_trade_consequence(self, agent_id: str, trade_item: str, outcome: str, capsule_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Simulate the symbolic on-chain consequence of a trade.

        Args:
            agent_id (str): Identifier of the agent performing the trade.
            trade_item (str): The item involved in the trade.
            outcome (str): Outcome of the trade ('accepted' or 'rejected').
            capsule_data (Optional[Dict[str, Any]]): Capsule data containing values and tags.

        Returns:
            Dict[str, Any]: A dictionary representing the blockchain operation event.
        """
        symbolic_tags = self._generate_symbolic_tags(capsule_data)
        event = {
            "agent_id": agent_id,
            "trade_item": trade_item,
            "outcome": outcome,
            "symbolic_tags": symbolic_tags,
            "description": self._generate_event_description(trade_item, outcome, symbolic_tags),
        }
        self.blockchain_events.append(event)
        return event

    def _generate_symbolic_tags(self, capsule_data: Optional[Dict[str, Any]]) -> List[str]:
        """
        Generate symbolic metadata tags based on capsule values and tags.

        Args:
            capsule_data (Optional[Dict[str, Any]]): Capsule data containing values and tags.

        Returns:
            List[str]: List of symbolic metadata tags.
        """
        if not capsule_data:
            return []

        tags = set()
        values = capsule_data.get("values", [])
        capsule_tags = capsule_data.get("tags", [])

        # Example symbolic tags based on capsule values and tags
        if "sacrifice" in values or "sacrifice" in capsule_tags:
            tags.add("sacrifice")
        if "strategic risk" in values or "strategic risk" in capsule_tags:
            tags.add("strategic risk")
        if "opportunity" in values or "opportunity" in capsule_tags:
            tags.add("opportunity")
        if "legacy" in values or "legacy" in capsule_tags:
            tags.add("legacy")

        # Add more symbolic tag logic as needed

        return list(tags)

    def _generate_event_description(self, trade_item: str, outcome: str, symbolic_tags: List[str]) -> str:
        """
        Generate a human-readable description of the blockchain event.

        Args:
            trade_item (str): The item involved in the trade.
            outcome (str): Outcome of the trade.
            symbolic_tags (List[str]): List of symbolic metadata tags.

        Returns:
            str: Description string.
        """
        tags_str = ", ".join(
            symbolic_tags) if symbolic_tags else "no symbolic tags"
        return f"Blockchain event for trade '{trade_item}' with outcome '{outcome}', tagged with: {tags_str}."
