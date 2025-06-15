import unittest
import logging
from unittest.mock import patch

import world_dynamics as wd


class TestBlackSwanEngine(unittest.TestCase):

    def setUp(self):
        # Ensure engine is enabled before each test
        wd.enable_black_swan_engine()
        wd.EXPERIMENTAL_FEATURES["chaos_pack"] = True

    def test_feature_flag_disabled(self):
        wd.EXPERIMENTAL_FEATURES["chaos_pack"] = False
        event_id = wd.inject_chaotic_event()
        self.assertIsNone(event_id)
        wd.EXPERIMENTAL_FEATURES["chaos_pack"] = True

    def test_safety_circuit_breaker_disabled(self):
        wd.disable_black_swan_engine()
        event_id = wd.inject_chaotic_event()
        self.assertIsNone(event_id)
        wd.enable_black_swan_engine()

    def test_manual_event_valid(self):
        event_id = wd.inject_chaotic_event(manual_event="trade_freeze")
        self.assertIsNotNone(event_id)

    def test_manual_event_invalid(self):
        with self.assertLogs(level='ERROR') as log:
            event_id = wd.inject_chaotic_event(manual_event="invalid_event")
            self.assertIsNone(event_id)
            self.assertTrue(
                any("Invalid manual_event" in message for message in log.output))

    def test_stochastic_event(self):
        event_id = wd.inject_chaotic_event()
        self.assertIsNotNone(event_id)

    @patch('world_dynamics.apply_event_effects')
    def test_apply_event_effects_exception(self, mock_apply):
        mock_apply.side_effect = Exception("Test exception")
        with self.assertLogs(level='ERROR') as log:
            event_id = wd.inject_chaotic_event(manual_event="trade_freeze")
            self.assertIsNone(event_id)
            self.assertTrue(
                any("Error applying event effects" in message for message in log.output))
        # Engine should be disabled after exception
        self.assertFalse(wd._black_swan_enabled)


if __name__ == "__main__":
    unittest.main()
