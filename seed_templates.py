#!/usr/bin/env python3
"""Quick script to seed email templates data for testing frontend.

Run this to populate your database with sample EmailCaseTypes, EmailTemplates, 
and TemplateOptions.

Usage:
    python seed_templates.py          # Add sample templates
    python seed_templates.py --clear  # Remove all templates first
"""

import argparse
import sys
from pathlib import Path

# Add backend to path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.models import EmailCaseType, EmailTemplate, TemplateOption


def clear_all_templates():
    """Remove all existing template-related data."""
    print("🗑️  Clearing all templates data...")
    TemplateOption.objects.delete()
    EmailTemplate.objects.delete()
    EmailCaseType.objects.delete()
    print("✅ Cleared!\n")


def seed_case_types():
    """Create email case types."""
    print("📋 Creating case types...")
    
    case_types_data = [
        {
            "code": "interwencja_policja",
            "label": "Interwencja policyjna",
            "description": "Pilne przypadki wymagające interwencji policji (znęcanie, niebezpieczeństwo)",
        },
        {
            "code": "interwencja_gmina",
            "label": "Interwencja gminna",
            "description": "Sprawy bezdomnych zwierząt wymagające reakcji gminy",
        },
        {
            "code": "follow_up_zglaszajacy",
            "label": "Follow-up do zgłaszającego",
            "description": "Aktualizacja statusu sprawy dla osoby zgłaszającej",
        },
        {
            "code": "informacja_edukacyjna",
            "label": "Materiał edukacyjny",
            "description": "Informacje pomocnicze dla zgłaszających",
        },
        {
            "code": "monitoring_sprawy",
            "label": "Monitoring sprawy",
            "description": "Przypomnienia i monitorowanie dalszych działań",
        },
    ]
    
    case_types = {}
    for ct_data in case_types_data:
        ct = EmailCaseType(**ct_data)
        ct.save()
        case_types[ct.code] = ct
        print(f"   ✓ {ct.label} ({ct.code})")
    
    print()
    return case_types


def seed_templates(case_types):
    """Create email templates."""
    print("📝 Creating templates...")
    
    templates_data = [
        {
            "name": "Policja - znęcanie się nad zwierzęciem",
            "title": "Pilna interwencja - podejrzenie znęcania się",
            "description": "Formalne zgłoszenie do Policji w sprawie znęcania",
            "case_type": case_types["interwencja_policja"],
            "body": """Szanowni Państwo,

Zgłaszam przypadek wymagający pilnej interwencji w sprawie {animal_type} ({case_label}).

Szczegóły zdarzenia:
{description}

Numer sprawy: {ticket_number}
Lokalizacja: {location}
Data zgłoszenia: {date}

Proszę o podjęcie odpowiednich działań zgodnie z art. 35 ustawy o ochronie zwierząt.

Z poważaniem,
System AnimalHelper""",
            "placeholders": "animal_type,case_label,description,ticket_number,location,date",
        },
        {
            "name": "Gmina - odbiór bezdomnego zwierzęcia",
            "title": "Wniosek o odbiór bezdomnego zwierzęcia",
            "description": "Wezwanie gminy do odbioru bezdomnego zwierzęcia",
            "case_type": case_types["interwencja_gmina"],
            "body": """Dzień dobry,

Zgłaszamy przypadek wymagający interwencji służb gminnych - {animal_type} ({case_label}).

Opis sytuacji:
{description}

Numer sprawy: {ticket_number}
Lokalizacja: {location}
Pilność: {urgency}

Wnosimy o niezwłoczne podjęcie działań.

Z poważaniem,
System AnimalHelper""",
            "placeholders": "animal_type,case_label,description,ticket_number,location,urgency",
        },
        {
            "name": "Follow-up - aktualizacja dla zgłaszającego",
            "title": "Aktualizacja statusu Twojej sprawy",
            "description": "Informacja zwrotna dla osoby zgłaszającej",
            "case_type": case_types["follow_up_zglaszajacy"],
            "body": """Dzień dobry,

Dziękujemy za zgłoszenie dotyczące {animal_type}.

Status sprawy {ticket_number}:
{status_update}

Podjęte działania:
{actions_taken}

W przypadku pytań lub nowych informacji, prosimy o kontakt.

Pozdrawiamy,
Zespół AnimalHelper""",
            "placeholders": "animal_type,ticket_number,status_update,actions_taken",
        },
        {
            "name": "Informacja - bezpieczne podejście do zwierzęcia",
            "title": "Jak bezpiecznie pomóc zwierzęciu?",
            "description": "Instrukcja postępowania dla zgłaszających",
            "case_type": case_types["informacja_edukacyjna"],
            "body": """Dzień dobry,

Dziękujemy za Twoją czujność i chęć pomocy zwierzęciu.

Prosimy o zachowanie ostrożności:
• Nie podchodź zbyt blisko zwierzęcia
• Nie próbuj samodzielnie łapać rannego zwierzęcia
• Zrób zdjęcie z bezpiecznej odległości
• Poczekaj na służby interwencyjne

Numer Twojej sprawy: {ticket_number}
Dalsze kroki: {next_steps}

Dziękujemy za zrozumienie,
Zespół AnimalHelper""",
            "placeholders": "ticket_number,next_steps",
        },
        {
            "name": "Monitoring - przypomnienie o sprawie",
            "title": "Przypomnienie: sprawa wymaga dalszego działania",
            "description": "Przypomnienie do jednostki odpowiedzialnej",
            "case_type": case_types["monitoring_sprawy"],
            "body": """Szanowni Państwo,

Uprzejmie przypomiamy o sprawie {ticket_number} zgłoszonej {days_ago} dni temu.

Zwierzę: {animal_type}
Status: {current_status}

Do tej pory nie otrzymaliśmy informacji zwrotnej. Prosimy o pilną reakcję.

Z poważaniem,
System AnimalHelper""",
            "placeholders": "ticket_number,days_ago,animal_type,current_status",
        },
    ]
    
    for tmpl_data in templates_data:
        tmpl = EmailTemplate(
            name=tmpl_data["name"],
            title=tmpl_data["title"],
            description=tmpl_data["description"],
            body=tmpl_data["body"],
            placeholders=tmpl_data["placeholders"],
            case_type=tmpl_data["case_type"],
            is_active=True,
        )
        tmpl.save()
        print(f"   ✓ {tmpl.name}")
    
    print()


