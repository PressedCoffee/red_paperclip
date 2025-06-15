import argparse
import json
import logging
import os
import random
import threading
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4

from agents.nft.pinata_nft_storage import PinataNFTStorage
from agents.x402_payment_handler import X402PaymentHandler
from simulations.coalition_formation import CoalitionFormation
from simulations.multi_agent_interaction import AutonomousAgent, create_agents
from world_dynamics import inject_chaotic_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HackathonDemo")

LOG_DIR = "simulation_logs"
SESSION_LOG_PREFIX = "demo_session_"


class DemoScenarioOrchestrator:
    def __init__(self, num_agents: int = 10, steps: int = 50):
        self.num_agents = num_agents
        self.steps = steps
        self.agents: List[AutonomousAgent] = []
        self.coalition_manager: Optional[CoalitionFormation] = None
        self.pinata_storage = PinataNFTStorage()
        self.payment_handler = X402PaymentHandler(
            wallet_manager=None)  # WalletManager integration TBD
        self.session_log: List[Dict[str, Any]] = []
        self.correlation_id = str(uuid4())

        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

    def mint_nft_for_agent(self, agent: AutonomousAgent) -> Optional[str]:
        metadata = {
            "agent_id": agent.agent_id,
            "goal": agent.goal,
            "tags": agent.tags,
            "timestamp": datetime.utcnow().isoformat(),
        }
        ipfs_hash_or_s3_key = self.pinata_storage.store_metadata(metadata)
        if ipfs_hash_or_s3_key:
            logger.info(
                f"NFT minted for {agent.agent_id}: {ipfs_hash_or_s3_key}")
        else:
            logger.error(f"Failed to mint NFT for {agent.agent_id}")
        return ipfs_hash_or_s3_key

    def run_trade_cycle(self, step: int):
        for agent in self.agents:
            # Each agent runs its step logic
            agent.run_step(step)

        # Coalition proposals
        for agent in self.agents:
            if random.random() < 0.15:  # Coalition proposal probability
                candidate_agents = random.sample(
                    [a.agent_id for a in self.agents if a.agent_id != agent.agent_id],
                    k=min(2, len(self.agents) - 1)
                )
                proposal = self.coalition_manager.propose_coalition(
                    agent.agent_id, candidate_agents)
                if proposal:
                    accepted = self.coalition_manager.accept_coalition(
                        proposal)
                    if accepted:
                        badge_xp_systems = {
                            a.agent_id: a.badge_xp_system for a in self.agents}
                        self.coalition_manager.update_xp_and_badges(
                            proposal, badge_xp_systems)
                        self.log_event(step, "coalition_formation", {
                            "coalition_id": proposal.get("coalition_id"),
                            "members": proposal.get("members"),
                            "pooled_payoff": proposal.get("pooled_payoff"),
                            "payoff_shares": proposal.get("payoff_shares"),
                            "accepted": True,
                        })

        # Trade proposals
        for agent in self.agents:
            if random.random() < 0.3:  # Trade proposal probability
                other_agent = random.choice(
                    [a for a in self.agents if a.agent_id != agent.agent_id])
                trade_log = agent.propose_trade(other_agent, step)
                coalition_id = self.coalition_manager.get_coalition_id(
                    agent.agent_id)
                if coalition_id is not None:
                    trade_log["coalition_id"] = coalition_id
                self.log_event(step, "trade_proposal", trade_log)

    def trigger_chaos_event(self, step: int):
        event_id = inject_chaotic_event()
        self.log_event(step, "chaos_event", {"event_id": event_id})
        logger.info(f"Chaos event triggered: {event_id}")

    def perform_micro_payment(self, agent: AutonomousAgent, step: int):
        # Mock payment flow: simulate parsing 402 response and signing payment
        mock_402_response = json.dumps({
            "payment_params": {
                "domain": {"name": "DemoDomain", "version": "1"},
                "types": {"Payment": [{"name": "amount", "type": "uint256"}]},
                "primaryType": "Payment",
                "message": {"amount": 1}
            }
        })
        payment_params = self.payment_handler.parse_402_response(
            mock_402_response)
        if payment_params:
            signature = self.payment_handler.sign_payment_authorization(
                payment_params)
            if signature:
                header = self.payment_handler.construct_payment_header(
                    signature, payment_params)
                self.log_event(step, "micro_payment", {
                    "agent_id": agent.agent_id,
                    "signature": signature,
                    "header": header,
                })
                logger.info(
                    f"Micro-payment performed for {agent.agent_id} at step {step}")
            else:
                logger.error(
                    f"Failed to sign payment authorization for {agent.agent_id}")
        else:
            logger.error(
                f"Failed to parse 402 payment response for {agent.agent_id}")

    def log_event(self, step: int, event_type: str, details: Dict[str, Any]):
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "step": step,
            "event_type": event_type,
            "correlation_id": self.correlation_id,
            "details": details,
        }
        self.session_log.append(event)

    def save_session_log(self):
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        filename = f"{SESSION_LOG_PREFIX}{timestamp}.json"
        filepath = os.path.join(LOG_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(self.session_log, f, indent=2)
        logger.info(f"Session log saved to {filepath}")
        return filepath

    def validate_session_log(self, filepath: str) -> bool:
        # Basic validation: check file exists and JSON loads
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            # Check correlation_id consistency
            for event in data:
                if event.get("correlation_id") != self.correlation_id:
                    logger.error("Correlation ID mismatch in session log")
                    return False
            logger.info("Session log validation passed")
            return True
        except Exception as e:
            logger.error(f"Session log validation failed: {e}")
            return False

    def run(self):
        logger.info(
            f"Starting demo with {self.num_agents} agents for {self.steps} steps")
        self.agents = create_agents(self.num_agents)
        self.coalition_manager = CoalitionFormation(self.agents)

        # Mint NFTs for all agents
        for agent in self.agents:
            ipfs_hash = self.mint_nft_for_agent(agent)
            self.log_event(0, "nft_minting", {
                           "agent_id": agent.agent_id, "ipfs_hash": ipfs_hash})

        trades_completed = 0
        coalitions_formed = 0
        chaos_events_triggered = 0
        payments_made = 0

        for step in range(1, self.steps + 1):
            self.run_trade_cycle(step)

            # Randomly trigger chaos event with low probability
            if random.random() < 0.1:
                self.trigger_chaos_event(step)
                chaos_events_triggered += 1

            # Randomly perform micro-payment for a random agent
            if random.random() < 0.2:
                agent = random.choice(self.agents)
                self.perform_micro_payment(agent, step)
                payments_made += 1

            # Count trades and coalitions from logs for summary
            trades_completed += sum(
                1 for e in self.session_log if e["event_type"] == "trade_proposal" and e["step"] == step)
            coalitions_formed += sum(
                1 for e in self.session_log if e["event_type"] == "coalition_formation" and e["step"] == step)

        log_filepath = self.save_session_log()
        valid = self.validate_session_log(log_filepath)

        summary = {
            "trades_completed": trades_completed,
            "coalitions_formed": coalitions_formed,
            "chaos_events_triggered": chaos_events_triggered,
            "payments_made": payments_made,
            "session_log_valid": valid,
            "session_log_file": log_filepath,
        }

        logger.info("Demo run complete. Summary:")
        for k, v in summary.items():
            logger.info(f"  {k}: {v}")

        return summary


def main():
    parser = argparse.ArgumentParser(description="Run Hackathon Demo Scenario")
    parser.add_argument("--agents", type=int, default=10,
                        help="Number of agents (default 10)")
    parser.add_argument("--steps", type=int, default=50,
                        help="Number of simulation steps (default 50)")
    args = parser.parse_args()

    orchestrator = DemoScenarioOrchestrator(
        num_agents=args.agents, steps=args.steps)
    summary = orchestrator.run()

    print("\nDemo Summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
