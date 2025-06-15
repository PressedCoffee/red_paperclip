from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict


class InteractionMap:
    """
    Tracks agent-to-agent interactions and models relationship links.
    """

    def __init__(self):
        self.interactions: List[Dict] = []
        self.coalition_memberships: Dict[int, List[str]] = {}
        self.snapshots: List[Dict] = []

    def record_interaction(self, agent_a: str, agent_b: str, interaction_type: str, timestamp: Optional[datetime] = None) -> None:
        """
        Record an interaction between two agents.

        :param agent_a: ID of the first agent.
        :param agent_b: ID of the second agent.
        :param interaction_type: Type of interaction (e.g., trade, query, visibility_share).
        :param timestamp: Optional timestamp; defaults to current time if None.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        interaction = {
            "agent_a": agent_a,
            "agent_b": agent_b,
            "interaction_type": interaction_type,
            "timestamp": timestamp,
        }
        self.interactions.append(interaction)

    def record_coalition_membership(self, coalition_id: int, members: List[str]) -> None:
        """
        Record the membership of a coalition at a given step.
        """
        self.coalition_memberships[coalition_id] = members

    def export_snapshot(self, step: int) -> Dict:
        """
        Export a snapshot of the interaction map including coalitions and pairwise interactions.
        """
        snapshot = {
            "step": step,
            "coalitions": self.coalition_memberships.copy(),
            "interactions": self.interactions.copy(),
        }
        self.snapshots.append(snapshot)
        return snapshot

    def export_json(self, filepath: str) -> None:
        """
        Export all snapshots to a JSON file.
        """
        import json
        with open(filepath, "w") as f:
            json.dump(self.snapshots, f, indent=2)

    def export_graphml(self, filepath: str) -> None:
        """
        Export the interaction map as a GraphML file compatible with Gephi or Cytoscape.
        Includes both pairwise interactions and coalition nodes.
        """
        import xml.etree.ElementTree as ET

        graphml = ET.Element(
            "graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
        graph = ET.SubElement(graphml, "graph", edgedefault="undirected")

        # Add nodes for agents
        agents = set()
        for interaction in self.interactions:
            agents.add(interaction["agent_a"])
            agents.add(interaction["agent_b"])
        for coalition_id, members in self.coalition_memberships.items():
            coalition_node_id = f"coalition_{coalition_id}"
            node = ET.SubElement(graph, "node", id=coalition_node_id)
            data = ET.SubElement(node, "data", key="type")
            data.text = "coalition"
            for member in members:
                agents.add(member)
        for agent in agents:
            node = ET.SubElement(graph, "node", id=agent)
            data = ET.SubElement(node, "data", key="type")
            data.text = "agent"

        # Add edges for pairwise interactions
        edge_id = 0
        for interaction in self.interactions:
            edge = ET.SubElement(
                graph, "edge", id=f"e{edge_id}", source=interaction["agent_a"], target=interaction["agent_b"])
            data = ET.SubElement(edge, "data", key="interaction_type")
            data.text = interaction["interaction_type"]
            edge_id += 1

        # Add edges from coalition nodes to members
        for coalition_id, members in self.coalition_memberships.items():
            coalition_node_id = f"coalition_{coalition_id}"
            for member in members:
                edge = ET.SubElement(
                    graph, "edge", id=f"e{edge_id}", source=coalition_node_id, target=member)
                data = ET.SubElement(edge, "data", key="interaction_type")
                data.text = "coalition_membership"
                edge_id += 1

        tree = ET.ElementTree(graphml)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    def get_interactions(self, agent_id: str, limit: int = 50) -> List[Dict]:
        """
        Retrieve recent interactions involving the specified agent.

        :param agent_id: Agent ID to filter interactions.
        :param limit: Maximum number of interactions to return.
        :return: List of interaction records.
        """
        filtered = [i for i in self.interactions if i["agent_a"]
                    == agent_id or i["agent_b"] == agent_id]
        sorted_interactions = sorted(
            filtered, key=lambda i: i["timestamp"], reverse=True)
        return sorted_interactions[:limit]

    def get_relationship_links(self) -> Dict[str, List[str]]:
        """
        Summarize relationship links between agents.

        :return: Dictionary mapping agent_id to list of connected agent_ids.
        """
        links = defaultdict(set)
        for interaction in self.interactions:
            a = interaction["agent_a"]
            b = interaction["agent_b"]
            links[a].add(b)
            links[b].add(a)
        # Convert sets to lists
        return {agent: list(neighbors) for agent, neighbors in links.items()}

    def summarize_interactions(self, agent_id: str) -> Dict:
        """
        Provide a summary of interactions for a given agent.

        :param agent_id: Agent ID to summarize.
        :return: Dictionary summarizing interaction counts by type and connected agents.
        """
        summary = {
            "interaction_counts": {},
            "connected_agents": set(),
        }
        for interaction in self.interactions:
            if interaction["agent_a"] == agent_id or interaction["agent_b"] == agent_id:
                itype = interaction["interaction_type"]
                summary["interaction_counts"][itype] = summary["interaction_counts"].get(
                    itype, 0) + 1
                other_agent = interaction["agent_b"] if interaction["agent_a"] == agent_id else interaction["agent_a"]
                summary["connected_agents"].add(other_agent)
        summary["connected_agents"] = list(summary["connected_agents"])
        return summary
