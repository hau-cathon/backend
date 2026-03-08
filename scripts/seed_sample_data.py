#!/usr/bin/env python3
"""Seed sample data for local development.

This script inserts realistic demo data used by the frontend:
- issues
- action history
- email history
- email case types
- email templates
- template options
- users and roles

It is idempotent for seeded records: rerunning updates/recreates only records
owned by this seed script.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from mongoengine.queryset.visitor import Q


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app  # noqa: E402
from app.models import (  # noqa: E402
    ActionHistoryEntry,
    EmailCaseType,
    EmailMessage,
    EmailTemplate,
    Issue,
    IssueDuplicate,
    Role,
    TemplateOption,
    User,
)

SEED_SOURCE = "seed_sample_data"
SEED_TICKETS = [
    "#AH-SEED-2001",
    "#AH-SEED-2002",
    "#AH-SEED-2003",
    "#AH-SEED-2004",
    "#AH-SEED-2005",
]
SEED_USER_EMAILS = [
    "anna.kowalska@animalhelper.local",
    "piotr.wisniewski@animalhelper.local",
    "marek.zielinski@animalhelper.local",
]
SEED_CASE_CODES = [
    "interwencja_policja",
    "interwencja_gmina",
    "follow_up_zglaszajacy",
]


def _print(msg: str) -> None:
    print(f"[seed] {msg}")


def remove_existing_seed_data() -> None:
    """Remove previously seeded records while leaving non-seed data intact."""
    _print("Removing previous seed records...")

    existing_seed_issues = list(Issue.objects(title__in=SEED_TICKETS))
    if existing_seed_issues:
        issue_ids = [issue.id for issue in existing_seed_issues]

        IssueDuplicate.objects(
            Q(original_issue__in=issue_ids) | Q(duplicate_issue__in=issue_ids)
        ).delete()

        ActionHistoryEntry.objects(Q(issue__in=issue_ids) | Q(ticket_id__in=SEED_TICKETS)).delete()
        EmailMessage.objects(Q(issue__in=issue_ids) | Q(ticket_id__in=SEED_TICKETS)).delete()
        Issue.objects(id__in=issue_ids).delete()

    EmailTemplate.objects(name__startswith="SEED:").delete()
    TemplateOption.objects(description__contains="[SEED]").delete()

    seed_case_types = list(EmailCaseType.objects(code__in=SEED_CASE_CODES))
    if seed_case_types:
        case_type_ids = [case_type.id for case_type in seed_case_types]
        EmailTemplate.objects(case_type__in=case_type_ids).delete()
        TemplateOption.objects(case_type_ref__in=case_type_ids).delete()
        EmailCaseType.objects(id__in=case_type_ids).delete()

    User.objects(email__in=SEED_USER_EMAILS).delete()
    Role.objects(name__in=["SUPERUSER", "PRODUCER", "DISPATCHER"]).delete()


def clear_all_domain_data() -> None:
    """Hard reset for development only."""
    _print("Clearing all domain collections...")
    IssueDuplicate.objects.delete()
    ActionHistoryEntry.objects.delete()
    EmailMessage.objects.delete()
    Issue.objects.delete()
    TemplateOption.objects.delete()
    EmailTemplate.objects.delete()
    EmailCaseType.objects.delete()
    User.objects.delete()
    Role.objects.delete()


def seed_roles() -> None:
    roles = [
        {"name": "SUPERUSER", "description": "Full platform access"},
        {"name": "PRODUCER", "description": "Handles assigned cases"},
        {"name": "DISPATCHER", "description": "Coordinates field response"},
    ]

    for role_data in roles:
        role = Role(**role_data)
        role.save()


def seed_users() -> dict[str, User]:
    users_data = [
        {
            "email": "anna.kowalska@animalhelper.local",
            "username": "anna_k",
            "password": "seed-password-123",
        },
        {
            "email": "piotr.wisniewski@animalhelper.local",
            "username": "piotr_w",
            "password": "seed-password-123",
        },
        {
            "email": "marek.zielinski@animalhelper.local",
            "username": "marek_z",
            "password": "seed-password-123",
        },
    ]

    users: dict[str, User] = {}
    for user_data in users_data:
        user = User(email=user_data["email"], username=user_data["username"])
        user.set_password(user_data["password"])
        user.save()
        users[user.username] = user

    return users


def seed_email_case_types() -> dict[str, EmailCaseType]:
    case_types_data = [
        {
            "code": "interwencja_policja",
            "label": "Interwencja policyjna",
            "description": "Pilne przypadki wymagajace interwencji policji",
        },
        {
            "code": "interwencja_gmina",
            "label": "Interwencja gminna",
            "description": "Sprawy bezdomnych zwierzat i odbioru przez gmine",
        },
        {
            "code": "follow_up_zglaszajacy",
            "label": "Follow-up do zglaszajacego",
            "description": "Aktualizacja statusu dla osoby zglaszajacej",
        },
    ]

    case_types: dict[str, EmailCaseType] = {}
    for case_type_data in case_types_data:
        case_type = EmailCaseType(**case_type_data)
        case_type.save()
        case_types[case_type.code] = case_type

    return case_types


def seed_email_templates(case_types: dict[str, EmailCaseType]) -> None:
    templates_data = [
        {
            "name": "SEED: Policja - znecanie",
            "title": "Pilna interwencja - podejrzenie znecania",
            "description": "Powiadomienie dla Policji",
            "case_type": case_types["interwencja_policja"],
            "body": (
                "Dzien dobry,\n\n"
                "Prosimy o pilna interwencje w sprawie {animal_type} ({case_label}).\n"
                "Opis: {description}\n\n"
                "Numer sprawy: {number}\n"
                "Adres: {location}\n"
            ),
            "placeholders": "animal_type,case_label,description,number,location",
        },
        {
            "name": "SEED: Gmina - odbior zwierzecia",
            "title": "Wniosek o odbior bezdomnego zwierzecia",
            "description": "Powiadomienie dla gminy",
            "case_type": case_types["interwencja_gmina"],
            "body": (
                "Dzien dobry,\n\n"
                "Wnosimy o odbior zwierzecia: {animal_type} ({case_type}).\n"
                "Szczegoly: {description}\n\n"
                "Numer sprawy: {number}\n"
            ),
            "placeholders": "animal_type,case_type,description,number",
        },
        {
            "name": "SEED: Follow-up - zglaszajacy",
            "title": "Aktualizacja statusu sprawy {number}",
            "description": "Status sprawy dla zglaszajacego",
            "case_type": case_types["follow_up_zglaszajacy"],
            "body": (
                "Dzien dobry,\n\n"
                "Dziekujemy za zgloszenie dotyczace {animal_type}.\n"
                "Aktualny status sprawy {number}: w trakcie realizacji.\n"
            ),
            "placeholders": "animal_type,number",
        },
    ]

    for template_data in templates_data:
        template = EmailTemplate(
            name=template_data["name"],
            title=template_data["title"],
            description=template_data["description"],
            body=template_data["body"],
            placeholders=template_data["placeholders"],
            case_type=template_data["case_type"],
            is_active=True,
        )
        template.save()


def seed_template_options(case_types: dict[str, EmailCaseType]) -> None:
    options_data = [
        {
            "case_type_ref": case_types["interwencja_policja"],
            "animal_type": "kot",
            "case_type": "znecanie",
            "case_label": "Kot zamkniety bez opieki",
            "description": "[SEED] Kot bez dostepu do wody i pozywienia od kilku dni.",
        },
        {
            "case_type_ref": case_types["interwencja_gmina"],
            "animal_type": "pies",
            "case_type": "bezdomny",
            "case_label": "Bezdomny pies przy ruchliwej drodze",
            "description": "[SEED] Zwierze bez opiekuna, zagrozenie ruchem drogowym.",
        },
        {
            "case_type_ref": case_types["follow_up_zglaszajacy"],
            "animal_type": "bocian",
            "case_type": "ranny",
            "case_label": "Ranny bocian przekazany rehabilitatorowi",
            "description": "[SEED] Sprawa po interwencji, oczekiwanie na informacje zwrotna.",
        },
    ]

    for option_data in options_data:
        option = TemplateOption(**option_data)
        option.save()


def seed_issues(users: dict[str, User]) -> dict[str, Issue]:
    now = datetime.utcnow()
    issues_data = [
        {
            "title": "#AH-SEED-2001",
            "event_type": "zdarzenie_drogowe",
            "species": "pies",
            "animal_count": 1,
            "options": ["asfalt", "ruchliwa ulica"],
            "urgency": True,
            "incident_address": "ul. Kwiatowa 12, Warszawa",
            "contact_phone": "501111222",
            "description": "Pies potracony przez samochod, potrzebna pilna pomoc weterynaryjna.",
            "status": "in_progress",
            "assigned_to": users["anna_k"],
            "created_at": now - timedelta(hours=18),
            "updated_at": now - timedelta(hours=2),
        },
        {
            "title": "#AH-SEED-2002",
            "event_type": "znecanie_sie",
            "species": "kot",
            "animal_count": 1,
            "options": ["balkon", "brak wody"],
            "urgency": False,
            "incident_address": "ul. Rozana 7/4, Krakow",
            "contact_phone": "502222333",
            "description": "Kot zamkniety na balkonie bez opieki od dluzszego czasu.",
            "status": "open",
            "assigned_to": users["piotr_w"],
            "created_at": now - timedelta(hours=26),
            "updated_at": now - timedelta(hours=5),
        },
        {
            "title": "#AH-SEED-2003",
            "event_type": "inne",
            "species": "bocian",
            "animal_count": 1,
            "options": ["skrzydlo", "rehabilitator"],
            "urgency": False,
            "incident_address": "Okolice Lowicza, droga K-702",
            "contact_phone": "503333444",
            "description": "Ranny bocian po kolizji z linia energetyczna.",
            "status": "resolved",
            "assigned_to": users["anna_k"],
            "created_at": now - timedelta(days=2, hours=3),
            "updated_at": now - timedelta(days=1, hours=4),
            "resolved_at": now - timedelta(days=1, hours=6),
        },
        {
            "title": "#AH-SEED-2004",
            "event_type": "bezdomne_zwierze",
            "species": "pies",
            "animal_count": 1,
            "options": ["duplikat", "to samo miejsce"],
            "urgency": False,
            "incident_address": "ul. Kwiatowa 12, Warszawa",
            "contact_phone": "504444555",
            "description": "Mozliwy duplikat zgloszenia dotyczacego potraconego psa.",
            "status": "duplicate",
            "assigned_to": users["marek_z"],
            "created_at": now - timedelta(hours=14),
            "updated_at": now - timedelta(hours=12),
        },
        {
            "title": "#AH-SEED-2005",
            "event_type": "bezdomne_zwierze",
            "species": "kot",
            "animal_count": 2,
            "options": ["schronisko", "odbior"],
            "urgency": False,
            "incident_address": "ul. Lesna 2, Poznan",
            "contact_phone": "505555666",
            "description": "Dwa bezdomne koty wymagaja odbioru i transportu do schroniska.",
            "status": "closed",
            "assigned_to": users["piotr_w"],
            "created_at": now - timedelta(days=3),
            "updated_at": now - timedelta(days=1, hours=2),
            "resolved_at": now - timedelta(days=1, hours=3),
        },
    ]

    issues: dict[str, Issue] = {}
    for issue_data in issues_data:
        issue = Issue(
            title=issue_data["title"],
            event_type=issue_data["event_type"],
            species=issue_data["species"],
            animal_count=issue_data["animal_count"],
            options=issue_data["options"],
            urgency=issue_data["urgency"],
            media=[],
            incident_address=issue_data["incident_address"],
            contact_phone=issue_data["contact_phone"],
            description=issue_data["description"],
            status=issue_data["status"],
            assigned_to=issue_data["assigned_to"],
            created_at=issue_data["created_at"],
            updated_at=issue_data["updated_at"],
            resolved_at=issue_data.get("resolved_at"),
            reminder_time=now + timedelta(days=2),
        )
        issue.save()
        issues[issue.title] = issue

    # Duplicate relation: #AH-SEED-2004 is duplicate of #AH-SEED-2001
    original = issues["#AH-SEED-2001"]
    duplicate = issues["#AH-SEED-2004"]
    duplicate.duplicate_of = original
    duplicate.save()

    original.duplicates = [duplicate]
    original.save()

    IssueDuplicate(
        original_issue=original,
        duplicate_issue=duplicate,
        status="merged",
        merged_fields=["description", "contact_phone"],
        merged_by=users["anna_k"],
        created_at=now - timedelta(hours=10),
        merged_at=now - timedelta(hours=9, minutes=30),
    ).save()

    return issues


def seed_action_history(issues: dict[str, Issue]) -> None:
    now = datetime.utcnow()

    def add(
        ticket: str,
        action_type: str,
        label: str,
        detail: str,
        timeline_type: str,
        hours_ago: float,
    ) -> None:
        issue = issues[ticket]
        ActionHistoryEntry(
            ticket_id=ticket,
            issue=issue,
            action_type=action_type,
            label=label,
            detail=detail,
            timeline_type=timeline_type,
            source=SEED_SOURCE,
            created_at=now - timedelta(hours=hours_ago),
            metadata={"seed": True},
        ).save()

    add("#AH-SEED-2001", "issue_created", "Utworzono zgloszenie", "Nowe zgloszenie drogowe zostalo zapisane.", "info", 18)
    add("#AH-SEED-2001", "email_sent", "Wyslano wiadomosc email", "Do: patrol@wet.local | Temat: Pilna interwencja", "success", 17.5)
    add("#AH-SEED-2001", "status_changed", "Zmieniono status zgloszenia", "Nowy status: in_progress", "warning", 16)

    add("#AH-SEED-2002", "issue_created", "Utworzono zgloszenie", "Sprawa dotyczaca podejrzenia znecania.", "info", 26)
    add("#AH-SEED-2002", "note_added", "Dodano notatke operatora", "Oczekiwanie na kontakt z administracja budynku.", "info", 22)

    add("#AH-SEED-2003", "issue_created", "Utworzono zgloszenie", "Sprawa rannego bociana.", "info", 51)
    add("#AH-SEED-2003", "status_changed", "Zmieniono status zgloszenia", "Nowy status: resolved", "success", 30)

    add("#AH-SEED-2004", "duplicate_detected", "Wykryto duplikat", "Sprawa zostala powiazana z #AH-SEED-2001.", "warning", 13)
    add("#AH-SEED-2004", "duplicate_merged", "Polaczono duplikat", "Scalono duplikat z oryginalem.", "success", 9.5)

    add("#AH-SEED-2005", "issue_created", "Utworzono zgloszenie", "Sprawa bezdomnych kotow przekazana do gminy.", "info", 72)
    add("#AH-SEED-2005", "status_changed", "Zmieniono status zgloszenia", "Nowy status: closed", "success", 27)


def seed_email_history(issues: dict[str, Issue]) -> None:
    now = datetime.utcnow()

    emails = [
        {
            "ticket_id": "#AH-SEED-2001",
            "issue": issues["#AH-SEED-2001"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "patrol@wet.local",
            "subject": "Pilna interwencja #AH-SEED-2001",
            "body": "Prosimy o pilny przyjazd na miejsce zdarzenia.",
            "created_at": now - timedelta(hours=17, minutes=45),
        },
        {
            "ticket_id": "#AH-SEED-2001",
            "issue": issues["#AH-SEED-2001"],
            "direction": "inbound",
            "from_email": "patrol@wet.local",
            "to_email": "noreply@animalhelper.local",
            "subject": "Re: Pilna interwencja #AH-SEED-2001",
            "body": "Potwierdzamy przyjecie. Zespol bedzie za 20 minut.",
            "created_at": now - timedelta(hours=17, minutes=10),
        },
        {
            "ticket_id": "#AH-SEED-2002",
            "issue": issues["#AH-SEED-2002"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "piw@krakow.local",
            "subject": "Prosba o interwencje #AH-SEED-2002",
            "body": "Przesylamy zgloszenie podejrzenia znecania nad zwierzeciem.",
            "created_at": now - timedelta(hours=21),
        },
    ]

    for email_data in emails:
        EmailMessage(
            ticket_id=email_data["ticket_id"],
            issue=email_data["issue"],
            direction=email_data["direction"],
            from_email=email_data["from_email"],
            to_email=email_data["to_email"],
            subject=email_data["subject"],
            body=email_data["body"],
            is_automated=False,
            metadata={"seed": True},
            created_at=email_data["created_at"],
        ).save()


def run_seed(clear_all: bool) -> None:
    if clear_all:
        clear_all_domain_data()
    else:
        remove_existing_seed_data()

    seed_roles()
    users = seed_users()
    case_types = seed_email_case_types()
    seed_email_templates(case_types)
    seed_template_options(case_types)
    issues = seed_issues(users)
    seed_action_history(issues)
    seed_email_history(issues)

    _print("Seed completed successfully.")
    _print(f"Issues: {Issue.objects.count()}")
    _print(f"Action history entries: {ActionHistoryEntry.objects.count()}")
    _print(f"Email messages: {EmailMessage.objects.count()}")
    _print(f"Email templates: {EmailTemplate.objects.count()}")
    _print(f"Template options: {TemplateOption.objects.count()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed sample data into MongoDB")
    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Delete all domain records before seeding (development only).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app, _ = create_app()
    with app.app_context():
        run_seed(clear_all=args.clear_all)


if __name__ == "__main__":
    main()
