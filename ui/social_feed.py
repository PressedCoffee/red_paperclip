from typing import List, Dict, Optional
from datetime import datetime


class SocialFeed:
    """
    Stores agent-authored public posts, event logs, and trade reflections.
    """

    def __init__(self):
        self.entries: List[Dict] = []

    def append_post(self, agent_id: str, content: str, mood: Optional[str] = None, timestamp: Optional[datetime] = None) -> None:
        """
        Append a public post authored by an agent.

        :param agent_id: ID of the agent authoring the post.
        :param content: Content of the post.
        :param mood: Optional mood tag.
        :param timestamp: Optional timestamp; defaults to current time if None.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        entry = {
            "agent_id": agent_id,
            "content": content,
            "type": "post",
            "timestamp": timestamp,
            "mood": mood,
        }
        self.entries.append(entry)

    def append_event_log(self, agent_id: str, event: str, timestamp: Optional[datetime] = None) -> None:
        """
        Append an event log entry authored by an agent.

        :param agent_id: ID of the agent authoring the event.
        :param event: Description of the event.
        :param timestamp: Optional timestamp; defaults to current time if None.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        entry = {
            "agent_id": agent_id,
            "content": event,
            "type": "event_log",
            "timestamp": timestamp,
            "mood": None,
        }
        self.entries.append(entry)

    def append_trade_reflection(self, agent_id: str, trade_summary: str, timestamp: Optional[datetime] = None) -> None:
        """
        Append a trade reflection authored by an agent.

        :param agent_id: ID of the agent authoring the reflection.
        :param trade_summary: Summary of the trade.
        :param timestamp: Optional timestamp; defaults to current time if None.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        entry = {
            "agent_id": agent_id,
            "content": trade_summary,
            "type": "trade_reflection",
            "timestamp": timestamp,
            "mood": None,
        }
        self.entries.append(entry)

    def get_recent_entries(self, limit: int = 50) -> List[Dict]:
        """
        Retrieve the most recent feed entries, sorted by timestamp descending.

        :param limit: Maximum number of entries to return.
        :return: List of feed entries.
        """
        sorted_entries = sorted(
            self.entries, key=lambda e: e["timestamp"], reverse=True)
        return sorted_entries[:limit]

    def get_entries_by_agent(self, agent_id: str, limit: int = 20) -> List[Dict]:
        """
        Retrieve recent feed entries authored by a specific agent.

        :param agent_id: Agent ID to filter entries.
        :param limit: Maximum number of entries to return.
        :return: List of feed entries.
        """
        filtered = [e for e in self.entries if e["agent_id"] == agent_id]
        sorted_entries = sorted(
            filtered, key=lambda e: e["timestamp"], reverse=True)
        return sorted_entries[:limit]
