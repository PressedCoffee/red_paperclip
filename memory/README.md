# Memory Module

## Purpose and Scope

The `memory/` module manages agent memory, including trade records, negotiation history, and reputation tracking. It interfaces with external memory storage systems like Pinecone and maintains historical data to support agent reasoning and decision-making.

## Key Classes and Roles

- **TradeRecord**: Represents individual trade records with details such as trade item, outcome, symbolic tags, and explanations.
- **AgentMemory**: Maintains trade histories, negotiation outcomes, reputation scores, and reasoning patterns for agents.

## Usage

AgentMemory instances track and store trade and negotiation data, update reputations, and maintain reasoning histories.

Example:

```python
from memory.agent_memory import AgentMemory, TradeRecord

agent_memory = AgentMemory(agent_id="agent123")
trade_record = TradeRecord("itemX", "success", "trade_tag", "Successful trade of itemX")
agent_memory.add_trade_record("agent123", trade_record)
reputation = agent_memory.get_reputation()
```

## Chaos Pack Notes

This module supports logging of advanced cognitive events such as capsule drift when integrated with Chaos Pack features.

## Dependencies and Integration

- Integrates with `agents` for agent identity.
- Supports `negotiation` and `trading` modules by storing interaction histories.
- Works with `cognitive_autonomy_expansion_pack` for meta-reasoning data storage.
