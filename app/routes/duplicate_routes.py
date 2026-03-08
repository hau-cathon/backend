"""Duplicate detection routes"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.issue import Issue
from app.utils.duplicate_detector import DuplicateDetector
from bson import ObjectId

duplicate_bp = Blueprint('duplicates', __name__)


@duplicate_bp.route('/check/<issue_identifier>', methods=['GET'])
# @jwt_required()
def check_duplicates(issue_identifier):
    """
    Sprawdza potencjalne duplikaty dla danego zgłoszenia
    
    Query params:
        days: ile dni wstecz sprawdzać (domyślnie 7)
        threshold: próg podobieństwa 0-1 (domyślnie 0.7)
    """
    try:
        # Znajdź issue po ticket_number lub MongoDB ID
        issue = Issue.objects(ticket_number=issue_identifier).first()
        if not issue:
            # Walidacja issue_id
            if not ObjectId.is_valid(issue_identifier):
                return jsonify({
                    'status': 'error',
                    'error': 'Nieprawidłowe ID zgłoszenia'
                }), 400
            
            # Pobierz zgłoszenie
            issue = Issue.objects(id=issue_identifier).first()
        
        if not issue:
            return jsonify({
                'status': 'error',
                'error': 'Zgłoszenie nie zostało znalezione'
            }), 404
        
        # Pobierz parametry z query string
        days = request.args.get('days', default=7, type=int)
        threshold = request.args.get('threshold', default=0.7, type=float)
        
        # Walidacja parametrów
        if days < 1 or days > 365:
            return jsonify({
                'status': 'error',
                'error': 'Parametr "days" musi być między 1 a 365'
            }), 400
        
        if threshold < 0 or threshold > 1:
            return jsonify({
                'status': 'error',
                'error': 'Parametr "threshold" musi być między 0 a 1'
            }), 400
        
        # Znajdź duplikaty
        detector = DuplicateDetector(similarity_threshold=threshold)
        duplicates = detector.find_duplicates(issue, days_back=days)
        
        return jsonify({
            'status': 'success',
            'issue_id': str(issue.id),
            'ticket_number': issue.ticket_number,
            'duplicates_found': len(duplicates),
            'duplicates': duplicates,
            'search_params': {
                'days_back': days,
                'threshold': threshold,
                'threshold_percent': threshold * 100
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Błąd podczas sprawdzania duplikatów: {str(e)}'
        }), 500


@duplicate_bp.route('/compare', methods=['POST'])
# @jwt_required()
def compare_issues():
    """
    Porównuje dwa zgłoszenia ze sobą
    
    Body:
        issue_id_1: ID pierwszego zgłoszenia
        issue_id_2: ID drugiego zgłoszenia
    """
    try:
        data = request.get_json()
        
        if not data or 'issue_id_1' not in data or 'issue_id_2' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Brak wymaganych pól: issue_id_1, issue_id_2'
            }), 400
        
        issue_id_1 = data['issue_id_1']
        issue_id_2 = data['issue_id_2']
        
        # Znajdź issues po ticket_number lub MongoDB ID
        issue1 = Issue.objects(ticket_number=issue_id_1).first()
        if not issue1:
            if not ObjectId.is_valid(issue_id_1):
                return jsonify({
                    'status': 'error',
                    'error': 'Nieprawidłowe ID pierwszego zgłoszenia'
                }), 400
            issue1 = Issue.objects(id=issue_id_1).first()
        
        issue2 = Issue.objects(ticket_number=issue_id_2).first()
        if not issue2:
            if not ObjectId.is_valid(issue_id_2):
                return jsonify({
                    'status': 'error',
                    'error': 'Nieprawidłowe ID drugiego zgłoszenia'
                }), 400
            issue2 = Issue.objects(id=issue_id_2).first()
        
        if not issue1 or not issue2:
            return jsonify({
                'status': 'error',
                'error': 'Jedno lub oba zgłoszenia nie zostały znalezione'
            }), 404
        
        # Oblicz podobieństwo
        detector = DuplicateDetector()
        text1 = f"{issue1.title} {issue1.description}"
        text2 = f"{issue2.title} {issue2.description}"
        
        similarity = detector.get_similarity_score(text1, text2)
        
        return jsonify({
            'status': 'success',
            'issue_1': {
                'id': str(issue1.id),
                'title': issue1.title
            },
            'issue_2': {
                'id': str(issue2.id),
                'title': issue2.title
            },
            'similarity': float(similarity),
            'similarity_percent': float(similarity * 100),
            'is_duplicate': similarity >= 0.7
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Błąd podczas porównywania: {str(e)}'
        }), 500