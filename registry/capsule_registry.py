import json
import uuid
from typing import List, Optional, Dict, Any


class Capsule:
    """
    Represents a Genesis Capsule with structured data.
    """

    def __init__(
        self,
        goal: str,
        values: Dict[str, Any],
        tags: List[str],
        wallet_address: Optional[str] = None,
        public_snippet: Optional[str] = None,
        capsule_id: Optional[str] = None,
    ):
        """
        Initialize a Capsule instance.

        :param goal: The goal of the capsule.
        :param values: A dictionary of values associated with the capsule.
        :param tags: A list of tags for categorization.
        :param wallet_address: Placeholder for wallet address (default None).
        :param public_snippet: Optional public snippet text.
        :param capsule_id: Unique identifier for the capsule. If None, a new UUID is generated.
        """
        self.capsule_id = capsule_id or str(uuid.uuid4())
        self.goal = goal
        self.values = values
        self.tags = tags
        self.wallet_address = wallet_address
        self.public_snippet = public_snippet

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the capsule to a dictionary.

        :return: Dictionary representation of the capsule.
        """
        return {
            "capsule_id": self.capsule_id,
            "goal": self.goal,
            "values": self.values,
            "tags": self.tags,
            "wallet_address": self.wallet_address,
            "public_snippet": self.public_snippet,
        }

    def to_json(self) -> str:
        """
        Serialize the capsule to a JSON string.

        :return: JSON string representation of the capsule.
        """
        return json.dumps(self.to_dict(), indent=2)


class CapsuleRegistry:
    """
    Registry for managing Genesis Capsules.
    """

    def __init__(self):
        """
        Initialize the CapsuleRegistry with an empty storage.
        """
        self._capsules: Dict[str, Capsule] = {}

    def create_capsule(self, capsule_data: Dict[str, Any]) -> Capsule:
        """
        Create a new capsule from the provided capsule data dictionary.

        :param capsule_data: A dictionary containing capsule data. Expected keys:
            - agent_id: The unique identifier for the capsule (usually the wallet address).
            - goal: The goal of the capsule.
            - values: A dictionary of values associated with the capsule.
            - tags: A list of tags for categorization.
        :return: The created Capsule instance.
        """
        agent_id = capsule_data["agent_id"]
        goal = capsule_data.get("goal", "")
        values = capsule_data.get("values", {})
        tags = capsule_data.get("tags", [])

        capsule = Capsule(
            goal=goal,
            values=values,
            tags=tags,
            wallet_address=agent_id,  # Assuming wallet_address is the agent_id
        )
        self._capsules[agent_id] = capsule
        return capsule

    def get_capsule_by_id(self, capsule_id: str) -> Optional[Capsule]:
        """
        Retrieve a capsule by its unique ID.

        :param capsule_id: The unique identifier of the capsule.
        :return: Capsule instance if found, else None.
        """
        return self._capsules.get(capsule_id)

    def list_capsules(self) -> List[Capsule]:
        """
        List all capsules in the registry.

        :return: List of Capsule instances.
        """
        return list(self._capsules.values())

    def add_capsule(self, capsule: Capsule):
        """
        Add a capsule to the registry.

        :param capsule: The Capsule instance to add.
        """
        self._capsules[capsule.capsule_id] = capsule

    def get_capsule(self, capsule_id: str) -> Optional[Capsule]:
        """
        Retrieve a capsule by its ID (alias for get_capsule_by_id).

        :param capsule_id: The unique identifier of the capsule.
        :return: Capsule instance if found, else None.
        """
        return self.get_capsule_by_id(capsule_id)

    def update_capsule(self, capsule_id: str, capsule: Capsule):
        """
        Update a capsule in the registry.

        :param capsule_id: The unique identifier of the capsule.
        :param capsule: The updated Capsule instance.
        """
        self._capsules[capsule_id] = capsule
