from datetime import datetime, timedelta
from app.models.issue import Issue
from app.utils.distanceCalculator import calculate_distance, validate_address_format
from app.utils.duplicate_detector import DuplicateDetector
from flask import current_app

def check_new_issue_duplicate(new_issue):
    """
    Check if new issue is a duplicate of existing issues.
    Uses:
    1. Address validation (city-street-number format)
    2. Distance (1km radius) + species match
    3. Description text similarity (0.7 threshold)
    
    Returns early without marking duplicates if address is invalid.
    """
    try:
        # 0. VALIDATE ADDRESS FORMAT FIRST
        new_address = getattr(new_issue, 'incident_address', None)
        if new_address:
            is_valid, parts = validate_address_format(str(new_address))
            if not is_valid:
                current_app.logger.warning(
                    f"New issue {new_issue.id} has invalid address format: '{new_address}'. "
                    f"Skipping duplicate detection."
                )
                return  # Don't run duplicate detection if address is invalid
        else:
            current_app.logger.warning(
                f"New issue {new_issue.id} has no address. Skipping duplicate detection."
            )
            return
        
        # 1. Get open issues from last 7 days
        date_threshold = datetime.utcnow() - timedelta(days=7)
        recent_open_issues = Issue.objects(
            created_at__gte=date_threshold,
            status='open',
            id__ne=new_issue.id
        )

        # 2. Check distance (limit=1km) and species
        close_species_issues = []
        
        for issue in recent_open_issues:
            try:
                # Validate existing issue address too
                existing_address = getattr(issue, 'incident_address', None)
                if not existing_address:
                    continue
                
                is_valid_existing, _ = validate_address_format(str(existing_address))
                if not is_valid_existing:
                    current_app.logger.warning(
                        f"Existing issue {issue.id} has invalid address: '{existing_address}'. "
                        f"Skipping its comparison."
                    )
                    continue
                
                # Both issues must have addresses
                if not hasattr(issue, 'incident_address') or not hasattr(new_issue, 'incident_address'):
                    continue
                
                loc1 = getattr(issue, 'incident_address', None)
                loc2 = getattr(new_issue, 'incident_address', None)
                
                if not loc1 or not loc2:
                    continue
                
                # Support both formats:
                # - dict with 'x', 'y' (coordinates)
                # - string (address text)
                
                # Normalize to dict format
                loc1_dict = loc1 if isinstance(loc1, dict) else {'address': str(loc1)}
                loc2_dict = loc2 if isinstance(loc2, dict) else {'address': str(loc2)}
                
                distance, conf1, conf2 = calculate_distance(loc1_dict, loc2_dict)
                
                # IMPORTANT: Only consider it a match if BOTH addresses have full street+number accuracy
                # Skip if either address fell back to city-only or partial matching
                if conf1 not in ['coordinates', 'full'] or conf2 not in ['coordinates', 'full']:
                    current_app.logger.warning(
                        f"Issue {issue.id}: Address confidence too low (conf1={conf1}, conf2={conf2}). "
                        f"Not reliable for duplicate detection. Skipping."
                    )
                    continue
                
                # Check if within 1km and same species
                if distance <= 1.0 and issue.species == new_issue.species:
                    close_species_issues.append(issue)
                    current_app.logger.info(
                        f"Found close issue {issue.id} at distance {distance:.2f}km "
                        f"(conf1={conf1}, conf2={conf2})"
                    )
                    
            except Exception as e:
                current_app.logger.warning(
                    f"Error calculating distance for issue {issue.id}: {str(e)}"
                )
                continue

        # 3. Check similarity (threshold=0.7)
        detector = DuplicateDetector(similarity_threshold=0.7)
        duplicates = []
        
        for issue in close_species_issues:
            try:
                similarity = detector.get_similarity_score(
                    f"{new_issue.description or ''}",
                    f"{issue.description or ''}"
                )
                print(f"Similarity of new issue with issue {issue.id}: {similarity:.2f}")
                if similarity >= 0.7:
                    duplicates.append(issue)
                    current_app.logger.info(
                        f"Found duplicate {issue.id} with similarity {similarity:.2f}"
                    )
            except Exception as e:
                current_app.logger.warning(
                    f"Error calculating similarity for issue {issue.id}: {str(e)}"
                )
                continue

        # Update new issue with duplicates
        if duplicates:
            new_issue.duplicates = duplicates
            new_issue.save()
            current_app.logger.info(f"Found {len(duplicates)} duplicates for {new_issue.id}")

            # Update each duplicate issue to include new issue
            for duplicate_issue in duplicates:
                try:
                    if new_issue not in duplicate_issue.duplicates:
                        duplicate_issue.duplicates.append(new_issue)
                        duplicate_issue.save()
                except Exception as e:
                    current_app.logger.error(
                        f"Error updating duplicate issue {duplicate_issue.id}: {str(e)}"
                    )
                    
    except Exception as e:
        current_app.logger.error(f"Error in check_new_issue_duplicate: {str(e)}")
        raise