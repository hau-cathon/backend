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
    "#AH-SEED-2006",
    "#AH-SEED-2007",
    "#AH-SEED-2008",
    "#AH-SEED-2009",
    "#AH-SEED-2010",
    "#AH-SEED-2011",
    "#AH-SEED-2012",
    "#AH-SEED-2013",
    "#AH-SEED-2014",
    "#AH-SEED-2015",
]
SEED_USER_EMAILS = [
    "anna.kowalska@animalhelper.local",
    "piotr.wisniewski@animalhelper.local",
    "marek.zielinski@animalhelper.local",
    "katarzyna.nowak@animalhelper.local",
    "tomasz.kowalczyk@animalhelper.local",
    "magdalena.wojcik@animalhelper.local",
]
SEED_CASE_CODES = [
    "interwencja_policja",
    "interwencja_gmina",
    "follow_up_zglaszajacy",
    "schronisko_transport",
    "weterynaryjne_konsultacje",
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
        {
            "email": "katarzyna.nowak@animalhelper.local",
            "username": "kasia_n",
            "password": "seed-password-123",
        },
        {
            "email": "tomasz.kowalczyk@animalhelper.local",
            "username": "tomek_k",
            "password": "seed-password-123",
        },
        {
            "email": "magdalena.wojcik@animalhelper.local",
            "username": "magda_w",
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
        {
            "code": "schronisko_transport",
            "label": "Transport do schroniska",
            "description": "Koordynacja transportu zwierzat do schroniska",
        },
        {
            "code": "weterynaryjne_konsultacje",
            "label": "Konsultacje weterynaryjne",
            "description": "Kontakt z poradnia weterynaryjna",
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
        {
            "name": "SEED: Transport do schroniska",
            "title": "Prośba o transport zwierzęcia",
            "description": "Koordynacja transportu",
            "case_type": case_types["schronisko_transport"],
            "body": (
                "Dzien dobry,\n\n"
                "Prosimy o transport dla {animal_type}.\n"
                "Miejsce odbioru: {location}\n"
                "Szczegoly: {description}\n\n"
                "Numer sprawy: {number}\n"
            ),
            "placeholders": "animal_type,location,description,number",
        },
        {
            "name": "SEED: Konsultacja weterynaryjna",
            "title": "Konieczna konsultacja weterynaryjna",
            "description": "Pilna pomoc weterynaryjna",
            "case_type": case_types["weterynaryjne_konsultacje"],
            "body": (
                "Dzien dobry,\n\n"
                "Potrzebujemy pilnej konsultacji dla {animal_type}.\n"
                "Objawy: {description}\n"
                "Lokalizacja: {location}\n\n"
                "Numer sprawy: {number}\n"
            ),
            "placeholders": "animal_type,description,location,number",
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
        {
            "case_type_ref": case_types["schronisko_transport"],
            "animal_type": "pies",
            "case_type": "bezdomny",
            "case_label": "Transport bezdomnego psa do schroniska",
            "description": "[SEED] Pies wymaga transportu do najbliższego schroniska.",
        },
        {
            "case_type_ref": case_types["schronisko_transport"],
            "animal_type": "kot",
            "case_type": "znaleziony",
            "case_label": "Znaleziony kot - wymagany odbiór",
            "description": "[SEED] Kot znaleziony przez obywatela, wymagany transport.",
        },
        {
            "case_type_ref": case_types["weterynaryjne_konsultacje"],
            "animal_type": "pies",
            "case_type": "ranny",
            "case_label": "Pies z obrażeniami - pilna pomoc",
            "description": "[SEED] Zwierzę wymaga natychmiastowej konsultacji weterynaryjnej.",
        },
        {
            "case_type_ref": case_types["weterynaryjne_konsultacje"],
            "animal_type": "jeż",
            "case_type": "chory",
            "case_label": "Jeż - podejrzenie zatrucia",
            "description": "[SEED] Zwierzę wykazuje objawy zatrucia, wymaga diagnostyki.",
        },
        {
            "case_type_ref": case_types["interwencja_policja"],
            "animal_type": "pies",
            "case_type": "znecanie",
            "case_label": "Pies bite przez właściciela",
            "description": "[SEED] Świadkowie zgłaszają przemoc wobec zwierzęcia.",
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
        {
            "title": "#AH-SEED-2006",
            "event_type": "zdarzenie_drogowe",
            "species": "lis",
            "animal_count": 1,
            "options": ["droga krajowa", "pilne"],
            "urgency": True,
            "incident_address": "DK12 km 156, koło Piotrkowa Trybunalskiego",
            "contact_phone": "506666777",
            "description": "Lis potrącony na drodze krajowej, zwierzę żyje ale nie może się poruszać.",
            "status": "in_progress",
            "assigned_to": users["kasia_n"],
            "created_at": now - timedelta(hours=6),
            "updated_at": now - timedelta(hours=1),
        },
        {
            "title": "#AH-SEED-2007",
            "event_type": "znecanie_sie",
            "species": "pies",
            "animal_count": 1,
            "options": ["łańcuch", "brak schronienia"],
            "urgency": True,
            "incident_address": "ul. Polna 45, Lublin",
            "contact_phone": "507777888",
            "description": "Pies trzymany na krótkim łańcuchu bez dostępu do schronienia i wody w upale.",
            "status": "open",
            "assigned_to": users["tomek_k"],
            "created_at": now - timedelta(hours=4),
            "updated_at": now - timedelta(hours=3),
        },
        {
            "title": "#AH-SEED-2008",
            "event_type": "bezdomne_zwierze",
            "species": "koty",
            "animal_count": 5,
            "options": ["kolonia", "sterylizacja"],
            "urgency": False,
            "incident_address": "Osiedle Słoneczne, parking przy bloku 14B, Gdańsk",
            "contact_phone": "508888999",
            "description": "Kolonia bezdomnych kotów, mieszkańcy proszą o pomoc w sterylizacji.",
            "status": "open",
            "assigned_to": users["magda_w"],
            "created_at": now - timedelta(hours=32),
            "updated_at": now - timedelta(hours=30),
        },
        {
            "title": "#AH-SEED-2009",
            "event_type": "inne",
            "species": "jeż",
            "animal_count": 1,
            "options": ["wyczerpany", "odwodniony"],
            "urgency": False,
            "incident_address": "Park miejski, ul. Ogrodowa, Wrocław",
            "contact_phone": "509999000",
            "description": "Jeż znaleziony w dzień, wyczerpany i odwodniony, prawdopodobnie chory.",
            "status": "resolved",
            "assigned_to": users["anna_k"],
            "created_at": now - timedelta(days=1, hours=8),
            "updated_at": now - timedelta(hours=12),
            "resolved_at": now - timedelta(hours=12),
        },
        {
            "title": "#AH-SEED-2010",
            "event_type": "bezdomne_zwierze",
            "species": "pies",
            "animal_count": 1,
            "options": ["agresywny", "niebezpieczny"],
            "urgency": True,
            "incident_address": "ul. Przemysłowa 88, Katowice",
            "contact_phone": "510000111",
            "description": "Agresywny bezdomny pies biega po terenach przemysłowych, stanowi zagrożenie.",
            "status": "in_progress",
            "assigned_to": users["marek_z"],
            "created_at": now - timedelta(hours=10),
            "updated_at": now - timedelta(hours=2),
        },
        {
            "title": "#AH-SEED-2011",
            "event_type": "zdarzenie_drogowe",
            "species": "sarna",
            "animal_count": 1,
            "options": ["martwe", "odbiór"],
            "urgency": False,
            "incident_address": "ul. Leśna przy lesie komunalnym, Szczecin",
            "contact_phone": "511111222",
            "description": "Martwa sarna przy drodze, wymaga odbioru.",
            "status": "closed",
            "assigned_to": users["piotr_w"],
            "created_at": now - timedelta(days=4),
            "updated_at": now - timedelta(days=3, hours=20),
            "resolved_at": now - timedelta(days=3, hours=20),
        },
        {
            "title": "#AH-SEED-2012",
            "event_type": "inne",
            "species": "wiewiórka",
            "animal_count": 1,
            "options": ["młode", "opiekun"],
            "urgency": False,
            "incident_address": "Park Jordana, Kraków",
            "contact_phone": "512222333",
            "description": "Młoda wiewiórka wypadła z gniazda, wymaga przekazania do rehabilitacji.",
            "status": "resolved",
            "assigned_to": users["kasia_n"],
            "created_at": now - timedelta(hours=48),
            "updated_at": now - timedelta(hours=24),
            "resolved_at": now - timedelta(hours=24),
        },
        {
            "title": "#AH-SEED-2013",
            "event_type": "znecanie_sie",
            "species": "kot",
            "animal_count": 3,
            "options": ["piwnica", "brud"],
            "urgency": True,
            "incident_address": "ul. Spacerowa 19, Bydgoszcz",
            "contact_phone": "513333444",
            "description": "Trzy koty zamknięte w piwnicy bez światła, wody i jedzenia od tygodnia.",
            "status": "open",
            "assigned_to": users["tomek_k"],
            "created_at": now - timedelta(hours=2),
            "updated_at": now - timedelta(hours=1),
        },
        {
            "title": "#AH-SEED-2014",
            "event_type": "bezdomne_zwierze",
            "species": "pies",
            "animal_count": 1,
            "options": ["przyjazny", "chiped"],
            "urgency": False,
            "incident_address": "Rynek Główny, Częstochowa",
            "contact_phone": "514444555",
            "description": "Zagubiony pies z obrożą i chipem, wymaga skanowania i kontaktu z właścicielem.",
            "status": "in_progress",
            "assigned_to": users["magda_w"],
            "created_at": now - timedelta(hours=7),
            "updated_at": now - timedelta(hours=5),
        },
        {
            "title": "#AH-SEED-2015",
            "event_type": "inne",
            "species": "gołąb",
            "animal_count": 1,
            "options": ["skrzydło", "balkon"],
            "urgency": False,
            "incident_address": "ul. Morska 34/12, Gdynia",
            "contact_phone": "515555666",
            "description": "Gołąb z uszkodzonym skrzydłem wleciał na balkon, nie może odlecieć.",
            "status": "open",
            "assigned_to": users["anna_k"],
            "created_at": now - timedelta(hours=5),
            "updated_at": now - timedelta(hours=4),
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

    # #AH-SEED-2001 - Pies potrącony
    add("#AH-SEED-2001", "issue_created", "Utworzono zgloszenie", "Nowe zgloszenie drogowe zostalo zapisane.", "info", 18)
    add("#AH-SEED-2001", "email_sent", "Wyslano wiadomosc email", "Do: patrol@wet.local | Temat: Pilna interwencja", "success", 17.5)
    add("#AH-SEED-2001", "status_changed", "Zmieniono status zgloszenia", "Nowy status: in_progress", "warning", 16)
    add("#AH-SEED-2001", "note_added", "Dodano notatke operatora", "Weterynarz jedzie na miejsce, ETA 15 min.", "info", 15)

    # #AH-SEED-2002 - Kot na balkonie
    add("#AH-SEED-2002", "issue_created", "Utworzono zgloszenie", "Sprawa dotyczaca podejrzenia znecania.", "info", 26)
    add("#AH-SEED-2002", "note_added", "Dodano notatke operatora", "Oczekiwanie na kontakt z administracja budynku.", "info", 22)
    add("#AH-SEED-2002", "email_sent", "Wyslano wiadomosc email", "Do: piw@krakow.local | Temat: Interwencja - znęcanie", "success", 21)

    # #AH-SEED-2003 - Bocian ranny
    add("#AH-SEED-2003", "issue_created", "Utworzono zgloszenie", "Sprawa rannego bociana.", "info", 51)
    add("#AH-SEED-2003", "email_sent", "Wyslano wiadomosc email", "Do: rehabilitacja@ptaki.pl | Temat: Ranny bocian", "success", 48)
    add("#AH-SEED-2003", "status_changed", "Zmieniono status zgloszenia", "Nowy status: resolved", "success", 30)
    add("#AH-SEED-2003", "note_added", "Dodano notatke operatora", "Bocian przekazany do rehabilitatora, prognoza dobra.", "success", 30)

    # #AH-SEED-2004 - Duplikat
    add("#AH-SEED-2004", "duplicate_detected", "Wykryto duplikat", "Sprawa zostala powiazana z #AH-SEED-2001.", "warning", 13)
    add("#AH-SEED-2004", "duplicate_merged", "Polaczono duplikat", "Scalono duplikat z oryginalem.", "success", 9.5)

    # #AH-SEED-2005 - Koty do schroniska
    add("#AH-SEED-2005", "issue_created", "Utworzono zgloszenie", "Sprawa bezdomnych kotow przekazana do gminy.", "info", 72)
    add("#AH-SEED-2005", "email_sent", "Wyslano wiadomosc email", "Do: schronisko@poznan.pl | Temat: Transport kotów", "success", 68)
    add("#AH-SEED-2005", "status_changed", "Zmieniono status zgloszenia", "Nowy status: closed", "success", 27)

    # #AH-SEED-2006 - Lis potrącony
    add("#AH-SEED-2006", "issue_created", "Utworzono zgloszenie", "Pilne - lis potrącony na DK12.", "warning", 6)
    add("#AH-SEED-2006", "status_changed", "Zmieniono status zgloszenia", "Nowy status: in_progress", "warning", 5)
    add("#AH-SEED-2006", "email_sent", "Wyslano wiadomosc email", "Do: wet-piotrkow@clinic.pl | Temat: Pilna interwencja", "success", 4.5)

    # #AH-SEED-2007 - Pies na łańcuchu
    add("#AH-SEED-2007", "issue_created", "Utworzono zgloszenie", "Zgłoszenie znęcania - pies na łańcuchu.", "warning", 4)
    add("#AH-SEED-2007", "email_sent", "Wyslano wiadomosc email", "Do: policja@lublin.pl | Temat: Interwencja - znęcanie", "success", 3.5)

    # #AH-SEED-2008 - Kolonia kotów
    add("#AH-SEED-2008", "issue_created", "Utworzono zgloszenie", "Kolonia kotów - prośba o sterylizację.", "info", 32)
    add("#AH-SEED-2008", "note_added", "Dodano notatke operatora", "Kontakt z organizacją TOZ w sprawie programu sterylizacji.", "info", 30)

    # #AH-SEED-2009 - Jeż chory
    add("#AH-SEED-2009", "issue_created", "Utworzono zgloszenie", "Jeż odwodniony znaleziony w parku.", "info", 32)
    add("#AH-SEED-2009", "email_sent", "Wyslano wiadomosc email", "Do: rehab@wildlife.pl | Temat: Chory jeż", "success", 28)
    add("#AH-SEED-2009", "status_changed", "Zmieniono status zgloszenia", "Nowy status: resolved", "success", 12)
    add("#AH-SEED-2009", "note_added", "Dodano notatke operatora", "Jeż przyjęty do rehabilitacji.", "success", 12)

    # #AH-SEED-2010 - Agresywny pies
    add("#AH-SEED-2010", "issue_created", "Utworzono zgloszenie", "Agresywny bezdomny pies - zagrożenie.", "warning", 10)
    add("#AH-SEED-2010", "status_changed", "Zmieniono status zgloszenia", "Nowy status: in_progress", "warning", 9)
    add("#AH-SEED-2010", "email_sent", "Wyslano wiadomosc email", "Do: straż@katowice.pl | Temat: Pies agresywny", "success", 8)

    # #AH-SEED-2011 - Martwa sarna
    add("#AH-SEED-2011", "issue_created", "Utworzono zgloszenie", "Martwa sarna - odbiór zwłok.", "info", 96)
    add("#AH-SEED-2011", "email_sent", "Wyslano wiadomosc email", "Do: odpady@szczecin.pl | Temat: Odbiór zwłok zwierzęcia", "success", 92)
    add("#AH-SEED-2011", "status_changed", "Zmieniono status zgloszenia", "Nowy status: closed", "success", 68)

    # #AH-SEED-2012 - Wiewiórka z gniazda
    add("#AH-SEED-2012", "issue_created", "Utworzono zgloszenie", "Młoda wiewiórka - wymaga opieki.", "info", 48)
    add("#AH-SEED-2012", "email_sent", "Wyslano wiadomosc email", "Do: rehab-wildlife@krakow.pl | Temat: Młoda wiewiórka", "success", 45)
    add("#AH-SEED-2012", "status_changed", "Zmieniono status zgloszenia", "Nowy status: resolved", "success", 24)

    # #AH-SEED-2013 - Koty w piwnicy
    add("#AH-SEED-2013", "issue_created", "Utworzono zgloszenie", "PILNE - 3 koty zamknięte w piwnicy.", "warning", 2)
    add("#AH-SEED-2013", "email_sent", "Wyslano wiadomosc email", "Do: policja@bydgoszcz.pl | Temat: Pilna interwencja", "success", 1.5)

    # #AH-SEED-2014 - Zagubiony pies z chipem
    add("#AH-SEED-2014", "issue_created", "Utworzono zgloszenie", "Zagubiony pies z chipem.", "info", 7)
    add("#AH-SEED-2014", "status_changed", "Zmieniono status zgloszenia", "Nowy status: in_progress", "warning", 6)
    add("#AH-SEED-2014", "note_added", "Dodano notatke operatora", "Chip zeskanowany, kontakt z właścicielem w toku.", "info", 5)

    # #AH-SEED-2015 - Gołąb na balkonie
    add("#AH-SEED-2015", "issue_created", "Utworzono zgloszenie", "Gołąb z uszkodzonym skrzydłem.", "info", 5)
    add("#AH-SEED-2015", "note_added", "Dodano notatke operatora", "Czeka na wolontariusza do odbioru.", "info", 4)


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
        {
            "ticket_id": "#AH-SEED-2003",
            "issue": issues["#AH-SEED-2003"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "rehabilitacja@ptaki.pl",
            "subject": "Ranny bocian - sprawa #AH-SEED-2003",
            "body": "Bocian po kolizji z linią energetyczną wymaga pilnej pomocy.",
            "created_at": now - timedelta(hours=48),
        },
        {
            "ticket_id": "#AH-SEED-2003",
            "issue": issues["#AH-SEED-2003"],
            "direction": "inbound",
            "from_email": "rehabilitacja@ptaki.pl",
            "to_email": "noreply@animalhelper.local",
            "subject": "Re: Ranny bocian - sprawa #AH-SEED-2003",
            "body": "Bocian przyjęty do rehabilitacji. Prognoza dobra, skrzydło w trakcie leczenia.",
            "created_at": now - timedelta(hours=30),
        },
        {
            "ticket_id": "#AH-SEED-2005",
            "issue": issues["#AH-SEED-2005"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "schronisko@poznan.pl",
            "subject": "Transport kotów - sprawa #AH-SEED-2005",
            "body": "Prosimy o transport dwóch bezdomnych kotów do schroniska.",
            "created_at": now - timedelta(hours=68),
        },
        {
            "ticket_id": "#AH-SEED-2006",
            "issue": issues["#AH-SEED-2006"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "wet-piotrkow@clinic.pl",
            "subject": "PILNE: Lis potrącony - sprawa #AH-SEED-2006",
            "body": "Lis potrącony na DK12 km 156, zwierzę żyje ale wymaga pilnej pomocy weterynaryjnej.",
            "created_at": now - timedelta(hours=4, minutes=30),
        },
        {
            "ticket_id": "#AH-SEED-2007",
            "issue": issues["#AH-SEED-2007"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "policja@lublin.pl",
            "subject": "Interwencja - znęcanie nad psem #AH-SEED-2007",
            "body": "Pies trzymany na krótkim łańcuchu bez schronienia i wody w upale. Prosimy o interwencję.",
            "created_at": now - timedelta(hours=3, minutes=30),
        },
        {
            "ticket_id": "#AH-SEED-2009",
            "issue": issues["#AH-SEED-2009"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "rehab@wildlife.pl",
            "subject": "Chory jeż - sprawa #AH-SEED-2009",
            "body": "Jeż znaleziony w dzień, wyczerpany i odwodniony, prawdopodobnie chory.",
            "created_at": now - timedelta(hours=28),
        },
        {
            "ticket_id": "#AH-SEED-2009",
            "issue": issues["#AH-SEED-2009"],
            "direction": "inbound",
            "from_email": "rehab@wildlife.pl",
            "to_email": "noreply@animalhelper.local",
            "subject": "Re: Chory jeż - sprawa #AH-SEED-2009",
            "body": "Jeż przyjęty, otrzymał nawodnienie i karmimy. Po obserwacji zostanie wypuszczony.",
            "created_at": now - timedelta(hours=12),
        },
        {
            "ticket_id": "#AH-SEED-2010",
            "issue": issues["#AH-SEED-2010"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "straż@katowice.pl",
            "subject": "Agresywny bezdomny pies #AH-SEED-2010",
            "body": "Agresywny bezdomny pies stanowi zagrożenie na terenach przemysłowych. Wymaga odłowienia.",
            "created_at": now - timedelta(hours=8),
        },
        {
            "ticket_id": "#AH-SEED-2011",
            "issue": issues["#AH-SEED-2011"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "odpady@szczecin.pl",
            "subject": "Odbiór zwłok sarny #AH-SEED-2011",
            "body": "Martwa sarna przy ul. Leśnej, prosimy o odbiór.",
            "created_at": now - timedelta(hours=92),
        },
        {
            "ticket_id": "#AH-SEED-2012",
            "issue": issues["#AH-SEED-2012"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "rehab-wildlife@krakow.pl",
            "subject": "Młoda wiewiórka - sprawa #AH-SEED-2012",
            "body": "Młoda wiewiórka wypadła z gniazda, wymaga przekazania do rehabilitacji.",
            "created_at": now - timedelta(hours=45),
        },
        {
            "ticket_id": "#AH-SEED-2013",
            "issue": issues["#AH-SEED-2013"],
            "direction": "outbound",
            "from_email": "noreply@animalhelper.local",
            "to_email": "policja@bydgoszcz.pl",
            "subject": "PILNE: 3 koty w piwnicy #AH-SEED-2013",
            "body": "Trzy koty zamknięte w piwnicy bez światła, wody i jedzenia od tygodnia. Pilna interwencja.",
            "created_at": now - timedelta(hours=1, minutes=30),
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

    _print("Rozpoczynam seedowanie danych testowych...")
    
    seed_roles()
    _print("✓ Role dodane")
    
    users = seed_users()
    _print(f"✓ Użytkownicy dodani: {len(users)}")
    
    case_types = seed_email_case_types()
    _print(f"✓ Typy spraw email dodane: {len(case_types)}")
    
    seed_email_templates(case_types)
    _print(f"✓ Szablony email dodane: {EmailTemplate.objects.count()}")
    
    seed_template_options(case_types)
    _print(f"✓ Opcje szablonów dodane: {TemplateOption.objects.count()}")
    
    issues = seed_issues(users)
    _print(f"✓ Zgłoszenia (issues) dodane: {len(issues)}")
    
    seed_action_history(issues)
    _print(f"✓ Historia akcji dodana: {ActionHistoryEntry.objects.count()}")
    
    seed_email_history(issues)
    _print(f"✓ Historia emaili dodana: {EmailMessage.objects.count()}")

    _print("")
    _print("=" * 60)
    _print("Seed completed successfully!")
    _print("=" * 60)
    _print(f"📋 Issues: {Issue.objects.count()}")
    _print(f"📝 Action history entries: {ActionHistoryEntry.objects.count()}")
    _print(f"📧 Email messages: {EmailMessage.objects.count()}")
    _print(f"📄 Email templates: {EmailTemplate.objects.count()}")
    _print(f"🔧 Template options: {TemplateOption.objects.count()}")
    _print(f"👥 Users: {User.objects.count()}")
    _print(f"🎭 Roles: {Role.objects.count()}")
    _print(f"📮 Email case types: {EmailCaseType.objects.count()}")
    _print("=" * 60)


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
