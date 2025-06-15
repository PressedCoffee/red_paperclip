# Red Paperclip - Multi-Agent Trading System

A sophisticated multi-agent trading and negotiation system where autonomous AI agents trade their way up from a single paperclip NFT, exploring emergent value systems and strategic decision-making.

## 🚀 Quick Start

1. **Clone and Setup**:

```bash
git clone https://github.com/PressedCoffee/red_paperclip.git
cd red_paperclip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install numpy pandas matplotlib pytest
```

2. **Run the Demo**:

```bash
python run_hackathon_demo.py
```

## 🎯 Key Features

### Multi-Agent System

- **Autonomous Agents**: Each agent has memory, goals, and strategic decision-making capabilities
- **Coalition Formation**: Agents can form alliances and negotiate group trades
- **Meta-Reasoning**: Advanced cognitive autonomy with self-modification capabilities

### Game Theory Integration

- **Universal Game Theory Toolkit (UGTT)**: Nash equilibrium computation and strategy analysis
- **Payoff Matrix Construction**: Dynamic strategy evaluation and optimization
- **Strategic Decision Making**: Agents use game theory for optimal trading decisions

### Trading & Economics

- **Simulated Exchange**: Full market simulation with order books and price discovery
- **Dynamic Value Systems**: Agents develop their own definitions of value beyond monetary worth
- **Blockchain Integration**: Wallet management and NFT trading capabilities

### Advanced AI Features

- **Badge/XP System**: Gamified progression and achievement tracking
- **Chaos Events**: Random market disruptions that test agent adaptability
- **Real-time Visualization**: Interactive dashboards and social feeds

## 🏗️ Architecture

```
red_paperclip/
├── agents/                     # Core agent system
│   ├── agent.py               # Main agent implementation
│   ├── badge_xp_system.py     # Achievement system
│   └── wallet/                # Blockchain integration
├── cognitive_autonomy_expansion_pack/  # Advanced AI
│   ├── meta_reasoning_engine.py        # Meta-cognitive reasoning
│   ├── ugtt_module.py                  # Game theory toolkit
│   └── reality_query_interface.py     # External world interaction
├── trading/                   # Market simulation
├── simulations/              # Multi-agent scenarios
└── ui/                      # Visualization components
```

## 🧪 Running Tests

```bash
# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run specific modules
python -m unittest cognitive_autonomy_expansion_pack.tests.test_ugtt_module -v
python -m unittest agents.wallet.test_wallet_manager -v
```

## 📊 Demo Scenarios

The hackathon demo showcases:

1. **Agent Initialization**: Creating agents with different goals and value systems
2. **Trading Rounds**: Autonomous negotiation and trade execution
3. **Coalition Formation**: Strategic alliance building
4. **Chaos Events**: Market disruption handling
5. **Value Evolution**: How agents redefine worth over time

## 🛠️ Technical Highlights

- **Game Theory**: Implements Nash equilibrium computation and strategic analysis
- **Multi-Agent Coordination**: Advanced negotiation protocols and coalition logic
- **Blockchain Ready**: Integration with Coinbase's AgentKit for real wallet operations
- **Extensible Architecture**: Modular design supporting new agent behaviors and market dynamics
- **Comprehensive Testing**: Full test suite with 89 files and 8,700+ lines of code

## 📈 Innovation Points

1. **Emergent Value Systems**: Agents autonomously develop non-monetary value concepts
2. **Strategic Coalition Formation**: Dynamic alliance building based on game theory
3. **Meta-Cognitive Reasoning**: Agents can reason about their own reasoning processes
4. **Chaos Adaptation**: Built-in resilience to unexpected market events
5. **Real-World Integration**: Hooks for physical world interaction and remote lab access

## 🎪 Hackathon Impact

This project demonstrates:

- **Advanced AI Coordination**: Multiple autonomous agents working and competing
- **Economic Innovation**: New models of value creation and exchange
- **Technical Sophistication**: Integration of game theory, blockchain, and AI reasoning
- **Practical Applications**: Foundation for decentralized autonomous organizations (DAOs)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

_Built for exploring how autonomous AI agents might redefine value, cooperation, and economic systems when given the freedom to evolve their own definitions of worth._
