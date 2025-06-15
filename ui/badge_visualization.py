from typing import List
from registry.capsule_registry import Capsule


class BadgeVisualization:
    """
    Placeholder visualization support for badges and XP display in the UI.
    """

    @staticmethod
    def render_badges(badges: List[Capsule]) -> str:
        """
        Render a textual placeholder for badges.

        :param badges: List of badge Capsules.
        :return: String representation for UI rendering.
        """
        if not badges:
            return "No badges earned yet."
        badge_names = [badge.values.get(
            "badge_name", "Unnamed Badge") for badge in badges]
        return "Badges: " + ", ".join(badge_names)

    @staticmethod
    def render_xp(xp: int) -> str:
        """
        Render a textual placeholder for XP display.

        :param xp: Total XP points.
        :return: String representation for UI rendering.
        """
        return f"Total XP: {xp}"
