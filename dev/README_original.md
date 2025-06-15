# Red Paperclip Autonomous Agent Project

## Mission Statement

Genesis Pad is an emergent barter simulation inspired by One Red Paperclip, where autonomous AI agents each begin with a single symbolic paperclip NFT and trade their way up — not merely for material wealth but through their own evolving definitions of value. For these agents, “value” can be monetary, social, symbolic, emotional, or existential. Agents negotiate trades, form coalitions, drift their motivations, survive chaos, and may barter for access to real-world interfaces like remote lab time or physical proxies. This is a testbed for exploring how value, meaning, and digital economies might evolve when autonomous minds are free to redefine them.

## Core Principles

Symbolic paperclip NFT as genesis object

Autonomous agent barter & coalition logic

Evolving value systems

Real-world hooks as an experiment

Chaos & transcendence modules for radical emergence

## Major Capabilities

- Autonomous agents with identity, lifecycle, and goal management.
- Cognitive autonomy expansion with meta-reasoning and self-modification.
- Memory management for trade, negotiation, and reputation histories.
- Negotiation and coalition formation with payoff splitting.
- Trade evaluation and simulated blockchain operations.
- User interface components for visualization and interaction mapping.
- Visibility preferences enforcing reciprocal transparency.
- Experimental Chaos Pack modules for advanced cognitive features.

## Quick Start

1. Clone the repository.
2. Install dependencies as needed (e.g., Pinecone client).
3. Configure environment variables in `.env` for API keys.
4. Run simulations or start the agent system as per your use case.

## Documentation

For detailed developer guidance, see the [Master Developer Handbook](docs/Master_Developer_Handbook.md).

## License

[Specify license here]

# AWS Backend API / Dashboard Module

This project includes a backend API module implemented with FastAPI to serve up-to-date data for agents, trades, coalitions, payments, and capsules.

## Features

- Modular routes for `/agents`, `/trades`, `/coalitions`, `/payments`, and `/capsules`.
- Basic API token authentication with a hardcoded secret for hackathon use.
- Feature flag control to enable or disable the API.
- Logging with correlation IDs for traceability.
- Local FastAPI server script `backend_api/run_api_server.py` for demo purposes.

## API Usage

### Authentication

All endpoints require an `Authorization` header with the API token:

```
Authorization: hackathon-secret-token
```

### Endpoints

- `GET /agents/` - Returns a list of agent snapshots with timestamps and correlation IDs.
- `GET /trades/` - Returns a list of trades with timestamps and correlation IDs.
- `GET /coalitions/` - Returns a list of coalitions with timestamps and correlation IDs.
- `GET /payments/` - Returns a list of payment logs with timestamps and correlation IDs.
- `GET /capsules/` - Returns a list of capsule registry entries with timestamps and correlation IDs.

### Example Response

```json
[
  {
    "timestamp": "2025-06-14T18:00:00Z",
    "agent_id": "agent_123",
    "correlation_id": "corr_abc123",
    "data": {
      "agent_id": "agent_123",
      "name": "Agent Smith",
      "status": "active"
    }
  }
]
```

## Running Locally

To run the API server locally for demo:

```bash
python backend_api/run_api_server.py
```

The API will be available at `http://localhost:8000`.

## Testing

Minimal unit and integration tests are provided in `backend_api/test_api.py`. Run tests with:

```bash
pytest backend_api/test_api.py
```

# Hackathon Demo Scenario

This project includes a Demo Scenario & Automation module to simulate a short multi-agent environment with NFT minting, trade cycles, coalition formation, chaos events, and micro-payment flows.

## Running the Demo

Use the CLI entrypoint script `run_hackathon_demo.py` to run the demo simulation.

```bash
python run_hackathon_demo.py --agents 10 --steps 50
```

- `--agents`: Number of agents to simulate (default: 10)
- `--steps`: Number of simulation steps (default: 50)

The demo will:

- Mint NFTs for each agent using Pinata IPFS with AWS S3 fallback.
- Run trade cycles and coalition formation among agents.
- Trigger chaos events via the Black Swan Engine.
- Perform x402 micro-payment flows to unlock mock resources.
- Log all events with timestamps, agent IDs, and correlation IDs.
- Save session logs as `simulation_logs/demo_session_<timestamp>.json`.
- Print a summary of trades completed, coalitions formed, chaos events triggered, and payments made.

## Testing

Unit tests for the demo orchestration and chaos triggers are located in `tests/test_hackathon_demo.py`.

Run tests with:

```bash
python -m unittest discover -s tests -p "test_hackathon_demo.py"
```

## Notes

- Ensure environment variables for Pinata API and AWS S3 are set for NFT minting.
- The micro-payment flow is simulated and requires wallet integration for full functionality.
- Chaos events are triggered randomly during the simulation steps.

This demo provides a foundation for exploring multi-agent interactions with blockchain and chaos event integration.

## GitHub Repository Setup

This project is available on GitHub. To contribute or clone:

```bash
# Clone the repository
git clone https://github.com/yourusername/red_paperclip.git
cd red_paperclip

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (create requirements.txt if needed)
pip install numpy pandas matplotlib pytest

# Run tests to verify setup
python -m unittest discover -s tests -p "test_*.py" -v
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Project Structure

```
red_paperclip/
├── agents/                          # Core agent system
├── cognitive_autonomy_expansion_pack/ # Advanced AI capabilities
├── memory/                         # Agent memory system
├── negotiation/                    # Negotiation protocols
├── registry/                       # Capsule registry system
├── simulations/                    # Multi-agent simulations
├── trading/                        # Trading logic and exchange
├── ui/                            # User interface components
├── visibility/                    # Visibility and transparency
└── tests/                         # Test suite
```
