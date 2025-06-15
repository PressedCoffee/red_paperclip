# Trading Module

## Purpose and Scope

The `trading/` module implements trade evaluation logic and simulated exchange operations for agents. It evaluates trade offers based on agent goals, values, and tags, and simulates blockchain consequences of trades.

## Key Classes and Roles

- **TradeEvaluator**: Evaluates trade offers using multidimensional criteria including alignment score, emotional resonance, symbolic alignment, and narrative potential.
- **propose_trade** (function): Proposes trades between agents in the simulated exchange.

## Usage

TradeEvaluator is used to assess trade offers and decide acceptance based on internal reasoning.

Example:

```python
from trading.trading_logic import TradeEvaluator
from agents.agent import Agent

trade_evaluator = TradeEvaluator()
agent = Agent(capsule_data)
offer = {"item_name": "itemX", "item_tags": ["value1", "tag1"]}
evaluation, accept = trade_evaluator.evaluate_trade(agent, offer)
```

## Chaos Pack Notes

Trade evaluation integrates with Chaos Pack features by simulating blockchain operations and logging trade events.

## Dependencies and Integration

- Depends on `agents` for agent data.
- Uses `memory` for recording trade history.
- Integrates with `agents.blockchain_ops` for blockchain simulation.
