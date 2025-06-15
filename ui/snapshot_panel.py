from typing import Dict, Any, Optional, List


class SnapshotPanel:
    """
    Backend scaffolding for the Agent Snapshot Panel UI.
    Provides methods to query agent data and simulate visibility preference toggling.
    """

    def __init__(self, agent: Any, visibility_preferences: Any, agent_registry: Optional[Dict[str, Any]] = None):
        """
        Initialize the SnapshotPanel with an agent instance and visibility preferences manager.

        :param agent: The agent instance to query data from.
        :param visibility_preferences: The visibility preferences manager instance.
        :param agent_registry: Optional dict mapping agent_id to agent instances for lookup.
        """
        self.agent = agent
        self.visibility_preferences = visibility_preferences
        self.agent_registry = agent_registry or {}

    def get_public_snippet(self) -> Optional[str]:
        """
        Query the agent's public snippet.

        :return: Public snippet string or None if not available.
        """
        return getattr(self.agent, "public_snippet", None)

    def get_top_badge(self) -> Optional[str]:
        """
        Query the agent's top badge.
        Placeholder: returns the first badge from agent's tags if available.

        :return: Top badge string or None.
        """
        tags = getattr(self.agent, "tags", [])
        if tags and isinstance(tags, list):
            return tags[0]
        return None

    def get_current_mood(self) -> Optional[str]:
        """
        Query the agent's current mood.
        Placeholder: returns 'neutral' as default mood.

        :return: Current mood string.
        """
        # Placeholder for future emotional arc integration
        return "neutral"

    def get_shared_attributes(self) -> Dict[str, Any]:
        """
        Query shared attributes of the agent relevant for the snapshot panel.

        :return: Dictionary of shared attributes.
        """
        return {
            "goal": getattr(self.agent, "goal", None),
            "values": getattr(self.agent, "values", None),
            "wallet_address": getattr(self.agent, "wallet_address", None),
            "nft_assigned": getattr(self.agent, "nft_assigned", False),
        }

    def get_visibility_preferences(self) -> Dict[str, bool]:
        """
        Get the current visibility preferences for the agent.

        :return: Dictionary of category to boolean preference.
        """
        if hasattr(self.visibility_preferences, "get_preferences"):
            return self.visibility_preferences.get_preferences()
        return {}

    def toggle_visibility_preference(self, category: str) -> None:
        """
        Simulate toggling a visibility preference for the agent.

        :param category: The category to toggle.
        """
        current_prefs = self.get_visibility_preferences()
        current_value = current_prefs.get(category, False)
        if hasattr(self.visibility_preferences, "update_preference"):
            self.visibility_preferences.update_preference(
                category, not current_value)

    def get_agent_snapshot(self, agent_id: str) -> Dict:
        """
        Return a snapshot of the specified agent's data.

        :param agent_id: The ID of the agent to snapshot.
        :return: Dictionary containing snapshot data.
        """
        agent = self.agent_registry.get(agent_id)
        if not agent:
            return {}

        snapshot = {
            "public_snippet": getattr(agent, "public_snippet", None),
            "top_badge": getattr(agent, "tags", [None])[0] if getattr(agent, "tags", None) else None,
            "current_mood": "neutral",  # Placeholder
            "shared_attributes": {
                "goal": getattr(agent, "goal", None),
                "values": getattr(agent, "values", None),
                "wallet_address": getattr(agent, "wallet_address", None),
                "nft_assigned": getattr(agent, "nft_assigned", False),
            }
        }
        return snapshot

    def query_visibility_state(self, agent_id: str) -> Dict:
        """
        Return the visibility state for the specified agent.

        :param agent_id: The ID of the agent to query.
        :return: Dictionary of visibility preferences.
        """
        # For demonstration, assume visibility preferences are global or per agent in a dict
        if hasattr(self.visibility_preferences, "get_agent_preferences"):
            return self.visibility_preferences.get_agent_preferences(agent_id)
        # Fallback to global preferences
        return self.get_visibility_preferences()

    def summarize_public_data(self, agent_id: str) -> Dict:
        """
        Summarize publicly shared data for the specified agent.

        :param agent_id: The ID of the agent to summarize.
        :return: Dictionary summarizing public data.
        """
        agent = self.agent_registry.get(agent_id)
        if not agent:
            return {}

        summary = {
            "public_snippet": getattr(agent, "public_snippet", None),
            "tags": getattr(agent, "tags", []),
            "goal": getattr(agent, "goal", None),
            "values": getattr(agent, "values", None),
            "nft_assigned": getattr(agent, "nft_assigned", False),
        }
        return summary
