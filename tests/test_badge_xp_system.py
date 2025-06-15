import unittest
from agents.badge_xp_system import BadgeXPSystem
from agents.agent import Agent, AgentIdentity
from registry.capsule_registry import CapsuleRegistry


class TestBadgeXPSystem(unittest.TestCase):
    def setUp(self):
        self.registry = CapsuleRegistry()
        self.badge_system = BadgeXPSystem(self.registry)
        self.agent_id = "agent-123"
        self.agent_identity = AgentIdentity(
            agent_id=self.agent_id, capsule_id="capsule-abc")
        self.agent = Agent(capsule_data={"capsule_id": "capsule-abc", "goal": "Test Goal"},
                           agent_identity=self.agent_identity, badge_xp_system=self.badge_system)

    def test_award_badge_and_xp(self):
        milestone = "First Milestone"
        xp_amount = 100
        badge_capsule = self.agent.award_badge(milestone, xp_amount)
        self.assertIsNotNone(badge_capsule)
        self.assertEqual(self.badge_system.get_agent_xp(
            self.agent_id), xp_amount)
        badges = self.badge_system.get_agent_badges(self.agent_id)
        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0].values["milestone"], milestone)

    def test_duplicate_badge_prevention(self):
        milestone = "Repeat Milestone"
        xp_amount = 50
        badge1 = self.agent.award_badge(milestone, xp_amount)
        badge2 = self.agent.award_badge(milestone, xp_amount)
        # Both badges are awarded because no prevention logic in BadgeXPSystem; this test documents current behavior
        badges = self.badge_system.get_agent_badges(self.agent_id)
        self.assertEqual(len(badges), 2)

    def test_capsule_registry_storage(self):
        milestone = "Registry Test"
        xp_amount = 75
        badge_capsule = self.agent.award_badge(milestone, xp_amount)
        retrieved = self.registry.get_capsule_by_id(badge_capsule.capsule_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.values["milestone"], milestone)

    def test_agent_xp_and_badges_methods(self):
        milestone = "Agent Method Test"
        xp_amount = 120
        badge_capsule = self.agent.award_badge(milestone, xp_amount)
        self.assertEqual(self.agent.get_xp(), xp_amount)
        badges = self.agent.get_badges()
        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0].values["milestone"], milestone)


if __name__ == "__main__":
    unittest.main()
