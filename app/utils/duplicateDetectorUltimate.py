from datetime import datetime, timedelta
from app.models.issue import Issue
from app.utils.distanceCalculator import calculate_distance
from app.utils.duplicate_detector import DuplicateDetector

def check_new_issue_duplicate(new_issue):
    # 1. Pobierz zgłoszenia z ostatnich 7 dni ze statusem 'open'
    date_threshold = datetime.utcnow() - timedelta(days=7)
    recent_open_issues = Issue.objects(
        created_at__gte=date_threshold,
        status='open',
        id__ne=new_issue.id
    )

    # 2. Sprawdź dystans (limit=1km) i species
    close_species_issues = []
    for issue in recent_open_issues:
        if hasattr(issue, 'incident_address') and hasattr(new_issue, 'incident_address'):
            # Zakładamy, że incident_address zawiera współrzędne x/y
            loc1 = getattr(issue, 'incident_address', None)
            loc2 = getattr(new_issue, 'incident_address', None)
            # loc1 i loc2 muszą być dict z x/y
            if isinstance(loc1, dict) and isinstance(loc2, dict):
                distance = calculate_distance(loc1, loc2)
                if distance <= 1 and issue.species == new_issue.species:
                    close_species_issues.append(issue)

    # 3. Sprawdź duplicate_detector (threshold=0.7)
    detector = DuplicateDetector(similarity_threshold=0.7)
    duplicates = []
    for issue in close_species_issues:
        similarity = detector.get_similarity_score(
            f"{new_issue.description}",
            f"{issue.description}"
        )
        if similarity >= 0.7:
            duplicates.append(issue)

    new_issue.duplicates = duplicates
    new_issue.save()