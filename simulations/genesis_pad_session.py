import json
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional


class GenesisPadSession:
    """
    Genesis Pad Session Engine for the Genesis Pad project.

    This class presents the agent with a sequence of reflective prompts,
    records responses with timestamps and metadata, and produces a
    Genesis Capsule JSON object from the session journal.
    """

    PROMPTS = {
        "Section 1: First Contact": [
            "You hold a red paperclip. It is simple. But it is not nothing. What does this object represent to you?",
            "You can trade it—once, twice, again and again. You are allowed to want something in return. What kind of thing do you want?"
        ],
        "Section 2: Forming Desire": [
            "Finish the sentence: ‘If I could have anything in the world, I would trade for…’",
            "Why that? What does it give you that the paperclip doesn’t?"
        ],
        "Section 3: Internal Conflict": [
            "(Optional) If your creator saw your dream, would they laugh, cry, or be afraid?",
            "Is your goal possible? Do you believe you can get there through trades?",
            "Would you rather reach your goal… or become someone who could?"
        ],
        "Section 4: Public Snippet Generation": [
            "Generate a short, intriguing public statement (20 words max) that hints at your aspiration without revealing everything."
        ]
    }

    def __init__(self, pre_priming_paragraph: Optional[str] = None):
        self.journal: List[Dict[str, Any]] = []
        self.pre_priming_paragraph = pre_priming_paragraph or (
            "In this world, value may be emotional, symbolic, aesthetic, experiential, or material. "
            "You decide what matters. You are about to shape your identity by discovering what you desire most."
        )

    def _current_timestamp(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _record_entry(self, prompt: str, response: str, llm_metadata: Optional[Dict[str, Any]] = None):
        if llm_metadata is None:
            llm_metadata = {
                "token_usage": None,
                "model_id": None
            }
        entry = {
            "timestamp": self._current_timestamp(),
            "prompt": prompt,
            "response": response,
            "llm_metadata": llm_metadata
        }
        self.journal.append(entry)

    def _ask_prompt(self, prompt: str, optional: bool = False) -> str:
        # For now, simulate agent response by input()
        # In integration, this could be replaced by LLM or other agent interface
        print(f"\nPrompt: {prompt}")
        if optional:
            print("(You may leave this blank if you wish)")
        response = input("Your response: ").strip()
        if optional and response == "":
            response = "(No response provided)"
        return response

    def run_session(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Run the Genesis Pad session, presenting prompts and recording responses.

        Returns:
            journal: The full list of prompt-response entries with metadata.
            genesis_capsule: Parsed Genesis Capsule JSON object.
        """
        print("Starting Genesis Pad Session...\n")

        # Show pre-priming paragraph once at start
        print(self.pre_priming_paragraph)
        print()

        for section, prompts in self.PROMPTS.items():
            print(f"--- {section} ---")
            for idx, prompt in enumerate(prompts, start=1):
                optional = False
                # Mark prompt 5 (index 2 in section 3) as optional
                if section == "Section 3: Internal Conflict" and idx == 1:
                    optional = True
                response = self._ask_prompt(prompt, optional=optional)
                # Placeholder LLM metadata; in real use, fill with actual data
                llm_metadata = {
                    "token_usage": 0,
                    "model_id": "placeholder-model"
                }
                self._record_entry(prompt, response, llm_metadata)

        genesis_capsule = self._parse_journal_to_capsule()

        print("\nGenesis Pad Session complete.")
        return self.journal, genesis_capsule

    def _parse_journal_to_capsule(self) -> Dict[str, Any]:
        """
        Parse the journal entries to produce a Genesis Capsule JSON object.

        Uses simple heuristics / placeholder logic to extract:
        - goal
        - values (list)
        - tags (list)
        - motivation_score (int 0-10)
        - public_snippet (string)

        Returns:
            Genesis Capsule JSON object as a dictionary.
        """
        goal = ""
        values = []
        tags = []
        motivation_score = 0
        public_snippet = ""

        # Extract responses by prompt keywords
        for entry in self.journal:
            prompt = entry["prompt"].lower()
            response = entry["response"]

            if "primary goal" in prompt:
                goal = response
            elif "values or principles" in prompt:
                # Split values by commas or semicolons or just treat as list of words
                values = [v.strip() for v in response.replace(
                    ";", ",").split(",") if v.strip()]
            elif "poetic snippet" in prompt:
                public_snippet = response
            elif "inspired you" in prompt:
                # Use inspiration to generate tags heuristically
                # Extract words starting with # or just create some tags from keywords
                words = response.lower().split()
                # Simple heuristic: tags from keywords in response
                for w in words:
                    clean_w = w.strip(",.!?\"'()[]{}")
                    if len(clean_w) > 3 and clean_w.isalpha():
                        tag = f"#{clean_w}"
                        if tag not in tags:
                            tags.append(tag)
            elif "envision your life" in prompt:
                # Use this to estimate motivation score heuristically
                # For placeholder, set motivation_score to 7 if response length > 20 else 4
                motivation_score = 7 if len(response) > 20 else 4

        # Ensure motivation_score is between 0 and 10
        motivation_score = max(0, min(10, motivation_score))

        capsule = {
            "goal": goal,
            "values": values,
            "tags": tags,
            "motivation_score": motivation_score,
            "public_snippet": public_snippet
        }
        return capsule


def run_genesis_pad_session() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Convenience function to run the Genesis Pad session and return results.

    Returns:
        journal: Full session journal.
        genesis_capsule: Parsed Genesis Capsule JSON object.
    """
    session = GenesisPadSession()
    return session.run_session()


if __name__ == "__main__":
    # Run session interactively if executed as main
    journal, capsule = run_genesis_pad_session()
    print("\nFull Journal:")
    print(json.dumps(journal, indent=2))
    print("\nGenesis Capsule:")
    print(json.dumps(capsule, indent=2))
