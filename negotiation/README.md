# Negotiation Module

## Purpose and Scope

The `negotiation/` module facilitates payoff splitting among coalition members based on their reputations. It supports collaborative decision-making by proposing fair splits of rewards or payoffs in multi-agent coalitions.

## Key Classes and Roles

- **NegotiationModule**: Manages negotiation processes, proposing payoff splits weighted by agent reputations and logging negotiation outcomes.

## Usage

The module is initialized with a dictionary of agent memories and used to propose payoff splits among coalition members.

Example:

```python
from negotiation.negotiation_module import NegotiationModule
from memory.agent_memory import AgentMemory

agent_memories = {
    "agent1": AgentMemory("agent1"),
    "agent2": AgentMemory("agent2"),
}
negotiation = NegotiationModule(agent_memories)
payoff_split = negotiation.propose_split(100.0, ["agent1", "agent2"])
print(payoff_split)
```

## Chaos Pack Notes

This module logs negotiation outcomes which can be used by Chaos Pack cognitive features for advanced reasoning.

## Dependencies and Integration

- Depends on `memory` for agent reputation and negotiation history.
- Integrates with `simulations` and `agents` for coalition and agent management.
