import pytest
from simulations.genesis_pad_session import GenesisPadSession


def test_run_session_completes_without_user_input():
    session = GenesisPadSession()
    journal, capsule = session.run_session()
    # The journal should have entries for all prompts
    total_prompts = sum(len(prompts) for prompts in session.PROMPTS.values())
    assert len(journal) == total_prompts
    # Each journal entry should have prompt, response, timestamp, and llm_metadata
    for entry in journal:
        assert "prompt" in entry
        assert "response" in entry
        assert "timestamp" in entry
        assert "llm_metadata" in entry


def test_genesis_capsule_is_complete_and_valid():
    session = GenesisPadSession()
    _, capsule = session.run_session()
    # Capsule should be a dict with expected keys
    expected_keys = {"goal", "values", "tags",
                     "motivation_score", "public_snippet"}
    assert isinstance(capsule, dict)
    assert expected_keys.issubset(capsule.keys())
    # motivation_score should be int between 0 and 10
    assert isinstance(capsule["motivation_score"], int)
    assert 0 <= capsule["motivation_score"] <= 10
    # values and tags should be lists
    assert isinstance(capsule["values"], list)
    assert isinstance(capsule["tags"], list)
    # goal and public_snippet should be strings
    assert isinstance(capsule["goal"], str)
    assert isinstance(capsule["public_snippet"], str)
