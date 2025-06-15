# Registry Module

## Purpose and Scope

The `registry/` module manages Genesis Capsules, which represent the core data structures for agents. It provides functionality to create, retrieve, and list capsules, serving as a centralized registry for agent metadata.

## Key Classes and Roles

- **Capsule**: Represents a Genesis Capsule with structured data including goals, values, tags, wallet address, and public snippets.
- **CapsuleRegistry**: Manages storage and retrieval of capsules, allowing creation and lookup by capsule ID.

## Usage

CapsuleRegistry is used to create new capsules from data dictionaries and retrieve capsules by their unique IDs.

Example:

```python
from registry.capsule_registry import CapsuleRegistry

registry = CapsuleRegistry()
capsule_data = {
    "agent_id": "agent123",
    "goal": "Expand influence",
    "values": {"trust": 0.8},
    "tags": ["leader", "strategist"]
}
capsule = registry.create_capsule(capsule_data)
retrieved = registry.get_capsule_by_id(capsule.capsule_id)
```

## Chaos Pack Notes

This module is foundational and used by Chaos Pack modules for managing capsule data.

## Dependencies and Integration

- Used by `agents` for agent identity and lifecycle.
- Integrated with `cognitive_autonomy_expansion_pack` for meta-capsule extensions.
