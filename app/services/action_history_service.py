from bson import ObjectId
from mongoengine.queryset.visitor import Q

from app.models.action_history import ActionHistoryEntry
from app.models.issue import Issue


class ActionHistoryService:
    @staticmethod
    def _resolve_issue(ticket_id: str):
        if not ticket_id:
            return None

        issue = None
        if ObjectId.is_valid(ticket_id):
            issue = Issue.objects(id=ticket_id).first()

        if issue is None:
            issue = Issue.objects(title=ticket_id).first()

        return issue

    @staticmethod
    def create_action(
        ticket_id: str,
        action_type: str,
        label: str,
        detail: str,
        timeline_type: str = 'info',
        source: str = 'frontend',
        actor_id: str = None,
        metadata: dict = None,
    ) -> ActionHistoryEntry:
        resolved_ticket = str(ticket_id or '').strip()
        if not resolved_ticket:
            raise ValueError('ticket_id is required')

        issue = ActionHistoryService._resolve_issue(resolved_ticket)
        action = ActionHistoryEntry(
            ticket_id=resolved_ticket,
            issue=issue,
            action_type=action_type,
            timeline_type=timeline_type,
            label=label,
            detail=detail,
            source=source,
            actor_id=actor_id,
            metadata=metadata or {},
        )
        action.save()
        return action

    @staticmethod
    def list_actions(ticket_id: str, limit: int = 200):
        resolved_ticket = str(ticket_id or '').strip()
        if not resolved_ticket:
            return []

        issue = ActionHistoryService._resolve_issue(resolved_ticket)
        if issue is not None:
            query = Q(ticket_id=resolved_ticket) | Q(issue=issue)
            return ActionHistoryEntry.objects(query).order_by('created_at').limit(limit)

        return ActionHistoryEntry.objects(ticket_id=resolved_ticket).order_by('created_at').limit(limit)
