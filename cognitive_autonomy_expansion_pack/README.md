# Cognitive Autonomy Expansion Pack

## Purpose and Scope

The `cognitive_autonomy_expansion_pack/` module contains experimental extensions to agent cognition. It enhances the basic Genesis Capsule with meta-capsule drift, meta-reasoning, reality querying, self-modification requests, and game-theoretic strategy evaluation (UGTT). These modules enable agents to adapt, reason about their own cognition, and engage in complex strategic interactions.

## Key Classes and Roles

- **MetaCapsule**: Extends the Genesis Capsule with driftable parameters and a drift engine simulating memetic drift.
- **GenesisMetaReasoner**: Performs meta-reasoning on agent memory and goals to propose strategy refinements.
- **CapsuleRealityQueryInterface**: Provides querying capabilities to assess reality and simulate responses.
- **GenesisSelfModificationRequest**: Manages requests for self-modification based on meta-reasoning.
- **CapsuleUGTT**: Implements game-theoretic strategy evaluation for agent decision-making.

## Usage

These modules are typically used internally by agents to enhance their cognitive autonomy. Feature flags control experimental Chaos Pack features.

Example:

```python
from cognitive_autonomy_expansion_pack.meta_capsule_drift_engine import MetaCapsule

meta_capsule = MetaCapsule(goal="Expand knowledge", values={"curiosity": 0.8}, tags=["exploration"])
meta_capsule.drift_parameters(stress_factor=0.1)
```

## Chaos Pack Notes

This entire module is part of the Chaos Pack experimental features. Enable or disable via the `EXPERIMENTAL_FEATURES` dictionary in each module.

## Dependencies and Integration

- Depends on `memory` for agent memory access.
- Integrates with `registry` for capsule data.
- Works alongside core `agents` modules for agent identity and lifecycle.
