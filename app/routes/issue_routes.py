"""Issue routes - basic CRUD operations"""
from flask import Blueprint, jsonify, request, current_app
from app.models.issue import Issue
from app.models.user import User
from datetime import datetime
from datetime import datetime, timedelta
from mongoengine.errors import ValidationError, DoesNotExist

issue_bp = Blueprint('issues', __name__)


@issue_bp.route('/', methods=['GET'])
def get_issues():
    """Get all issues with optional filtering"""
    try:
        # Query parameters for filtering
        event_type = request.args.get('event_type')
        species = request.args.get('species')
        status = request.args.get('status')
        urgency = request.args.get('urgency')
        user_id = request.args.get('user_id')
        
        # Build query
        query = {}
        if event_type:
            query['event_type'] = event_type
        if species:
            query['species'] = species
        if status:
            query['status'] = status
        if urgency is not None:
            query['urgency'] = urgency.lower() == 'true'
        if user_id:
            query['user'] = user_id
        
        issues = Issue.objects(**query).order_by('-created_at')
        return jsonify({
            'status': 'success',
            'count': len(issues),
            'issues': [issue.to_dict() for issue in issues]
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@issue_bp.route('/<issue_id>', methods=['GET'])
def get_issue(issue_id):
    """Get single issue by ID"""
    try:
        issue = Issue.objects.get(id=issue_id)
        return jsonify({
            'status': 'success',
            'issue': issue.to_dict()
        }), 200
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Issue not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@issue_bp.route('/', methods=['POST'])
def create_issue():
    """Create new issue"""
    try:
        data = request.get_json()
        current_app.logger.info(f"Creating issue with data: {data}")
        
        # Required fields validation
        required_fields = ['event_type', 'species', 'incident_address']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create issue
        reminder_time = data.get('reminder_time')
        if reminder_time:
            reminder_time = datetime.fromisoformat(reminder_time)
        else:
            reminder_time = datetime.utcnow() + timedelta(days=7)
        
        current_app.logger.info(f"Creating Issue object...")
        issue = Issue(
            event_type=data['event_type'],
            species=data['species'],
            incident_address=data['incident_address'],
            animal_count=data.get('animal_count', 1),
            options=data.get('options', []),
            urgency=data.get('urgency', False),
            media=data.get('media', []),
            contact_phone=data.get('contact_phone'),
            description=data.get('description'),
            status=data.get('status', 'open'),
            reminder_time=reminder_time
        )
        
        current_app.logger.info(f"Saving issue...")
        issue.save()
        current_app.logger.info(f"Issue saved with ID: {issue.id}")
        
        current_app.logger.info(f"Building title...")
        issue.title = issue.build_title()
        issue.save()
        current_app.logger.info(f"Issue title: {issue.title}")
        
        # Check for duplicates asynchronously (don't block response)
        try:
            from app.utils.duplicateDetectorUltimate import check_new_issue_duplicate
            current_app.logger.info(f"Checking duplicates...")
            check_new_issue_duplicate(issue)
            current_app.logger.info(f"Duplicate check completed for issue {issue.id}")
        except Exception as e:
            # Log error but don't fail the request
            current_app.logger.error(f"Error checking duplicates for issue {issue.id}: {str(e)}")
        
        current_app.logger.info(f"Returning success response for issue {issue.id}")
        return jsonify({
            'status': 'success',
            'message': 'Issue created successfully',
            'issue': issue.to_dict()
        }), 201
        
    except ValidationError as e:
        current_app.logger.error(f"ValidationError: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f'Validation error: {str(e)}'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Exception in create_issue: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@issue_bp.route('/<issue_id>', methods=['PUT'])
def update_issue(issue_id):
    """Update issue"""
    try:
        issue = Issue.objects.get(id=issue_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'event_type' in data:
            issue.event_type = data['event_type']
        if 'species' in data:
            issue.species = data['species']
            issue.title = issue.build_title()
        if 'animal_count' in data:
            issue.animal_count = data['animal_count']
        if 'options' in data:
            issue.options = data['options']
        if 'urgency' in data:
            issue.urgency = data['urgency']
        if 'media' in data:
            issue.media = data['media']
        if 'incident_address' in data:
            issue.incident_address = data['incident_address']
        if 'contact_phone' in data:
            issue.contact_phone = data['contact_phone']
        if 'description' in data:
            issue.description = data['description']
        if 'status' in data:
            issue.status = data['status']
            if data['status'] == 'resolved':
                issue.resolved_at = datetime.utcnow()
            if 'reminder_time' in data:
                issue.reminder_time = datetime.fromisoformat(data['reminder_time'])
        if 'assigned_to' in data:
            try:
                assigned_user = User.objects.get(id=data['assigned_to'])
                issue.assigned_to = assigned_user
            except DoesNotExist:
                return jsonify({
                    'status': 'error',
                    'error': 'Assigned user not found'
                }), 404
        
        issue.updated_at = datetime.utcnow()
        issue.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Issue updated successfully',
            'issue': issue.to_dict()
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Issue not found'
        }), 404
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'error': f'Validation error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@issue_bp.route('/<issue_id>', methods=['DELETE'])
def delete_issue(issue_id):
    """Delete issue"""
    try:
        issue = Issue.objects.get(id=issue_id)
        issue.delete()
        
        return jsonify({
            'status': 'success',
            'message': 'Issue deleted successfully'
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Issue not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@issue_bp.route('/<issue_id>/merge-duplicate', methods=['POST'])
def merge_duplicate(issue_id):
    """Merge a duplicate issue with the original"""
    try:
        data = request.get_json()
        duplicate_issue_id = data.get('duplicate_issue_id')
        
        if not duplicate_issue_id:
            return jsonify({
                'status': 'error',
                'error': 'duplicate_issue_id is required'
            }), 400
        
        original = Issue.objects.get(id=issue_id)
        duplicate = Issue.objects.get(id=duplicate_issue_id)
        
        # Merge contact phone if original doesn't have one
        merged_phone = data.get('contact_phone')
        if merged_phone:
            original.contact_phone = merged_phone
        elif duplicate.contact_phone and not original.contact_phone:
            original.contact_phone = duplicate.contact_phone
        
        # Merge description if original doesn't have one
        if duplicate.description and not original.description:
            original.description = duplicate.description
        
        # Merge media
        if duplicate.media:
            if not original.media:
                original.media = []
            original.media.extend(duplicate.media)
        
        # Merge options
        if duplicate.options:
            if not original.options:
                original.options = []
            for opt in duplicate.options:
                if opt not in original.options:
                    original.options.append(opt)
        
        # Update animal count if duplicate has more
        if duplicate.animal_count and duplicate.animal_count > original.animal_count:
            original.animal_count = duplicate.animal_count
        
        original.updated_at = datetime.utcnow()
        
        # Add duplicate to original's duplicates_confirmed list
        if not original.duplicates_confirmed:
            original.duplicates_confirmed = []
        if duplicate not in original.duplicates_confirmed:
            original.duplicates_confirmed.append(duplicate)
        
        # Remove from duplicates list if present
        if original.duplicates:
            original.duplicates = [d for d in original.duplicates if str(d.id) != str(duplicate_issue_id)]
        
        original.save()
        
        # Mark duplicate as duplicate and set its duplicate_of reference
        duplicate.status = 'duplicate'
        duplicate.duplicate_of = original
        duplicate.updated_at = datetime.utcnow()
        
        # Add original to duplicate's duplicates_confirmed list (bidirectional)
        if not duplicate.duplicates_confirmed:
            duplicate.duplicates_confirmed = []
        if original not in duplicate.duplicates_confirmed:
            duplicate.duplicates_confirmed.append(original)
        
        # Remove from duplicates list if present
        if duplicate.duplicates:
            duplicate.duplicates = [d for d in duplicate.duplicates if str(d.id) != str(issue_id)]
        
        duplicate.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Issues merged successfully',
            'merged_ids': [str(original.id), str(duplicate.id)],
            'issue': original.to_dict()
        }), 200
        
    except DoesNotExist as e:
        return jsonify({
            'status': 'error',
            'error': 'Issue not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@issue_bp.route('/<issue_id>/reject-duplicate', methods=['POST'])
def reject_duplicate(issue_id):
    """Reject a duplicate relationship"""
    try:
        data = request.get_json()
        duplicate_issue_id = data.get('duplicate_issue_id')
        
        if not duplicate_issue_id:
            return jsonify({
                'status': 'error',
                'error': 'duplicate_issue_id is required'
            }), 400
        
        original = Issue.objects.get(id=issue_id)
        duplicate = Issue.objects.get(id=duplicate_issue_id)
        
        # Remove the duplicate from original's duplicates list
        if original.duplicates:
            original.duplicates = [d for d in original.duplicates if str(d.id) != str(duplicate_issue_id)]
            original.save()
        
        # Clear the duplicate_of reference from the duplicate issue
        if duplicate.duplicate_of and str(duplicate.duplicate_of.id) == str(issue_id):
            duplicate.duplicate_of = None
            # Only set to duplicate status if it was being treated as one
            if duplicate.status == 'duplicate':
                duplicate.status = 'open'
            duplicate.updated_at = datetime.utcnow()
            duplicate.save()
        
        # Also remove original from duplicate's duplicates list if it exists there (bidirectional cleanup)
        if duplicate.duplicates:
            duplicate.duplicates = [d for d in duplicate.duplicates if str(d.id) != str(issue_id)]
            duplicate.save()
        
        return jsonify({
            'status': 'success',
            'message': 'Duplicate relationship rejected',
            'rejected_ids': [str(original.id), str(duplicate.id)],
            'issue': original.to_dict()
        }), 200
        
    except DoesNotExist:
        return jsonify({
            'status': 'error',
            'error': 'Issue not found'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@issue_bp.route('/stats', methods=['GET'])
def get_issue_stats():
    """Get issue statistics"""
    try:
        total = Issue.objects.count()
        by_status = {}
        for status in ['open', 'in_progress', 'resolved', 'closed', 'duplicate']:
            by_status[status] = Issue.objects(status=status).count()
        
        by_event_type = {}
        for event_type in ['bezdomne_zwierze', 'zdarzenie_drogowe', 'znecanie_sie', 'inne']:
            by_event_type[event_type] = Issue.objects(event_type=event_type).count()
        
        urgent = Issue.objects(urgency=True).count()
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total': total,
                'by_status': by_status,
                'by_event_type': by_event_type,
                'urgent': urgent
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
