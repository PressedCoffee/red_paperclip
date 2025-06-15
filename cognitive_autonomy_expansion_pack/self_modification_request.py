import datetime
from typing import Any, Dict, Optional

# Assuming MetaReasoningEngine and agent lifecycle components are available
from cognitive_autonomy_expansion_pack.meta_reasoning_engine import GenesisMetaReasoner
from agents.agent import AgentLifecycleManager
from agents.badge_xp_system import grant_xp, trigger_badge_unlock
from ui.snapshot_panel import SnapshotPanel


class GenesisSelfModificationRequest:
    """
    Framework for agent-proposed changes with permission model, audit trail, and review hooks.
    Integrates with MetaReasoner and agent lifecycle.
    Includes XP triggers and capsule snapshots.
    """

    def __init__(self, meta_reasoner: GenesisMetaReasoner,
                 lifecycle_manager: AgentLifecycleManager,
                 snapshot_panel: Optional[SnapshotPanel] = None):
        self.meta_reasoner = meta_reasoner
        self.lifecycle_manager = lifecycle_manager
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

    def review_request(self, request: Dict[str, Any], approved: bool, reviewer_comments: Optional[str] = None):
        """
        Review a self-modification request, approve or reject it.
        """
        request["status"] = "approved" if approved else "rejected"
        request["review_comments"] = reviewer_comments
        request["review_timestamp"] = datetime.datetime.utcnow().isoformat()
        self._log_request(request)

        if approved:
            self._execute_modification(request)
            grant_xp(request["agent_id"], amount=20,
                     reason="Approved self-modification")
            trigger_badge_unlock(
                request["agent_id"], badge_name="Self-Modifier")

        if self.snapshot_panel:
            self.snapshot_panel.update_self_mod_request(request)

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
