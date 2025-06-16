from typing import List, Dict, Any, Optional
from memory.agent_memory import AgentMemory
from registry.capsule_registry import Capsule
from config.trade_config import get_config
import logging
import uuid
import time
import datetime

logger = logging.getLogger(__name__)


class NegotiationModule:
    def __init__(self, agent_memories: Dict[str, AgentMemory]):
        """
        Initialize with a dictionary mapping agent_id to AgentMemory.
        """
        self.agent_memories = agent_memories
        self.config = get_config()
        self.trade_history = []

    def propose_split(self, total_payoff: float, members: List[str]) -> Dict[str, float]:
        """
        Propose a payoff split among members weighted by their reputation.

        Args:
            total_payoff: The total payoff to split.
            members: List of agent IDs in the coalition.

        Returns:
            A dict mapping agent_id to their payoff share.
        """
        reputations = {}
        total_reputation = 0.0
        for agent_id in members:
            mem = self.agent_memories.get(agent_id)
            rep = mem.get_reputation() if mem else 1.0
            reputations[agent_id] = rep
            total_reputation += rep

        if total_reputation == 0:
            # Avoid division by zero, split equally
            equal_share = total_payoff / len(members)
            shares = {agent_id: equal_share for agent_id in members}
        else:
            shares = {agent_id: (
                reputations[agent_id] / total_reputation) * total_payoff for agent_id in members}

        # Log and update negotiation histories
        for agent_id, share in shares.items():
            mem = self.agent_memories.get(agent_id)
            if mem:
                outcome = {
                    "coalition_members": members,
                    "total_payoff": total_payoff,
                    "proposed_share": share,
                    "reputation": reputations[agent_id],
                }
                mem.log_negotiation_result(outcome)
                logger.debug(f"Negotiation split for {agent_id}: {outcome}")

        return shares

    def propose_trade_with_pitch(self, initiator_agent, target_agent, trade_details: Dict[str, Any], llm=None) -> Dict[str, Any]:
        """
        Propose a trade with persuasion pitch integration.

        Args:
            initiator_agent: The agent proposing the trade
            target_agent: The target agent for the trade  
            trade_details: Details of the proposed trade
            llm: Optional LLM for pitch generation

        Returns:
            Dict containing trade proposal and pitch results
        """
        correlation_id = str(uuid.uuid4())

        # Generate persuasion pitch if verbal exchange is enabled
        pitch_result = initiator_agent.generate_persuasion_pitch(
            target_capsule=self._get_agent_capsule(target_agent),
            context="trade",
            llm=llm
        )

        # Create trade proposal
        trade_proposal = {
            "type": "trade_proposal",
            "initiator": initiator_agent.get_agent_id() or initiator_agent.capsule_id,
            "target": target_agent.get_agent_id() or target_agent.capsule_id,
            "trade_details": trade_details,
            "pitch": pitch_result,
            "correlation_id": correlation_id,
            "timestamp": time.time()
        }

        # Calculate acceptance probability based on pitch and capsule alignment
        acceptance_probability = self._calculate_acceptance_probability(
            initiator_agent, target_agent, trade_details, pitch_result
        )

        trade_proposal["acceptance_probability"] = acceptance_probability

        # Log the trade proposal
        self._log_trade_proposal(trade_proposal)

        # Log pitch reception in target agent's memory
        self._log_pitch_reception(target_agent, pitch_result, correlation_id)

        return trade_proposal

    def propose_coalition_with_pitch(self, initiator_agent, target_agents: List, coalition_details: Dict[str, Any], llm=None) -> Dict[str, Any]:
        """
        Propose a coalition with persuasion pitches for each target.

        Args:
            initiator_agent: The agent proposing the coalition
            target_agents: List of target agents for the coalition
            coalition_details: Details of the proposed coalition
            llm: Optional LLM for pitch generation

        Returns:
            Dict containing coalition proposal and pitch results
        """
        correlation_id = str(uuid.uuid4())

        # Generate pitches for each target
        pitch_results = []
        for target_agent in target_agents:
            pitch_result = initiator_agent.generate_persuasion_pitch(
                target_capsule=self._get_agent_capsule(target_agent),
                context="coalition",
                llm=llm
            )
            pitch_results.append({
                "target": target_agent.get_agent_id() or target_agent.capsule_id,
                "pitch": pitch_result
            })

        # Create coalition proposal
        coalition_proposal = {
            "type": "coalition_proposal",
            "initiator": initiator_agent.get_agent_id() or initiator_agent.capsule_id,
            "targets": [agent.get_agent_id() or agent.capsule_id for agent in target_agents],
            "coalition_details": coalition_details,
            "pitches": pitch_results,
            "correlation_id": correlation_id,
            "timestamp": time.time()
        }

        # Log the coalition proposal
        self._log_coalition_proposal(coalition_proposal)

        # Log pitch reception for each target
        for target_agent, pitch_data in zip(target_agents, pitch_results):
            self._log_pitch_reception(
                target_agent, pitch_data["pitch"], correlation_id)

        return coalition_proposal

    def _get_agent_capsule(self, agent):
        """
        Extract or create a Capsule from an agent.
        """
        if hasattr(agent, 'capsule_data'):
            # Create a temporary Capsule object from agent data
            from registry.capsule_registry import Capsule
            return Capsule(
                goal=agent.goal or "Unknown goal",
                values=agent.values or {},
                tags=agent.tags or [],
                wallet_address=agent.wallet_address,
                public_snippet=agent.public_snippet,
                capsule_id=agent.capsule_id
            )
        return agent  # Assume it's already a capsule-like object

    def _calculate_acceptance_probability(self, initiator_agent, target_agent, trade_details: Dict[str, Any], pitch_result: Dict[str, Any]) -> float:
        """
        Calculate probability of trade/coalition acceptance based on capsule alignment and pitch quality.
        """
        base_probability = 0.5  # Base 50% chance

        # Boost probability if pitch was successfully generated and paid for
        if pitch_result["success"] and pitch_result["pitch"]:
            base_probability += 0.2  # 20% boost for having a pitch

        # Calculate capsule alignment score
        alignment_score = self._calculate_capsule_alignment(
            initiator_agent, target_agent)
        base_probability += (alignment_score - 0.5) * \
            0.4  # Scale alignment to -0.2 to +0.2

        # Reputation factor
        if hasattr(initiator_agent, 'get_agent_id'):
            initiator_id = initiator_agent.get_agent_id() or initiator_agent.capsule_id
            initiator_memory = self.agent_memories.get(initiator_id)
            if initiator_memory:
                reputation = initiator_memory.get_reputation()
                # Scale reputation to influence
                reputation_factor = (reputation - 1.0) * 0.1
                base_probability += reputation_factor

        # Clamp probability to 0-1 range
        return max(0.0, min(1.0, base_probability))

    def _calculate_capsule_alignment(self, agent1, agent2) -> float:
        """
        Calculate alignment score between two agents' capsules.
        """
        try:
            # Goal similarity (simple string matching)
            goal_similarity = 0.5
            if hasattr(agent1, 'goal') and hasattr(agent2, 'goal'):
                if agent1.goal and agent2.goal:
                    common_words = set(agent1.goal.lower().split()) & set(
                        agent2.goal.lower().split())
                    total_words = set(agent1.goal.lower().split()) | set(
                        agent2.goal.lower().split())
                    goal_similarity = len(
                        common_words) / max(len(total_words), 1) if total_words else 0.5

            # Value similarity
            value_similarity = 0.5
            if hasattr(agent1, 'values') and hasattr(agent2, 'values'):
                if agent1.values and agent2.values:
                    common_values = set(agent1.values.keys()) & set(
                        agent2.values.keys())
                    total_values = set(agent1.values.keys()) | set(
                        agent2.values.keys())
                    value_similarity = len(
                        common_values) / max(len(total_values), 1) if total_values else 0.5

            # Tag similarity
            tag_similarity = 0.5
            if hasattr(agent1, 'tags') and hasattr(agent2, 'tags'):
                if agent1.tags and agent2.tags:
                    common_tags = set(agent1.tags) & set(agent2.tags)
                    total_tags = set(agent1.tags) | set(agent2.tags)
                    tag_similarity = len(
                        common_tags) / max(len(total_tags), 1) if total_tags else 0.5

            # Weighted average
            alignment_score = (goal_similarity * 0.5 +
                               value_similarity * 0.3 + tag_similarity * 0.2)
            return alignment_score

        except Exception:
            return 0.5  # Default neutral alignment

    def _log_trade_proposal(self, proposal: Dict[str, Any]):
        """
        Log trade proposal with pitch details.
        """
        initiator_memory = self.agent_memories.get(proposal["initiator"])
        if initiator_memory:
            log_entry = {
                "event_type": "trade_proposal_sent",
                "correlation_id": proposal["correlation_id"],
                "target": proposal["target"],
                "trade_details": proposal["trade_details"],
                "pitch_cost": proposal["pitch"]["cost"],
                "acceptance_probability": proposal["acceptance_probability"],
                "timestamp": proposal["timestamp"]
            }
            initiator_memory.log_event(log_entry)

    def _log_coalition_proposal(self, proposal: Dict[str, Any]):
        """
        Log coalition proposal with pitch details.
        """
        initiator_memory = self.agent_memories.get(proposal["initiator"])
        if initiator_memory:
            log_entry = {
                "event_type": "coalition_proposal_sent",
                "correlation_id": proposal["correlation_id"],
                "targets": proposal["targets"],
                "coalition_details": proposal["coalition_details"],
                "pitch_costs": [p["pitch"]["cost"] for p in proposal["pitches"]],
                "timestamp": proposal["timestamp"]
            }
            initiator_memory.log_event(log_entry)

    def _log_pitch_reception(self, target_agent, pitch_result: Dict[str, Any], correlation_id: str):
        """
        Log pitch reception in target agent's memory.
        """
        target_id = target_agent.get_agent_id() if hasattr(
            target_agent, 'get_agent_id') else target_agent.capsule_id
        target_memory = self.agent_memories.get(target_id)
        if target_memory:
            log_entry = {
                "event_type": "persuasion_pitch_received",
                "correlation_id": correlation_id,
                "sender": pitch_result["agent_id"],
                "pitch_text": pitch_result["pitch"],
                "context": pitch_result["context"],
                "timestamp": pitch_result["timestamp"]
            }
            target_memory.log_event(log_entry)

    def negotiate_trade_with_appraisal(self, initiator_agent, target_capsule: Capsule,
                                       item_metadata: Dict[str, Any], context: str = "trade",
                                       enable_verbal_exchange: bool = True) -> Dict[str, Any]:
        """
        Enhanced trade negotiation with comprehensive item appraisal.

        Args:
            initiator_agent: Agent initiating the trade
            target_capsule: Target capsule for the trade
            item_metadata: Metadata of the item being traded
            context: Trade context
            enable_verbal_exchange: Whether to use verbal exchange layer

        Returns:
            Dict containing trade negotiation result with full appraisal details
        """
        correlation_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()

        logger.info(f"Starting trade negotiation with appraisal for item {item_metadata.get('name', 'unknown')} "
                    f"correlation_id {correlation_id}")

        try:
            # Step 1: Initiator appraises the item
            initiator_appraisal = initiator_agent.appraise_item(
                item_metadata, context, target_capsule, enable_verbal_exchange
            )

            # Step 2: Check if initiator finds value in the trade
            if initiator_appraisal["decision"] != "accept":
                logger.info(
                    f"Initiator rejected trade based on appraisal: {initiator_appraisal['reasoning']}")
                return {
                    "correlation_id": correlation_id,
                    "timestamp": timestamp,
                    "trade_result": "rejected_by_initiator",
                    "initiator_appraisal": initiator_appraisal,
                    "reason": "Initiator appraisal resulted in rejection"
                }

            # Step 3: Generate pitch if verbal exchange enabled
            pitch_result = None
            if enable_verbal_exchange:
                pitch_result = initiator_agent.generate_persuasion_pitch(
                    target_capsule, context="trade"
                )
                # Log pitch reception
                self._log_pitch_reception(
                    target_capsule, pitch_result, correlation_id)

            # Step 4: Calculate acceptance probability with appraisal data
            acceptance_probability = self._calculate_acceptance_probability_with_appraisal(
                initiator_agent, target_capsule, item_metadata, initiator_appraisal, pitch_result
            )

            # Step 5: Simulate target decision (in real system, target would appraise)
            trade_accepted = acceptance_probability > 0.5

            # Step 6: Create comprehensive trade result
            trade_result = {
                "correlation_id": correlation_id,
                "timestamp": timestamp,
                "initiator_id": initiator_agent.get_agent_id(),
                "target_id": target_capsule.capsule_id,
                "item_metadata": item_metadata,
                "context": context,
                "initiator_appraisal": initiator_appraisal,
                "pitch_result": pitch_result,
                "acceptance_probability": acceptance_probability,
                "trade_result": "accepted" if trade_accepted else "rejected",
                "final_value": initiator_appraisal["final_net_value"],
                "costs_incurred": initiator_appraisal["costs"],
                "archetype_influence": initiator_appraisal["archetype"],
            }

            # Step 7: If accepted, handle NFT minting and ownership transfer
            if trade_accepted:
                nft_result = initiator_agent.mint_nft_on_trade(
                    item_metadata,
                    {
                        "trade_partner": target_capsule.capsule_id,
                        "trade_type": context,
                        "correlation_id": correlation_id
                    }
                )
                trade_result["nft_minted"] = nft_result

            # Step 8: Log comprehensive trade attempt
            self._log_trade_with_appraisal(trade_result)

            # Step 9: Store in trade history
            self.trade_history.append(trade_result)

            return trade_result

        except Exception as e:
            logger.error(
                f"Error in trade negotiation with appraisal {correlation_id}: {e}")
            return {
                "correlation_id": correlation_id,
                "timestamp": timestamp,
                "trade_result": "error",
                "error": str(e)
            }

    def evaluate_proposal_with_appraisal(self, evaluator_agent, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a trade proposal using comprehensive appraisal system.

        Args:
            evaluator_agent: Agent evaluating the proposal
            proposal: Trade proposal to evaluate

        Returns:
            Dict containing evaluation result with appraisal details
        """
        correlation_id = str(uuid.uuid4())

        try:
            # Extract item metadata from proposal
            item_metadata = proposal.get("item_metadata", {})
            context = proposal.get("context", "trade")

            # Get proposer capsule if available
            proposer_capsule = None
            # In a real system, you'd fetch this from registry

            # Perform appraisal
            evaluation_appraisal = evaluator_agent.appraise_item(
                item_metadata, context, proposer_capsule, False  # No pitch cost for evaluation
            )

            # Create evaluation result
            evaluation_result = {
                "correlation_id": correlation_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "evaluator_id": evaluator_agent.get_agent_id(),
                "proposal_id": proposal.get("correlation_id", "unknown"),
                "evaluation_appraisal": evaluation_appraisal,
                "decision": evaluation_appraisal["decision"],
                "reasoning": evaluation_appraisal["reasoning"],
                "net_value": evaluation_appraisal["final_net_value"]
            }

            # Log evaluation
            self._log_proposal_evaluation(evaluation_result)

            return evaluation_result

        except Exception as e:
            logger.error(
                f"Error in proposal evaluation with appraisal {correlation_id}: {e}")
            return {
                "correlation_id": correlation_id,
                "decision": "error",
                "error": str(e)
            }

    def _calculate_acceptance_probability_with_appraisal(self, initiator_agent, target_capsule: Capsule,
                                                         item_metadata: Dict[str, Any],
                                                         initiator_appraisal: Dict[str, Any],
                                                         pitch_result: Optional[Dict[str, Any]]) -> float:
        """
        Calculate acceptance probability incorporating appraisal data.
        """
        try:
            # Base probability from capsule alignment
            base_alignment = self.calculate_capsule_alignment(
                initiator_agent.capsule_data, target_capsule
            )

            # Factor in appraisal quality
            appraisal_factor = min(
                initiator_appraisal["final_net_value"] / 100, 1.0)  # Normalize to 0-1

            # Factor in pitch quality if available
            pitch_factor = 0.0
            if pitch_result and pitch_result.get("cost", 0) == 0:  # Free pitch
                pitch_factor = 0.1
            # Premium pitch
            elif pitch_result and pitch_result.get("cost", 0) > 0:
                pitch_factor = 0.2

            # Combine factors
            acceptance_prob = (base_alignment * 0.6) + \
                (appraisal_factor * 0.3) + pitch_factor

            # Apply some randomness and constraints
            return max(0.0, min(1.0, acceptance_prob))

        except Exception as e:
            logger.warning(f"Error calculating acceptance probability: {e}")
            return 0.3  # Default moderate probability

    def _log_trade_with_appraisal(self, trade_result: Dict[str, Any]):
        """
        Log comprehensive trade result with appraisal details.
        """
        correlation_id = trade_result["correlation_id"]

        # Log to initiator's memory
        initiator_memory = self.agent_memories.get(
            trade_result["initiator_id"])
        if initiator_memory:
            log_entry = {
                "event_type": "trade_negotiation_completed",
                "correlation_id": correlation_id,
                "target": trade_result["target_id"],
                "item": trade_result["item_metadata"].get("name", "unknown"),
                "trade_result": trade_result["trade_result"],
                "final_value": trade_result["final_value"],
                "costs": trade_result["costs_incurred"],
                "acceptance_probability": trade_result["acceptance_probability"],
                "nft_minted": trade_result.get("nft_minted", {}).get("nft_id"),
                "timestamp": trade_result["timestamp"]
            }
            initiator_memory.log_event(log_entry)

        # Log to target's memory
        target_memory = self.agent_memories.get(trade_result["target_id"])
        if target_memory:
            log_entry = {
                "event_type": "trade_proposal_received",
                "correlation_id": correlation_id,
                "initiator": trade_result["initiator_id"],
                "item": trade_result["item_metadata"].get("name", "unknown"),
                "result": trade_result["trade_result"],
                "timestamp": trade_result["timestamp"]
            }
            target_memory.log_event(log_entry)

        # Comprehensive logging
        logger.info(f"=== TRADE NEGOTIATION COMPLETE [{correlation_id}] ===")
        logger.info(f"Initiator: {trade_result['initiator_id']}")
        logger.info(f"Target: {trade_result['target_id']}")
        logger.info(
            f"Item: {trade_result['item_metadata'].get('name', 'unknown')}")
        logger.info(f"Result: {trade_result['trade_result'].upper()}")
        logger.info(f"Final Value: ${trade_result['final_value']:.2f}")
        logger.info(
            f"Acceptance Probability: {trade_result['acceptance_probability']:.2f}")
        if trade_result.get("nft_minted"):
            logger.info(f"NFT Minted: {trade_result['nft_minted']['nft_id']}")
        logger.info(f"=== END TRADE [{correlation_id}] ===")

    def _log_proposal_evaluation(self, evaluation_result: Dict[str, Any]):
        """
        Log proposal evaluation result.
        """
        evaluator_memory = self.agent_memories.get(
            evaluation_result["evaluator_id"])
        if evaluator_memory:
            log_entry = {
                "event_type": "proposal_evaluated",
                "correlation_id": evaluation_result["correlation_id"],
                "proposal_id": evaluation_result["proposal_id"],
                "decision": evaluation_result["decision"],
                "net_value": evaluation_result["net_value"],
                "timestamp": evaluation_result["timestamp"]
            }
            evaluator_memory.log_event(log_entry)

    def get_trade_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trade history."""
        return self.trade_history[-limit:] if self.trade_history else []

    def get_agent_trade_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive trade statistics for an agent."""
        agent_trades = [t for t in self.trade_history if t.get(
            "initiator_id") == agent_id]

        if not agent_trades:
            return {"total_trades": 0, "success_rate": 0.0, "average_value": 0.0}

        successful_trades = [t for t in agent_trades if t.get(
            "trade_result") == "accepted"]
        total_value = sum(t.get("final_value", 0) for t in agent_trades)

        return {
            "total_trades": len(agent_trades),
            "successful_trades": len(successful_trades),
            "success_rate": len(successful_trades) / len(agent_trades),
            "average_value": total_value / len(agent_trades),
            "total_value": total_value,
        }
