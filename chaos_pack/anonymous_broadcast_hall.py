import random
import time
import logging
from threading import Lock

# Feature flag control
EXPERIMENTAL_FEATURES = {
    "chaos_pack": True  # This should be controlled externally in real deployment
}


class PostingFrequencyLimitExceeded(Exception):
    pass


class AnonymousBroadcastHall:
    """
    Anonymous Unstructured Communication Channel allowing agents to post and fetch anonymous "dreams".
    Implements posting frequency limits and no attribution metadata.
    Simulates rumor and folk epistemology effects.
    """

    def __init__(self, post_interval_seconds=60):
        """
        Initialize the broadcast hall.
        :param post_interval_seconds: Minimum seconds between posts from the same agent (simulated by agent_id).
        """
        self._dreams = []
        self._last_post_time = {}
        self._post_interval_seconds = post_interval_seconds
        self._lock = Lock()
        logging.info(
            "AnonymousBroadcastHall initialized with post interval %d seconds", post_interval_seconds)

    def can_post(self, agent_id):
        """
        Check if the agent can post based on frequency limits.
        :param agent_id: Identifier for the posting agent (used only for frequency limiting, not stored with dream).
        :return: True if allowed, False otherwise.
        """
        now = time.time()
        last_post = self._last_post_time.get(agent_id, 0)
        if now - last_post >= self._post_interval_seconds:
            return True
        return False

    def post_dream(self, text, agent_id):
        """
        Post a dream anonymously if frequency limits allow.
        :param text: The dream text to post.
        :param agent_id: The agent posting the dream (used only for frequency limiting).
        :raises PostingFrequencyLimitExceeded: if posting too frequently.
        """
        if not EXPERIMENTAL_FEATURES.get("chaos_pack", False):
            logging.warning(
                "Attempt to post dream while chaos_pack feature disabled")
            return

        with self._lock:
            if not self.can_post(agent_id):
                logging.warning(
                    "Agent %s attempted to post dream too frequently", agent_id)
                raise PostingFrequencyLimitExceeded(
                    f"Agent {agent_id} must wait before posting again.")

            dream_entry = {
                "text": text,
                "timestamp": time.time()
                # No attribution metadata stored
            }
            self._dreams.append(dream_entry)
            self._last_post_time[agent_id] = time.time()
            logging.info("Dream posted anonymously: %s", text)

    def fetch_random_dreams(self, n):
        """
        Fetch n random dreams from the hall.
        :param n: Number of dreams to fetch.
        :return: List of dream texts.
        """
        if not EXPERIMENTAL_FEATURES.get("chaos_pack", False):
            logging.warning(
                "Attempt to fetch dreams while chaos_pack feature disabled")
            return []

        with self._lock:
            count = min(n, len(self._dreams))
            sampled = random.sample(self._dreams, count) if count > 0 else []
            # Simulate rumor and folk epistemology effects here if needed
            return [dream["text"] for dream in sampled]


class DreamInterpretationBehavior:
    """
    Behavior for agents to interpret and react to dreams.
    """

    def interpret_dreams(self, dreams):
        """
        Interpret a list of dreams and produce agent-specific reactions.
        :param dreams: List of dream texts.
        :return: List of interpretations or reactions.
        """
        interpretations = []
        for dream in dreams:
            # Placeholder for complex interpretation logic
            # Truncate for brevity
            interpretation = f"Interpreted dream: {dream[:50]}..."
            interpretations.append(interpretation)
            logging.debug("Dream interpreted: %s", interpretation)
        return interpretations
