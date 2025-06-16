import datetime
import uuid
from typing import Any, Dict, Optional

# Assuming MetaReasoningEngine and agent lifecycle components are available
from cognitive_autonomy_expansion_pack.meta_reasoning_engine import GenesisMetaReasoner
from agents.agent import AgentLifecycleManager
from agents.badge_xp_system import grant_xp, trigger_badge_unlock
from agents.goal_reevaluation_module import GoalReevaluationModule
from ui.snapshot_panel import SnapshotPanel
from registry.capsule_registry import CapsuleRegistry
from memory.agent_memory import AgentMemory


class GenesisSelfModificationRequest:
    """
    Framework for agent-proposed changes with permission model, audit trail, and review hooks.
    Integrates with MetaReasoner, Goal Reevaluation, and agent lifecycle.
    Includes deep Capsule hooks and LLM integration.
    """

    def __init__(self,
                 capsule_registry: CapsuleRegistry,
                 goal_module: GoalReevaluationModule,
                 agent_memory: AgentMemory,
                 meta_reasoner: Optional[GenesisMetaReasoner] = None,
                 lifecycle_manager: Optional[AgentLifecycleManager] = None,
                 llm: Optional[Any] = None,
                 live_mode: bool = False,
                 snapshot_panel: Optional[SnapshotPanel] = None):
        self.capsule_registry = capsule_registry
        self.goal_module = goal_module
        self.agent_memory = agent_memory
        self.meta_reasoner = meta_reasoner
        self.lifecycle_manager = lifecycle_manager
        self.llm = llm
        self.live_mode = live_mode
        self.snapshot_panel = snapshot_panel
        self.audit_trail: list[Dict[str, Any]] = []

    def create_request(self, agent_id: str, modification_details: Dict[str, Any], requires_approval: bool = True) -> Dict[str, Any]:
        """
        Create a self-modification request.
        """
        request = {
            "agent_id": agent_id,
            "modification_details": modification_details,
            "requires_approval": requires_approval,
            "status": "pending",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "review_comments": None,
        }
        self._log_request(request)
        return request

    def review_request(self, request: Dict[str, Any], reviewer_comments: Optional[str] = None) -> bool:
        """
        Review a self-modification request, approve or reject it.
        Uses LLM to validate or auto-approve if live_mode is True.
        Logs all LLM prompts and completions in agent_memory.
        Logs decisions in Capsule Registry.
        """
        correlation_id = str(uuid.uuid4())
        approved = False
        if self.live_mode:
            prompt = f"Validate the following self-modification request and decide to approve or reject:\n{request}\nComments:"
            # Log prompt to agent_memory
            self.agent_memory.log_interaction({
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "correlation_id": correlation_id,
                "type": "llm_prompt",
                "content": prompt,
            })
            # Invoke LLM
            completion = self.llm.invoke(prompt)
            # Log completion to agent_memory
            self.agent_memory.log_interaction({
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "correlation_id": correlation_id,
                "type": "llm_completion",
                "content": completion,
            })
            # Determine approval based on LLM output (simple heuristic)
            approved = "approve" in completion.lower()
            review_comments = completion.strip()
        else:
            # Fallback path when live_mode is False
            approved = not request.get("requires_approval", True)
            review_comments = reviewer_comments

        request["status"] = "approved" if approved else "rejected"
        request["review_comments"] = review_comments
        request["review_timestamp"] = datetime.datetime.utcnow().isoformat()
        self._log_request(request)

        # Log decision in Capsule Registry
        capsule_data = {
            "agent_id": request["agent_id"],
            "goal": "Self-Modification Decision",
            "values": {
                "request": request,
                "approved": approved,
                "review_comments": review_comments,
                "correlation_id": correlation_id,
            },
            "tags": ["self_modification", "decision"],
        }
        self.capsule_registry.create_capsule(capsule_data)

        if approved:
            self._execute_modification(request)
            grant_xp(request["agent_id"], amount=20,
                     reason="Approved self-modification")
            trigger_badge_unlock(
                request["agent_id"], badge_name="Self-Modifier")

        if self.snapshot_panel:
            self.snapshot_panel.update_self_mod_request(request)

        return approved

    def _execute_modification(self, request: Dict[str, Any]):
        """
        Execute the approved modification.
        Placeholder for actual modification logic.
        """
        # TODO: Implement actual self-modification execution logic
        self.lifecycle_manager.apply_modification(
            request["agent_id"], request["modification_details"])

    def _log_request(self, request: Dict[str, Any]):
        """
        Log the request to the audit trail and update snapshot panel.
        """
        self.audit_trail.append(request)
        if self.snapshot_panel:
            self.snapshot_panel.update_self_mod_request(request)

    def get_snapshot_metadata(self) -> Dict[str, Any]:
        """
        Return structured metadata for agent snapshot observability.
        """
        last_request = self.audit_trail[-1] if self.audit_trail else None
        return {
            "self_mod_request_status": last_request["status"] if last_request else None,
            "last_self_mod_request": last_request,
            "audit_trail_length": len(self.audit_trail),
        }

    def propose_modification(self, capsule_id: str, modification: Dict[str, Any], agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Core method for proposing and applying capsule modifications.

        Args:
            capsule_id: ID of the capsule to modify
            modification: Dict containing proposed changes (goal, values, tags)
            agent_id: Optional agent ID for logging (defaults to capsule_id)

        Returns:
            Dict with status, details, and any error information
        """
        correlation_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat()
        agent_id = agent_id or capsule_id

        # Get the capsule
        capsule = self.capsule_registry.get_capsule(capsule_id)
        if not capsule:
            result = {
                "status": "error",
                "reason": "Capsule not found",
                "capsule_id": capsule_id,
                "correlation_id": correlation_id,
                "timestamp": timestamp
            }
            self._log_modification_event(
                agent_id, "error", result, correlation_id)
            return result

        # Store original state for audit trail
        original_capsule_state = capsule.to_dict()

        # Validate modification request
        validation_result = self._validate_modification(capsule, modification)
        if not validation_result["valid"]:
            result = {
                "status": "rejected",
                "reason": validation_result["reason"],
                "capsule_id": capsule_id,
                "modification": modification,
                "correlation_id": correlation_id,
                "timestamp": timestamp
            }
            self._log_modification_event(
                agent_id, "rejected", result, correlation_id)
            return result

        # Apply the modification
        try:
            modified_fields = []
            for field, value in modification.items():
                if hasattr(capsule, field):
                    old_value = getattr(capsule, field)
                    setattr(capsule, field, value)
                    modified_fields.append({
                        "field": field,
                        "old_value": old_value,
                        "new_value": value
                    })

            # Update capsule in registry
            self.capsule_registry.update_capsule(capsule_id, capsule)

            # Trigger immediate goal reevaluation
            self.goal_module.reevaluate_capsule(capsule)

            # Grant XP for successful self-modification
            grant_xp(agent_id, 10, "Successful self-modification")

            result = {
                "status": "approved",
                "capsule_id": capsule_id,
                "modification": modification,
                "modified_fields": modified_fields,
                "original_state": original_capsule_state,
                "new_state": capsule.to_dict(),
                "correlation_id": correlation_id,
                "timestamp": timestamp
            }

            self._log_modification_event(
                agent_id, "approved", result, correlation_id)
            return result

        except Exception as e:
            result = {
                "status": "error",
                "reason": f"Failed to apply modification: {str(e)}",
                "capsule_id": capsule_id,
                "modification": modification,
                "correlation_id": correlation_id,
                "timestamp": timestamp
            }
            self._log_modification_event(
                agent_id, "error", result, correlation_id)
            return result

    def _validate_modification(self, capsule, modification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if a modification request is allowed.

        Args:
            capsule: The capsule to be modified
            modification: Proposed modifications

        Returns:
            Dict with validation result
        """
        # Define allowed fields for modification
        # Added archetype to allowed fields
        ALLOWED_FIELDS = ["values", "tags", "goal", "archetype"]

        # Check if all proposed fields are allowed
        proposed_fields = set(modification.keys())
        if not proposed_fields.issubset(ALLOWED_FIELDS):
            invalid_fields = proposed_fields - ALLOWED_FIELDS
            return {
                "valid": False,
                "reason": f"Invalid fields: {list(invalid_fields)}. Allowed: {list(ALLOWED_FIELDS)}"
            }

        # Additional validation using LLM if available
        if self.live_mode and self.llm and self.meta_reasoner:
            try:
                alignment_score = self._check_capsule_alignment(
                    capsule, modification)
                if alignment_score < 0.3:  # Threshold for alignment
                    return {
                        "valid": False,
                        "reason": f"Modification poorly aligned with current capsule (score: {alignment_score:.2f})"
                    }
            except Exception as e:
                # If LLM validation fails, fall back to basic validation
                pass

        return {"valid": True, "reason": "Validation passed"}

    def _check_capsule_alignment(self, capsule, modification: Dict[str, Any]) -> float:
        """
        Use LLM to check alignment between current capsule and proposed modification.

        Returns:
            Float between 0-1 representing alignment score
        """
        if not self.llm:
            return 0.8  # Default alignment if no LLM

        prompt = f"""
        Analyze the alignment between a capsule's current state and a proposed modification.
        
        Current Capsule:
        - Goal: {capsule.goal}
        - Values: {capsule.values}
        - Tags: {capsule.tags}
        
        Proposed Modification:
        {modification}
        
        Rate the alignment on a scale of 0.0 to 1.0, where:
        - 1.0 = Perfect alignment, modification enhances current direction
        - 0.5 = Neutral, modification doesn't conflict but doesn't strongly align
        - 0.0 = Poor alignment, modification conflicts with current goals/values
        
        Respond with just the numeric score (e.g., 0.7).
        """

        try:
            response = self.llm.invoke(prompt)
            # Extract numeric score from response
            score_str = response.strip()
            score = float(score_str)
            return max(0.0, min(1.0, score))  # Clamp to 0-1 range
        except:
            return 0.8  # Default fallback

    def _log_modification_event(self, agent_id: str, event_type: str, details: Dict[str, Any], correlation_id: str):
        """
        Log modification events to agent memory and audit trail.
        """
        event = {
            "event_type": f"self_modification_{event_type}",
            "agent_id": agent_id,
            "capsule_snapshot": details.get("new_state", details.get("original_state")),
            "timestamp": details.get("timestamp", datetime.datetime.utcnow().isoformat()),
            "correlation_id": correlation_id,
            "details": details
        }

        # Log to agent memory
        if self.agent_memory:
            self.agent_memory.log_event(event)

        # Store in audit trail
        self.audit_trail.append(event)

        # Log LLM interaction if used
        if self.live_mode and details.get("llm_used"):
            llm_log = {
                "type": "llm_interaction",
                "timestamp": event["timestamp"],
                "correlation_id": correlation_id,
                "prompt": "Self-modification alignment check",
                "completion": str(details.get("alignment_score", "N/A")),
                "live_mode": self.live_mode
            }
            if self.agent_memory:
                self.agent_memory.store_llm_interaction(llm_log)
