from simulations.hackathon_demo import DemoScenarioOrchestrator
import argparse


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
