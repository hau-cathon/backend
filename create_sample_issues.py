#!/usr/bin/env python3
"""Create sample issues for testing duplicate detection"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.models import Issue

def create_sample_issues(clear=False):
    """Create sample issues with similar descriptions to test duplicate detection"""
    
    app, _ = create_app()
    with app.app_context():
        print("\n🐕 Creating sample issues for duplicate detection testing...\n")
        
        # Clear existing issues if requested
        existing = Issue.objects.count()
        if existing > 0 and clear:
            Issue.objects.delete()
            print(f"✅ Cleared {existing} existing issues\n")
        elif existing > 0:
            print(f"ℹ️  Found {existing} existing issues (use --clear to remove them)\n")
        
        now = datetime.utcnow()
        
        # Issue 1: Bezdomny pies przy drodze
        issue1 = Issue(
            title="#AH-TEST-001",
            event_type="bezdomne_zwierze",
            species="pies",
            animal_count=1,
            options=["przy drodze", "bez obrozy"],
            urgency=True,
            incident_address="ul. Polna 15, Warszawa",
            contact_phone="501234567",
            description="Bezdomny pies przy ruchliwej drodze krajowej. Zwierzę bez obroży, wygląda na zagubione. Zagrożenie dla ruchu drogowego.",
            status="open",
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(hours=2)
        )
        issue1.save()
        print(f"✓ Created: {issue1.title} - Bezdomny pies przy drodze")
        
        # Issue 2: Similar - Bezdomny pies (should be detected as duplicate)
        issue2 = Issue(
            title="#AH-TEST-002",
            event_type="bezdomne_zwierze",
            species="pies",
            animal_count=1,
            options=["przy ulicy", "bez obrozy"],
            urgency=True,
            incident_address="ul. Polna 18, Warszawa",
            contact_phone="502345678",
            description="Pies bez właściciela przy ruchliwej ulicy. Nie ma obroży, prawdopodobnie zagubiony. Stanowi zagrożenie w ruchu.",
            status="open",
            created_at=now - timedelta(hours=1),
            updated_at=now - timedelta(hours=1)
        )
        issue2.save()
        print(f"✓ Created: {issue2.title} - Bezdomny pies (DUPLICATE)")
        
        # Issue 3: Kot zamknięty na balkonie
        issue3 = Issue(
            title="#AH-TEST-003",
            event_type="znecanie_sie",
            species="kot",
            animal_count=1,
            options=["balkon", "brak wody"],
            urgency=False,
            incident_address="ul. Kwiatowa 7/12, Kraków",
            contact_phone="503456789",
            description="Kot zamknięty na balkonie bez dostępu do wody i jedzenia. Widoczny od kilku dni, właściciel nieobecny.",
            status="open",
            created_at=now - timedelta(hours=5),
            updated_at=now - timedelta(hours=5)
        )
        issue3.save()
        print(f"✓ Created: {issue3.title} - Kot zamknięty na balkonie")
        
        # Issue 4: Similar kot (should be detected as duplicate)
        issue4 = Issue(
            title="#AH-TEST-004",
            event_type="znecanie_sie",
            species="kot",
            animal_count=1,
            options=["balkon", "brak opieki"],
            urgency=False,
            incident_address="ul. Kwiatowa 7/14, Kraków",
            contact_phone="504567890",
            description="Kot porzucony na balkonie, brak dostępu do pokarmu i wody. Od wielu dni bez opieki, sąsiad wyjechał.",
            status="open",
            created_at=now - timedelta(hours=3),
            updated_at=now - timedelta(hours=3)
        )
        issue4.save()
        print(f"✓ Created: {issue4.title} - Kot porzucony (DUPLICATE)")
        
        # Issue 5: Potrącony pies (different, not a duplicate)
        issue5 = Issue(
            title="#AH-TEST-005",
            event_type="zdarzenie_drogowe",
            species="pies",
            animal_count=1,
            options=["potrącenie", "ranny"],
            urgency=True,
            incident_address="ul. Słoneczna 42, Gdańsk",
            contact_phone="505678901",
            description="Pies potrącony przez samochód, leży przy drodze. Wymaga pilnej pomocy weterynaryjnej, widoczne obrażenia.",
            status="in_progress",
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(hours=12)
        )
        issue5.save()
        print(f"✓ Created: {issue5.title} - Potrącony pies")
        
        # Issue 6: Konia w złym stanie
        issue6 = Issue(
            title="#AH-TEST-006",
            event_type="znecanie_sie",
            species="koń",
            animal_count=1,
            options=["wychudzony", "brak opieki"],
            urgency=True,
            incident_address="Wieś Polanka 15, pow. warszawski",
            contact_phone="506789012",
            description="Koń w stanie skrajnego wycieńczenia, brak opieki weterynaryjnej. Widoczne zaniedbanie przez właściciela.",
            status="open",
            created_at=now - timedelta(hours=8),
            updated_at=now - timedelta(hours=8)
        )
        issue6.save()
        print(f"✓ Created: {issue6.title} - Koń zaniedbany")
        
        print("\n" + "=" * 60)
        print(f"✅ Created {Issue.objects.count()} sample issues")
        print("=" * 60)
        print("\n💡 Test duplicate detection with:")
        print(f"   Issue 1 vs Issue 2: High similarity (same location, bezdomny pies)")
        print(f"   Issue 3 vs Issue 4: High similarity (same building, kot na balkonie)")
        print(f"   Issue 5: Different (potrącenie)")
        print(f"   Issue 6: Different (koń)")
        print("\n🔗 API endpoint: GET /api/duplicates/check/<issue_id>")
        print(f"   Example: http://localhost:5000/api/duplicates/check/{issue1.id}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create sample issues for duplicate detection testing")
    parser.add_argument("--clear", action="store_true", help="Clear existing issues before creating new ones")
    args = parser.parse_args()
    
    create_sample_issues(clear=args.clear)
