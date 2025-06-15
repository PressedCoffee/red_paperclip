import unittest
import os
import json
from simulations.hackathon_demo import DemoScenarioOrchestrator
from chaos_pack.world_dynamics import inject_chaotic_event


class TestHackathonDemoOrchestrator(unittest.TestCase):
    def test_run_orchestration_creates_log_and_summary(self):
        orchestrator = DemoScenarioOrchestrator(num_agents=3, steps=5)
        summary = orchestrator.run()

        # Check summary keys
        self.assertIn("trades_completed", summary)
        self.assertIn("coalitions_formed", summary)
        self.assertIn("chaos_events_triggered", summary)
        self.assertIn("payments_made", summary)
        self.assertIn("session_log_valid", summary)
        self.assertIn("session_log_file", summary)

        # Check session log file exists
        self.assertTrue(os.path.exists(summary["session_log_file"]))

        # Check session log file content is valid JSON
        with open(summary["session_log_file"], "r") as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)

    def test_inject_chaotic_event_returns_event_id(self):
        event_id = inject_chaotic_event()
        self.assertIsInstance(event_id, str)
        self.assertTrue(len(event_id) > 0)


if __name__ == "__main__":
    unittest.main()
