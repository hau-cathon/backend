
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.issue import Issue
from app.models.issue_duplicate import IssueDuplicate
from app.models.user import User
from app.services.issue_duplicate_service import IssueDuplicateService

issue_duplicate_bp = Blueprint('issue_duplicates', __name__)


@issue_duplicate_bp.route('/issues/<issue_id>/duplicates', methods=['POST'])
@jwt_required()
def mark_duplicate(issue_id):
    try:
        data = request.get_json()
        duplicate_issue_id = data.get('duplicate_issue_id')

        if not duplicate_issue_id:
            return jsonify({'error': 'duplicate_issue_id is required'}), 400

        original = Issue.objects.get(id=issue_id)
        duplicate = Issue.objects.get(id=duplicate_issue_id)

        existing = IssueDuplicate.objects(
            original_issue_id=original.id,
            duplicate_issue_id=duplicate.id
        ).first()
        if existing:
            return jsonify({'error': 'Already marked as duplicate'}), 409

        duplicate_record = IssueDuplicateService.mark_as_duplicate(issue_id, duplicate_issue_id)

        return jsonify({
            'message': 'Issue marked as duplicate (pending)',
            'duplicate': duplicate_record.to_dict()
        }), 201

    except Issue.DoesNotExist:
        return jsonify({'error': 'Issue not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@issue_duplicate_bp.route('/duplicates/<duplicate_id>/merge', methods=['POST'])
@jwt_required()
def merge_duplicate(duplicate_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        fields_to_merge = data.get('fields', ['description', 'contact_phone', 'media'])

        duplicate_record = IssueDuplicateService.merge_duplicates(
            duplicate_id,
            current_user_id,
            fields_to_merge
        )

        return jsonify({
            'message': 'Issues merged successfully',
            'duplicate': duplicate_record.to_dict()
        }), 200

    except IssueDuplicate.DoesNotExist:
        return jsonify({'error': 'Duplicate record not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@issue_duplicate_bp.route('/duplicates/<duplicate_id>/reject', methods=['POST'])
@jwt_required()
def reject_duplicate(duplicate_id):
    try:
        data = request.get_json() or {}
        reason = data.get('reason')

        duplicate_record = IssueDuplicateService.reject_duplicate(duplicate_id, reason)

        return jsonify({
            'message': 'Duplicate relationship rejected',
            'duplicate': duplicate_record.to_dict()
        }), 200

    except IssueDuplicate.DoesNotExist:
        return jsonify({'error': 'Duplicate record not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@issue_duplicate_bp.route('/issues/<issue_id>/duplicates', methods=['GET'])
@jwt_required()
def get_issue_duplicates(issue_id):
    try:
        Issue.objects.get(id=issue_id)

        duplicates = IssueDuplicateService.get_duplicates_for_issue(issue_id)

        return jsonify({
            'issue_id': issue_id,
            'duplicates': [dup.to_dict() for dup in duplicates]
        }), 200

    except Issue.DoesNotExist:
        return jsonify({'error': 'Issue not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@issue_duplicate_bp.route('/duplicates/pending', methods=['GET'])
@jwt_required()
def get_pending_duplicates():
    try:
        duplicates = IssueDuplicateService.get_pending_duplicates()

        return jsonify({
            'count': len(duplicates),
            'duplicates': [dup.to_dict() for dup in duplicates]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
