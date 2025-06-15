import random
import logging
from uuid import uuid4

# Feature flags dictionary (should be imported or defined elsewhere in the real system)
EXPERIMENTAL_FEATURES = {
    "chaos_pack": True  # This should be controlled externally
}

# Safety circuit breaker flag
_black_swan_enabled = True


def disable_black_swan_engine():
    global _black_swan_enabled
    _black_swan_enabled = False
    logging.warning(
        "Black Swan Engine disabled due to safety circuit breaker.")


def enable_black_swan_engine():
    global _black_swan_enabled
    _black_swan_enabled = True
    logging.info("Black Swan Engine enabled.")


def determine_affected_agents(event):
    # Placeholder: In real implementation, determine agents affected by the event
    # For demonstration, return a sample list of agent IDs or names
    if event == "trade_freeze":
        return ["agent_1", "agent_3", "agent_7"]
    elif event == "reputational_collapse":
        return ["agent_2", "agent_5"]
    elif event == "false_memory_insertion":
        return ["agent_4", "agent_6", "agent_8"]
    elif event == "symbolic_agent_death":
        return ["agent_9"]
    else:
        return []


def calculate_detection_difficulty(event):
    # Placeholder: Assign detection difficulty scores based on event type
    difficulty_map = {
        "trade_freeze": 7.5,
        "reputational_collapse": 8.0,
        "false_memory_insertion": 9.0,
        "symbolic_agent_death": 6.5
    }
    return difficulty_map.get(event, 5.0)


def apply_event_effects(event, affected_agents):
    # Placeholder: Apply the effects of the event to the affected agents
    # This function should modify the simulation state accordingly
    logging.info(
        f"Applying effects of event '{event}' to agents: {affected_agents}")


def inject_chaotic_event(manual_event=None):
    """
    Inject a chaotic event into the simulation.

    Parameters:
        manual_event (str or None): If provided, manually trigger this event type.
                                    Otherwise, select an event stochastically.

    Returns:
        str: Unique chaos_event_id for the injected event, or None if disabled.
    """
    if not EXPERIMENTAL_FEATURES.get("chaos_pack", False):
        logging.info("Chaos Pack feature disabled; no event injected.")
        return None

    if not _black_swan_enabled:
        logging.warning(
            "Black Swan Engine is disabled by safety circuit breaker; no event injected.")
        return None

    event_types = [
        "trade_freeze",
        "reputational_collapse",
        "false_memory_insertion",
        "symbolic_agent_death"
    ]

    event_id = str(uuid4())

    if manual_event:
        if manual_event not in event_types:
            logging.error(f"Invalid manual_event '{manual_event}' specified.")
            return None
        event = manual_event
        logging.info(f"Manually triggering chaotic event: {event}")
    else:
        event = random.choice(event_types)
        logging.info(f"Stochastically triggered chaotic event: {event}")

    affected_agents = determine_affected_agents(event)
    detection_difficulty_score = calculate_detection_difficulty(event)

    try:
        apply_event_effects(event, affected_agents)
    except Exception as e:
        logging.error(f"Error applying event effects: {e}")
        disable_black_swan_engine()
        return None

    logging.info(
        f"ChaosEvent {event_id}: {event} affecting {affected_agents} with detection difficulty {detection_difficulty_score}")

    return event_id
