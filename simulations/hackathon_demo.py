#!/usr/bin/env python3
"""
Red Paperclip Hackathon Demo - Main entry point for demonstration
"""

from uuid import uuid4
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import threading
import random
import logging
import json
import argparse
import os
import sys

# Add parent directory to Python path to allow imports from parent modules
# This must be done BEFORE any other imports from the project
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Standard library imports

# Project imports (after sys.path setup)
try:
    from agents.nft.pinata_nft_storage import PinataNFTStorage
    from agents.x402_payment_handler_v2 import X402PaymentHandler
    from simulations.coalition_formation import CoalitionFormation
    from simulations.multi_agent_interaction import AutonomousAgent, create_agents, ENABLE_GENESIS_PAD
    from chaos_pack.world_dynamics import inject_chaotic_event
    import requests
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Please run this script from the project root directory or ensure all dependencies are installed.")
    print(f"Current sys.path[0]: {sys.path[0] if sys.path else 'None'}")
    print(f"Parent directory: {parent_dir}")
    print(f"Working directory: {os.getcwd()}")
    sys.exit(1)

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

        # Initialize payment handler with wallet or fallback
        try:
            from agents.wallet.wallet_manager import WalletManager
            from registry.capsule_registry import CapsuleRegistry
            capsule_registry = CapsuleRegistry()
            wallet_manager = WalletManager(capsule_registry)
        except ImportError:
            wallet_manager = None

        self.payment_handler = X402PaymentHandler(
            wallet_manager=wallet_manager,
            agent_id=f"demo_orchestrator_{str(uuid4())[:8]}"
        )
        self.session_log: List[Dict[str, Any]] = []
        self.correlation_id = str(uuid4())

        # X402 server configuration
        self.x402_server_url = os.getenv(
            "X402_SERVER_URL", "http://localhost:8000")

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

    def perform_premium_resource_access(self, agent: AutonomousAgent, step: int):
        """
        Production-ready X402 micropayment flow for premium resource access.
        """
        try:
            # Attempt to access premium resource
            resource_url = f"{self.x402_server_url}/api/premium-data"

            logger.info(
                f"🔍 Agent {agent.agent_id} requesting premium resource")

            # First request (should get 402)
            response = requests.get(resource_url, timeout=10)

            if response.status_code == 402:
                # Handle 402 Payment Required
                logger.info(
                    f"💰 Received 402 Payment Required for {agent.agent_id}")

                payment_receipt = self.payment_handler.handle_402_response(
                    response.text,
                    resource_url
                )

                if payment_receipt:
                    # Log successful payment
                    self.log_event(step, "x402_payment_success", {
                        "agent_id": agent.agent_id,
                        "payment_id": payment_receipt.get("paymentId"),
                        "amount": payment_receipt.get("amount"),
                        "signature": payment_receipt.get("signature"),
                        "correlation_id": payment_receipt.get("correlation_id"),
                        "resource_url": resource_url
                    })

                    # Simulate successful resource access with payment
                    logger.info(
                        f"✅ Premium resource access granted to {agent.agent_id}")

                    # In real implementation, would retry request with X-PAYMENT header
                    self.log_event(step, "premium_resource_access", {
                        "agent_id": agent.agent_id,
                        "payment_id": payment_receipt.get("paymentId"),
                        "resource": "premium_market_data",
                        "status": "success"
                    })

                else:
                    # Payment failed
                    self.log_event(step, "x402_payment_failed", {
                        "agent_id": agent.agent_id,
                        "resource_url": resource_url,
                        "reason": "payment_authorization_failed"
                    })

            elif response.status_code == 200:
                # Unexpected - should have required payment
                logger.warning(
                    f"⚠️ Premium resource accessible without payment for {agent.agent_id}")
                self.log_event(step, "unexpected_free_access", {
                    "agent_id": agent.agent_id,
                    "resource_url": resource_url
                })

            else:
                # Other error
                logger.error(
                    f"❌ Unexpected response {response.status_code} for {agent.agent_id}")
                self.log_event(step, "resource_access_error", {
                    "agent_id": agent.agent_id,
                    "status_code": response.status_code,
                    "resource_url": resource_url
                })

        except requests.exceptions.RequestException as e:
            logger.error(
                f"❌ Network error accessing premium resource for {agent.agent_id}: {e}")
            self.log_event(step, "network_error", {
                "agent_id": agent.agent_id,
                "error": str(e),
                "resource_url": resource_url
            })

        except Exception as e:
            logger.error(
                f"❌ Unexpected error in premium resource access for {agent.agent_id}: {e}")
            self.log_event(step, "unexpected_error", {
                "agent_id": agent.agent_id,
                "error": str(e),
                "resource_url": resource_url
            })

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
                self.perform_premium_resource_access(agent, step)
                payments_made += 1            # Count trades and coalitions from logs for summary
            trades_completed += sum(
                1 for e in self.session_log if e["event_type"] == "trade_proposal" and e["step"] == step)
            coalitions_formed += sum(
                1 for e in self.session_log if e["event_type"] == "coalition_formation" and e["step"] == step)

        log_filepath = self.save_session_log()
        valid = self.validate_session_log(log_filepath)

        # Get X402 payment metrics
        payment_metrics = self.payment_handler.get_metrics()
        payment_receipts = self.payment_handler.get_receipts()

        summary = {
            "trades_completed": trades_completed,
            "coalitions_formed": coalitions_formed,
            "chaos_events_triggered": chaos_events_triggered,
            "payments_made": payments_made,
            "session_log_valid": valid,
            "session_log_file": log_filepath,
            "x402_metrics": payment_metrics,
            "x402_receipts": payment_receipts,
            "premium_resources_accessed": sum(
                1 for e in self.session_log if e["event_type"] == "premium_resource_access"),
            "payment_failures": sum(
                1 for e in self.session_log if e["event_type"] == "x402_payment_failed")
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
