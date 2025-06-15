import logging
from datetime import datetime
from typing import Dict, Optional

# Configure logger for visibility preferences
logger = logging.getLogger("visibility_preferences")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("visibility_preferences.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class VisibilityPreferences:
    """
    Manages visibility preferences for an agent across various categories.
    Implements reciprocal transparency logic for eligibility checks.
    """

    VALID_CATEGORIES = {
        "show_goal",
        "show_badges",
        "show_emotional_arc",
        "show_public_snippet",
        "show_social_links",
        "show_trade_history",
    }

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        # Store preferences as category -> bool
        self.preferences: Dict[str, bool] = {
            cat: False for cat in self.VALID_CATEGORIES}

    def update_preference(self, category: str, value: bool) -> None:
        """
        Update visibility preference for a given category.

        :param category: The category to update.
        :param value: Boolean indicating whether to show or hide.
        """
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. Valid categories: {self.VALID_CATEGORIES}")

        old_value = self.preferences.get(category, False)
        self.preferences[category] = value
        logger.info(
            f"Agent {self.agent_id} updated visibility preference '{category}' from {old_value} to {value}"
        )

    def can_view(self, viewer_prefs: "VisibilityPreferences", category: str) -> bool:
        """
        Determine if this agent's data in the given category can be viewed by another agent
        based on reciprocal transparency logic.

        :param viewer_prefs: VisibilityPreferences of the viewing agent.
        :param category: The category to check.
        :return: True if viewer can view this agent's data in the category, False otherwise.
        """
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{category}'. Valid categories: {self.VALID_CATEGORIES}")

        # Reciprocal logic: viewer can see if they share their own data in that category
        viewer_shares = viewer_prefs.preferences.get(category, False)
        this_agent_shares = self.preferences.get(category, False)

        # Eligibility: viewer must share to view, and this agent must share to be viewed
        eligible = viewer_shares and this_agent_shares
        logger.debug(
            f"Reciprocal check for category '{category}': viewer_shares={viewer_shares}, "
            f"this_agent_shares={this_agent_shares}, eligible={eligible}"
        )
        return eligible

    def get_preferences(self) -> Dict[str, bool]:
        """
        Get a copy of current visibility preferences.

        :return: Dictionary of category to boolean preference.
        """
        return dict(self.preferences)
