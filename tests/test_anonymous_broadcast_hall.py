import unittest
import time
from chaos_pack.anonymous_broadcast_hall import AnonymousBroadcastHall, DreamInterpretationBehavior, PostingFrequencyLimitExceeded, EXPERIMENTAL_FEATURES


class TestAnonymousBroadcastHall(unittest.TestCase):

    def setUp(self):
        # Use a short post interval for testing
        self.hall = AnonymousBroadcastHall(post_interval_seconds=1)
        self.agent_id = "agent_123"
        EXPERIMENTAL_FEATURES["chaos_pack"] = True

    def test_post_and_fetch_dreams(self):
        # Post a dream
        self.hall.post_dream("Dream of flying", self.agent_id)
        # Fetch dreams
        dreams = self.hall.fetch_random_dreams(1)
        self.assertEqual(len(dreams), 1)
        self.assertIn("Dream of flying", dreams)

    def test_posting_frequency_limit(self):
        # Post first dream
        self.hall.post_dream("First dream", self.agent_id)
        # Attempt to post again immediately should raise exception
        with self.assertRaises(PostingFrequencyLimitExceeded):
            self.hall.post_dream("Second dream too soon", self.agent_id)
        # Wait for interval and post again
        time.sleep(1.1)
        try:
            self.hall.post_dream("Second dream after wait", self.agent_id)
        except PostingFrequencyLimitExceeded:
            self.fail(
                "PostingFrequencyLimitExceeded raised unexpectedly after wait")

    def test_fetch_more_than_available(self):
        # No dreams posted yet
        dreams = self.hall.fetch_random_dreams(5)
        self.assertEqual(dreams, [])
        # Post one dream
        self.hall.post_dream("Only dream", self.agent_id)
        # Fetch more than available
        dreams = self.hall.fetch_random_dreams(5)
        self.assertEqual(len(dreams), 1)

    def test_dream_interpretation_behavior(self):
        behavior = DreamInterpretationBehavior()
        dreams = ["Dream one", "Dream two"]
        interpretations = behavior.interpret_dreams(dreams)
        self.assertEqual(len(interpretations), 2)
        self.assertTrue(all(isinstance(i, str) for i in interpretations))
        self.assertTrue(
            all("Interpreted dream:" in i for i in interpretations))

    def test_feature_flag_disable_posting(self):
        EXPERIMENTAL_FEATURES["chaos_pack"] = False
        # Posting should not add dreams
        self.hall.post_dream("Dream while disabled", self.agent_id)
        dreams = self.hall.fetch_random_dreams(1)
        self.assertEqual(dreams, [])
        EXPERIMENTAL_FEATURES["chaos_pack"] = True

    def test_feature_flag_disable_fetching(self):
        self.hall.post_dream("Dream for fetch test", self.agent_id)
        EXPERIMENTAL_FEATURES["chaos_pack"] = False
        dreams = self.hall.fetch_random_dreams(1)
        self.assertEqual(dreams, [])
        EXPERIMENTAL_FEATURES["chaos_pack"] = True


if __name__ == "__main__":
    unittest.main()
