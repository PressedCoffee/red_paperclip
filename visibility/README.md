# Visibility Module

## Purpose and Scope

The `visibility/` module manages visibility preferences for agents, implementing reciprocal transparency logic to control data sharing across various categories such as goals, badges, emotional arcs, public snippets, social links, and trade history.

## Key Classes and Roles

- **VisibilityPreferences**: Manages and enforces visibility preferences for an agent, ensuring reciprocal sharing rules are respected.

## Usage

VisibilityPreferences instances are used to update and check visibility settings between agents.

Example:

```python
from visibility.visibility_preferences import VisibilityPreferences

agent_prefs = VisibilityPreferences(agent_id="agent123")
agent_prefs.update_preference("show_goal", True)

viewer_prefs = VisibilityPreferences(agent_id="agent456")
viewer_prefs.update_preference("show_goal", True)

can_view = agent_prefs.can_view(viewer_prefs, "show_goal")
print(f"Viewer can see goal: {can_view}")
```

## Chaos Pack Notes

Visibility preferences are critical for managing data sharing in Chaos Pack modules, ensuring privacy and transparency.

## Dependencies and Integration

- Integrates with `agents` for enforcing broadcast and data sharing permissions.
- Works with `ui` to control visibility of agent data in dashboards and feeds.
