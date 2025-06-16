#!/usr/bin/env python3
"""
Red Paperclip Hackathon Demo Runner
Orchestrates a complete demonstration of the autonomous agent trading system
"""

import sys
import os
import argparse
import datetime
import json
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_environment():
    """Ensure environment is properly configured."""
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = ['OPENAI_API_KEY',
                     'CDP_API_KEY_ID', 'CDP_API_KEY_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False

    print("✅ Environment configured successfully")
    return True


def run_agent_simulation(num_agents: int = 5, num_steps: int = 20,
                         enable_verbal_exchange: bool = True,
                         enable_chaos: bool = False) -> str:
    """Run the main agent simulation and return session log path."""

    print(f"🚀 Starting Red Paperclip Hackathon Demo")
    print(f"   Agents: {num_agents}")
    print(f"   Steps: {num_steps}")
    print(
        f"   Verbal Exchange: {'✅ Enabled' if enable_verbal_exchange else '❌ Disabled'}")
    print(f"   Chaos Events: {'✅ Enabled' if enable_chaos else '❌ Disabled'}")
    print("=" * 60)

    # Import simulation modules
    from simulations.integrated_simulation import run_integrated_simulation
    from memory.agent_memory import AgentMemory
    from registry.capsule_registry import CapsuleRegistry
    from agents.badge_xp_system import BadgeXPSystem

    # Initialize core systems
    capsule_registry = CapsuleRegistry()
    agent_memory = AgentMemory()
    badge_xp_system = BadgeXPSystem(capsule_registry)

    # Create session timestamp
    session_timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    session_log_path = f"simulation_logs/demo_session_{session_timestamp}.json"

    try:
        # Run the integrated simulation
        session_data = run_integrated_simulation(
            num_agents=num_agents,
            num_steps=num_steps,
            enable_verbal_exchange=enable_verbal_exchange,
            enable_chaos_events=enable_chaos,
            session_log_path=session_log_path
        )

        print(f"✅ Simulation completed successfully!")
        print(f"📁 Session log saved: {session_log_path}")

        return session_log_path

    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return ""


def display_session_summary(session_log_path: str):
    """Display a quick summary of the simulation results."""
    if not session_log_path or not os.path.exists(session_log_path):
        return

    try:
        with open(session_log_path, 'r') as f:
            events = json.load(f)

        # Analyze events
        trades = sum(1 for e in events if e.get('event_type') ==
                     'trade_proposal' and e.get('details', {}).get('accepted', False))
        coalitions = sum(1 for e in events if e.get(
            'event_type') == 'coalition_formation')
        chaos_events = sum(1 for e in events if e.get(
            'event_type') == 'chaos_event')
        x402_payments = sum(1 for e in events if e.get(
            'event_type') == 'x402_payment')
        nft_mints = sum(1 for e in events if e.get(
            'event_type') == 'nft_minting')

        print("\n" + "=" * 60)
        print("📊 HACKATHON DEMO RESULTS")
        print("=" * 60)
        print(f"📈 Total Events: {len(events)}")
        print(f"✅ Trades Completed: {trades}")
        print(f"🤝 Coalitions Formed: {coalitions}")
        print(f"⚡ Chaos Events: {chaos_events}")
        print(f"💸 x402 Payments: {x402_payments}")
        print(f"🎨 NFTs Minted: {nft_mints}")
        print("=" * 60)
        print("🎯 NEXT STEPS:")
        print("1. View detailed metrics: python dashboards/hackathon_dashboard.py")
        print("2. Check payment receipts in receipts/ directory")
        print("3. Review session log for full audit trail")
        print("=" * 60)

    except Exception as e:
        print(f"⚠️  Could not analyze session results: {e}")


def main():
    """Main hackathon demo entry point."""
    parser = argparse.ArgumentParser(
        description="Red Paperclip Hackathon Demo")
    parser.add_argument('--agents', type=int, default=5,
                        help='Number of agents (default: 5)')
    parser.add_argument('--steps', type=int, default=20,
                        help='Number of simulation steps (default: 20)')
    parser.add_argument('--enable_verbal_exchange', type=bool, default=True,
                        help='Enable verbal exchange layer (default: True)')
    parser.add_argument('--enable_chaos', type=bool, default=False,
                        help='Enable chaos events (default: False)')
    parser.add_argument('--skip_dashboard', action='store_true',
                        help='Skip automatic dashboard launch')

    args = parser.parse_args()

    print("📎 RED PAPERCLIP HACKATHON DEMONSTRATION")
    print("AI Agents with Autonomous Trading, Verbal Exchange & x402 Payments")
    print("=" * 70)

    # Setup environment
    if not setup_environment():
        return 1

    # Run simulation
    session_log_path = run_agent_simulation(
        num_agents=args.agents,
        num_steps=args.steps,
        enable_verbal_exchange=args.enable_verbal_exchange,
        enable_chaos=args.enable_chaos
    )

    if not session_log_path:
        print("❌ Demo failed to complete")
        return 1

    # Display summary
    display_session_summary(session_log_path)

    # Launch dashboard if requested
    if not args.skip_dashboard:
        print("\n🔄 Launching dashboard...")
        try:
            import subprocess
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                "dashboards/hackathon_dashboard.py",
                "--server.headless", "false"
            ], cwd=os.path.dirname(os.path.abspath(__file__)))
        except Exception as e:
            print(f"⚠️  Could not launch dashboard automatically: {e}")
            print("Manual launch: streamlit run dashboards/hackathon_dashboard.py")

    print("\n🎉 Hackathon demo completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
