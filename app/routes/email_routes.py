"""Email reading routes"""
from flask import Blueprint, jsonify
from ..utils.email_reader import read_unread_emails, mark_as_read

email_bp = Blueprint('email', __name__)


@email_bp.route('/check', methods=['GET'])
def check_emails():
    """Sprawdza i odczytuje nowe emaile"""
    try:
        emails = read_unread_emails()
        
        return jsonify({
            'status': 'success',
            'count': len(emails),
            'emails': emails
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