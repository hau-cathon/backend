"""Email routes for inbox checks and ticket communication history."""
from datetime import datetime
from bson import ObjectId
from mongoengine.queryset.visitor import Q

from flask import Blueprint, jsonify, request, current_app

from app.models.email_message import EmailMessage
from app.models.issue import Issue
from app.services.action_history_service import ActionHistoryService
from app.utils.SMTP import send_email
from ..utils.email_reader import read_unread_emails, mark_as_read

email_bp = Blueprint('email_api', __name__)


def _is_smtp_configured() -> bool:
    return bool(
        current_app.config.get('MAIL_SERVER')
        and current_app.config.get('MAIL_PORT')
        and current_app.config.get('MAIL_USERNAME')
        and current_app.config.get('MAIL_PASSWORD')
    )


def _safe_log_action(**kwargs):
    try:
        ActionHistoryService.create_action(**kwargs)
    except Exception:
        # Action history must never break API response.
        pass


def _resolve_issue_ref(ticket_ref):
    value = str(ticket_ref or '').strip()
    if not value:
        return None

    issue = None
    if ObjectId.is_valid(value):
        issue = Issue.objects(id=value).first()

    if issue is None:
        issue = Issue.objects(title=value).first()

    return issue


@email_bp.route('/ticket/<ticket_id>/history', methods=['GET'], endpoint='ticket_history')
def get_ticket_email_history(ticket_id):
    """Get persisted email history for a ticket."""
    try:
        issue = _resolve_issue_ref(ticket_id)
        query = Q(ticket_id=ticket_id)

        if issue is not None:
            query = query | Q(issue=issue)
            if issue.title:
                query = query | Q(ticket_id=issue.title)

        emails = EmailMessage.objects(query).order_by('-created_at')
        return jsonify({
            'status': 'success',
            'count': len(emails),
            'emails': [email.to_dict() for email in emails],
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
        }), 500


@email_bp.route('/ticket/<ticket_id>/send', methods=['POST'], endpoint='ticket_send')
def send_ticket_email(ticket_id):
    """Send (or mock-send in dev) email for a ticket and persist it."""
    try:
        data = request.get_json() or {}
        required_fields = ['to_email', 'subject', 'body']
        for field in required_fields:
            if not str(data.get(field, '')).strip():
                return jsonify({
                    'status': 'error',
                    'error': f'Missing required field: {field}',
                }), 400

        to_email = str(data['to_email']).strip()
        subject = str(data['subject']).strip()
        body = str(data['body']).strip()
        html_body = data.get('html_body')
        cc_emails = str(data.get('cc_emails', '')).strip() or None
        is_automated = bool(data.get('is_automated', False))
        issue = _resolve_issue_ref(ticket_id)

        stored_ticket_id = str(ticket_id)
        if issue is not None:
            stored_ticket_id = str(issue.id)

        smtp_configured = _is_smtp_configured()
        delivery_mode = 'mock'
        sent_ok = True

        if smtp_configured:
            sent_ok = send_email(to_email, subject, body, html_body=html_body)
            delivery_mode = 'smtp' if sent_ok else 'smtp_failed'

        email = EmailMessage(
            ticket_id=stored_ticket_id,
            issue=issue,
            direction='outbound',
            from_email=(current_app.config.get('MAIL_USERNAME') or 'noreply@animalhelper.local'),
            to_email=to_email,
            cc_emails=cc_emails,
            subject=subject,
            body=body,
            html_body=html_body,
            is_automated=is_automated,
            metadata={
                'delivery_mode': delivery_mode,
                'smtp_configured': smtp_configured,
                'delivery_success': sent_ok,
            },
        )
        email.save()

        timeline_type = 'success' if sent_ok else 'alert'
        _safe_log_action(
            ticket_id=stored_ticket_id,
            action_type='email_sent',
            label='Wyslano wiadomosc email' if sent_ok else 'Nieudana wysylka email',
            detail=f'Do: {to_email} | Temat: {subject}',
            timeline_type=timeline_type,
            source='backend.email_routes',
            metadata={
                'email_id': str(email.id),
                'to_email': to_email,
                'subject': subject,
                'delivery_mode': delivery_mode,
            },
        )

        if not sent_ok:
            return jsonify({
                'status': 'error',
                'error': 'Email could not be sent via SMTP',
                'email_id': str(email.id),
                'delivery_mode': delivery_mode,
            }), 502

        return jsonify({
            'status': 'success',
            'message': 'Email saved and sent' if smtp_configured else 'Email saved (mock delivery)',
            'email_id': str(email.id),
            'delivery_mode': delivery_mode,
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
        }), 500


@email_bp.route('/check', methods=['GET'], endpoint='check_mailbox')
def check_emails():
    """Sprawdza i odczytuje nowe emaile"""
    try:
        emails = read_unread_emails()

        persisted_count = 0
        for item in emails:
            ticket_ref = str(item.get('ticket_number') or '').strip()
            if not ticket_ref:
                continue

            external_id = str(item.get('email_id') or '').strip() or None
            if external_id and EmailMessage.objects(external_id=external_id).first():
                continue

            email_doc = EmailMessage(
                ticket_id=ticket_ref,
                direction='inbound',
                from_email=str(item.get('from') or 'unknown@sender.local'),
                to_email=(current_app.config.get('MAIL_USERNAME') or 'noreply@animalhelper.local'),
                subject=str(item.get('subject') or '(brak tematu)'),
                body=str(item.get('body') or ''),
                external_id=external_id,
                is_automated=False,
                metadata={
                    'mailbox_date': item.get('date'),
                    'raw_ticket_number': item.get('ticket_number'),
                },
            )
            email_doc.save()
            persisted_count += 1

            _safe_log_action(
                ticket_id=ticket_ref,
                action_type='email_received',
                label='Odebrano wiadomosc email',
                detail=f"Od: {email_doc.from_email} | Temat: {email_doc.subject}",
                timeline_type='info',
                source='backend.email_routes',
                metadata={
                    'email_id': str(email_doc.id),
                    'external_id': email_doc.external_id,
                },
            )
        
        return jsonify({
            'status': 'success',
            'count': len(emails),
            'persisted': persisted_count,
            'emails': emails
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_bp.route('/mark-read/<email_id>', methods=['POST'], endpoint='mark_read')
def mark_email_read(email_id):
    """Oznacza email jako przeczytany"""
    try:
        email_doc = EmailMessage.objects(id=email_id).first()
        if email_doc:
            email_doc.read_at = datetime.utcnow()
            email_doc.save()
            return jsonify({
                'status': 'success',
                'message': 'Email oznaczony jako przeczytany'
            }), 200

        success = mark_as_read(email_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Email oznaczony jako przeczytany'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Nie udało się oznaczyć emaila'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500