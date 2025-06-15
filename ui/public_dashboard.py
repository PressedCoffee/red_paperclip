from typing import Dict, Any, Optional
from ui.social_feed import SocialFeed
from ui.interaction_map import InteractionMap
from ui.snapshot_panel import SnapshotPanel


class PublicDashboard:
    """
    Backend interface exposing API endpoints for public data access.
    """

    def __init__(self, social_feed: SocialFeed, interaction_map: InteractionMap, snapshot_panel: SnapshotPanel):
        self.social_feed = social_feed
        self.interaction_map = interaction_map
        self.snapshot_panel = snapshot_panel

    def get_snapshot(self, agent_id: str) -> Dict[str, Any]:
        """
        API endpoint to get agent snapshot data.

        :param agent_id: Agent ID to query.
        :return: Snapshot data dictionary.
        """
        return self.snapshot_panel.get_agent_snapshot(agent_id)

    def get_feed(self, agent_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        API endpoint to get social feed entries.

        :param agent_id: Optional agent ID to filter feed entries.
        :param limit: Maximum number of entries to return.
        :return: Dictionary with feed entries list.
        """
        if agent_id:
            entries = self.social_feed.get_entries_by_agent(agent_id, limit)
        else:
            entries = self.social_feed.get_recent_entries(limit)
        return {"entries": entries}

    def get_interaction_map(self, agent_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        API endpoint to get interaction map data.

        :param agent_id: Optional agent ID to filter interactions.
        :param limit: Maximum number of interactions to return.
        :return: Dictionary with interaction data.
        """
        if agent_id:
            interactions = self.interaction_map.get_interactions(
                agent_id, limit)
            summary = self.interaction_map.summarize_interactions(agent_id)
            return {
                "interactions": interactions,
                "summary": summary,
            }
        else:
            links = self.interaction_map.get_relationship_links()
            return {"relationship_links": links}