def seed_template_options(case_types):
    """Create template options for quick selection."""
    print("🎯 Creating template options...")
    
    options_data = [
        # Interwencja policyjna
        {
            "case_type_ref": case_types["interwencja_policja"],
            "animal_type": "pies",
            "case_type": "znęcanie",
            "case_label": "Pies bez opieki w skrajnych warunkach",
            "description": "Pies trzymany na krótkim łańcuchu bez dostępu do wody i schronienia przed pogodą.",
        },
        {
            "case_type_ref": case_types["interwencja_policja"],
            "animal_type": "kot",
            "case_type": "znęcanie",
            "case_label": "Kot zamknięty bez opieki",
            "description": "Kot zamknięty w mieszkaniu bez dostępu do wody i pokarmu od kilku dni.",
        },
        {
            "case_type_ref": case_types["interwencja_policja"],
            "animal_type": "koń",
            "case_type": "zaniedbanie",
            "case_label": "Koń w stanie skrajnego wycieńczenia",
            "description": "Koń wyraźnie niedożywiony, brak opieki weterynaryjnej, zaniedbany.",
        },
        
        # Interwencja gminna
        {
            "case_type_ref": case_types["interwencja_gmina"],
            "animal_type": "pies",
            "case_type": "bezdomny",
            "case_label": "Bezdomny pies przy ruchliwej drodze",
            "description": "Pies bez opieki poruszający się przy drodze krajowej, zagrożenie dla ruchu.",
        },
        {
            "case_type_ref": case_types["interwencja_gmina"],
            "animal_type": "kot",
            "case_type": "kolonia",
            "case_label": "Kolonia kotów wymagająca sterylizacji",
            "description": "Duża grupa bezdomnych kotów, konieczność programu TNR (trap-neuter-return).",
        },
        {
            "case_type_ref": case_types["interwencja_gmina"],
            "animal_type": "pies",
            "case_type": "agresywny",
            "case_label": "Pies swobodnie poruszający się, zachowanie agresywne",
            "description": "Pies bez właściciela manifestujący agresję wobec przechodniów.",
        },
        
        # Follow-up
        {
            "case_type_ref": case_types["follow_up_zglaszajacy"],
            "animal_type": "pies",
            "case_type": "pomoc_udzielona",
            "case_label": "Sprawa rozwiązana - pies bezpieczny",
            "description": "Pies odebrany przez schronisko, otrzymał opiekę weterynaryjną.",
        },
        {
            "case_type_ref": case_types["follow_up_zglaszajacy"],
            "animal_type": "kot",
            "case_type": "w_trakcie",
            "case_label": "Sprawa w toku - czekamy na reakcję",
            "description": "Zgłoszenie przekazane do odpowiednich służb, monitoring sprawy.",
        },
        
        # Edukacyjne
        {
            "case_type_ref": case_types["informacja_edukacyjna"],
            "animal_type": "jeż",
            "case_type": "dzika_fauna",
            "case_label": "Jak pomóc dzikiemu zwierzęciu",
            "description": "Instrukcja dotycząca pomocy zwierzętom dzikim (jeże, ptaki, itp.).",
        },
    ]
    
    for opt_data in options_data:
        opt = TemplateOption(**opt_data)
        opt.save()
        print(f"   ✓ {opt.animal_type} - {opt.case_label}")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="Seed email templates for testing")
    parser.add_argument("--clear", action="store_true", help="Clear all templates before seeding")
    args = parser.parse_args()
    
    print("\n🚀 Starting template seeding...\n")
    
    # Initialize Flask app
    app, _ = create_app()
    with app.app_context():
        if args.clear:
            clear_all_templates()
        
        # Check if data already exists
        existing_count = EmailCaseType.objects.count()
        if existing_count > 0 and not args.clear:
            print(f"⚠️  Found {existing_count} existing case types.")
            response = input("Do you want to add more templates anyway? (y/n): ")
            if response.lower() != 'y':
                print("❌ Cancelled. Use --clear flag to remove existing data first.")
                return
        
        # Seed data
        case_types = seed_case_types()
        seed_templates(case_types)
        seed_template_options(case_types)
        
        # Summary
        print("=" * 50)
        print("✅ Seeding complete!\n")
        print(f"   Case Types: {EmailCaseType.objects.count()}")
        print(f"   Templates: {EmailTemplate.objects.count()}")
        print(f"   Template Options: {TemplateOption.objects.count()}")
        print("=" * 50)
        print("\n💡 Your frontend can now fetch templates from:")
        print("   GET http://localhost:5000/api/email-templates")
        print("   GET http://localhost:5000/api/email-case-types")
        print("   GET http://localhost:5000/api/template-options\n")


if __name__ == "__main__":
    main()
