"""Create mock issues matching frontend mockData"""
from mongoengine import connect
from app.models.issue import Issue
from datetime import datetime

print("📡 Connecting to MongoDB...")
connect(host='mongodb://localhost:27017/pieski_db')
print("✅ Connected!")

print()
print("🗑️  Clearing old data...")
Issue.objects().delete()
print("✅ Cleared!")

print()
print("📝 Creating mock issues matching new Issue model...")

# Issue 1: #AH-1024
issue1 = Issue(
    event_type="zdarzenie_drogowe",
    title="Pies potrącony przez samochód",
    species="Pies",
    animal_count=1,
    options=["ranny", "potrzebuje_weterynarza"],
    urgency=True,
    incident_address="ul. Kwiatowa 12, Warszawa",
    contact_phone="+48123456789",
    description="Pies potrącony przez samochód na ul. Kwiatowej. Zwierzę leży przy chodniku, jest przytomne, ale nie może wstać. Właściciel nieznany. Świadek zdarzenia czeka na miejscu i prosi o szybką interwencję.",
    reporter_email="jan.nowak@example.com",
    ticket_number="#AH-1024",
    status="in_progress",
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
issue1.save()
print(f"   ✅ Issue 1: {issue1.ticket_number} (ID: {issue1.id})")

# Issue 2: #AH-1025
issue2 = Issue(
    event_type="znecanie_sie",
    title="Kot zamknięty na balkonie",
    species="Kot",
    animal_count=1,
    options=["glodny", "zaniedbany"],
    urgency=False,
    incident_address="ul. Różana 7/4, Kraków",
    contact_phone="+48987654321",
    description="Kot zamknięty na balkonie bez dostępu do wody i jedzenia od co najmniej 3 dni. Sąsiedzi zgłaszają głośne miauczenie. Właściciel nie odbiera telefonu.",
    reporter_email="maria.zielinska@example.com",
    ticket_number="#AH-1025",
    status="open",
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
issue2.save()
print(f"   ✅ Issue 2: {issue2.ticket_number} (ID: {issue2.id})")

# Issue 3: #AH-1026
issue3 = Issue(
    event_type="bezdomne_zwierze",
    title="Stado porzuconych szczeniąt",
    species="Pies",
    animal_count=5,
    options=["porzucone", "szczenieta", "wycienione"],
    urgency=True,
    incident_address="Droga leśna koło Piaseczna",
    contact_phone="+48555123456",
    description="Pięć szczeniąt znalezionych w kartonie przy drodze leśnej. Szczenięta są wycieńczone i wymagają natychmiastowej pomocy weterynaryjnej.",
    reporter_email="piotr.nowicki@example.com",
    ticket_number="#AH-1026",
    status="open",
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
issue3.save()
print(f"   ✅ Issue 3: {issue3.ticket_number} (ID: {issue3.id})")

print()
print("=" * 70)
print("✅ MOCK DATA CREATED!")
print("=" * 70)
print()
print("📋 Available issues:")
print(f"   • {issue1.ticket_number} - {issue1.title}")
print(f"   • {issue2.ticket_number} - {issue2.title}")
print(f"   • {issue3.ticket_number} - {issue3.title}")
print()
print("🧪 TEST EMAIL ENDPOINTS:")
print("-" * 70)
print(f"# Get email history for issue 1:")
print(f"curl http://localhost:5000/api/email/ticket/{issue1.ticket_number}/history")
print()
print(f"# Send email for issue 1:")
print(f'curl -X POST http://localhost:5000/api/email/ticket/{issue1.ticket_number}/send \\')
print('  -H "Content-Type: application/json" \\')
print('  -d \'{"to_email":"jan.nowak@example.com","subject":"Test","body":"Test message"}\'')
print()
print("💡 Now open frontend and navigate to any ticket to see email functionality!")
print()
