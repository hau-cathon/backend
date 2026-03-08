"""Email reading routes"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from ..utils.email_reader import read_unread_emails, mark_as_read, extract_ticket_number
from ..utils.SMTP import send_email
from ..models.email_message import EmailMessage
from ..models.issue import Issue

email_bp = Blueprint('email', __name__)


@email_bp.route('/check', methods=['GET'])
def check_emails():
    """Sprawdza i odczytuje nowe emaile, automatycznie przypisując do zgłoszeń"""
    try:
        emails = read_unread_emails()
        processed = []
        errors = []
        
        for email_data in emails:
            try:
                # Znajdź numer zgłoszenia
                ticket_number = email_data.get('ticket_number')
                
                if ticket_number:
                    # Znajdź zgłoszenie po numerze
                    issue = Issue.objects(ticket_number=ticket_number).first()
                    
                    if issue:
                        # Zapisz email do bazy
                        email_msg = EmailMessage(
                            ticket_id=str(issue.id),
                            direction='inbound',
                            from_email=email_data['sender'],
                            to_email='system@example.com',  # TODO: get from config
                            subject=email_data['subject'],
                            body=email_data['full_body'],
                            external_id=email_data['email_id'],
                            read_at=datetime.utcnow()
                        )
                        email_msg.save()
                        
                        # Oznacz jako przeczytany
                        mark_as_read(email_data['email_id'])
                        
                        processed.append({
                            'email_id': email_data['email_id'],
                            'ticket_id': str(issue.id),
                            'ticket_number': ticket_number,
                            'status': 'assigned'
                        })
                    else:
                        errors.append({
                            'email_id': email_data['email_id'],
                            'issue': f'Ticket {ticket_number} not found',
                            'subject': email_data['subject']
                        })
                else:
                    errors.append({
                        'email_id': email_data['email_id'],
                        'issue': 'No ticket number found in email',
                        'subject': email_data['subject']
                    })
                    
            except Exception as e:
                errors.append({
                    'email_id': email_data.get('email_id', 'unknown'),
                    'error': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'total': len(emails),
            'processed': len(processed),
            'errors': len(errors),
            'details': {'processed': processed, 'errors': errors}
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_bp.route('/ticket/<ticket_identifier>/history', methods=['GET'])
def get_ticket_email_history(ticket_identifier):
    """Pobiera historię maili dla danego zgłoszenia (po ID lub ticket_number)"""
    try:
        # Spróbuj znaleźć issue po ticket_number lub MongoDB ID
        issue = Issue.objects(ticket_number=ticket_identifier).first()
        if not issue:
            from bson import ObjectId
            if ObjectId.is_valid(ticket_identifier):
                issue = Issue.objects(id=ticket_identifier).first()
        
        if not issue:
            return jsonify({
                'status': 'error',
                'error': 'Zgłoszenie nie znalezione'
            }), 404
        
        emails = EmailMessage.objects(ticket_id=str(issue.id)).order_by('-created_at')
        
        return jsonify({
            'status': 'success',
            'count': len(emails),
            'emails': [email.to_dict() for email in emails]
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_bp.route('/ticket/<ticket_identifier>/send', methods=['POST'])
def send_ticket_email(ticket_identifier):
    """Wysyła email w kontekście zgłoszenia (po ID lub ticket_number)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Brak danych'
            }), 400
        
        # Walidacja
        to_email = data.get('to_email')
        subject = data.get('subject')
        body = data.get('body')
        html_body = data.get('html_body')
        
        if not all([to_email, subject, body]):
            return jsonify({
                'status': 'error',
                'error': 'Wymagane pola: to_email, subject, body'
            }), 400
        
        # Znajdź zgłoszenie po ticket_number lub MongoDB ID
        issue = Issue.objects(ticket_number=ticket_identifier).first()
        if not issue:
            from bson import ObjectId
            if ObjectId.is_valid(ticket_identifier):
                issue = Issue.objects(id=ticket_identifier).first()
        if not issue:
            return jsonify({
                'status': 'error',
                'error': 'Zgłoszenie nie znalezione'
            }), 404
        
        # Dodaj numer zgłoszenia do tematu jeśli istnieje
        if issue.ticket_number:
            subject = f"[{issue.ticket_number}] {subject}"
        
        # Zapisz email w bazie (bez realnego wysyłania)
        from flask import current_app
        from_email = current_app.config.get('MAIL_USERNAME') or 'system@pieski.pl'
        
        email_msg = EmailMessage(
            ticket_id=str(issue.id),
            direction='outbound',
            from_email=from_email,
            to_email=to_email,
            cc_emails=data.get('cc_emails'),
            subject=subject,
            body=body,
            html_body=html_body,
            is_automated=data.get('is_automated', False),
            created_at=datetime.utcnow()
        )
        email_msg.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Email zapisany',
            'email_id': str(email_msg.id),
            'note': 'Email został zapisany w bazie danych (nie wysłano realnie)'
        }), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@email_bp.route('/mark-read/<email_id>', methods=['POST'])
def mark_email_read(email_id):
    """Oznacza email jako przeczytany"""
    try:
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