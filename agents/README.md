# Agents Module

## Purpose and Scope

The `agents/` module provides the core scaffolding for autonomous agents in the system. It manages agent identity, lifecycle, badge and XP systems, blockchain operations, and goal reevaluation. Agents are instantiated with Genesis Capsule data and interact with other modules to perform their functions.

## Key Classes and Roles

- **AgentIdentity**: Represents the identity of an agent linked to a Genesis Capsule, including wallet address, NFT assignment, personality traits, and placeholders for future integrations.
- **Agent**: Core agent class exposing capsule attributes and providing methods for broadcasting, badge awarding, and XP management.
- **AgentLifecycleManager**: Manages the lifecycle and modifications of agents.
- **BadgeXPSystem**: Manages badges and experience points (XP) for agents.
- **BlockchainOpsSimulator**: Simulates blockchain operations related to agent trades.
- **GoalReevaluationModule**: Periodically reevaluates agent goals based on capsule data and memory.

## Usage

Agents are typically instantiated with capsule data and optionally linked to an AgentIdentity and BadgeXPSystem. They can broadcast messages respecting visibility preferences, award badges, and track XP.

Example:

```python
from agents.agent import Agent, AgentIdentity
from agents.badge_xp_system import BadgeXPSystem

capsule_data = {...}  # Genesis Capsule data
agent_identity = AgentIdentity(agent_id="agent123", capsule_id="capsule123")
badge_system = BadgeXPSystem(capsule_registry)

agent = Agent(capsule_data, agent_identity, badge_system)
agent.broadcast_to_public("Trade completed", visibility_prefs)
agent.award_badge("First Trade", 10)
```

## Chaos Pack Notes

This module integrates with Chaos Pack features via badge and XP systems. Enabling or disabling Chaos Pack features may affect badge awarding and goal reevaluation behaviors.

## Dependencies and Integration

- Depends on `registry` for capsule data.
- Integrates with `memory` for agent memory and trade history.
- Works with `visibility` for managing broadcast permissions.
- Interacts with `trading` and `negotiation` modules for trade and coalition activities.
