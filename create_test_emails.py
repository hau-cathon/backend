"""Create test email messages in database"""
from mongoengine import connect
from app.models.issue import Issue
from app.models.email_message import EmailMessage
from datetime import datetime, timedelta

print("📡 Connecting to MongoDB...")
connect(host='mongodb://localhost:27017/pieski_db')
print("✅ Connected!")

print()
print("🗑️  Clearing old emails...")
EmailMessage.objects().delete()
print("✅ Cleared!")

print()
print("📝 Creating test emails for issues...")

# Get issues
issue1 = Issue.objects(ticket_number="#AH-1024").first()
issue2 = Issue.objects(ticket_number="#AH-1025").first()

if issue1:
    # Email 1: Outbound - potwierdzenie zgłoszenia
    email1 = EmailMessage(
        ticket_id=str(issue1.id),
        direction='outbound',
        from_email='system@pieski.pl',
        to_email='jan.nowak@example.com',
        subject=f'[{issue1.ticket_number}] Potwierdzenie przyjęcia zgłoszenia',
        body='Dziękujemy za zgłoszenie. Zajmiemy się sprawą w trybie pilnym.\n\nZespół Animal Helper',
        created_at=datetime.utcnow() - timedelta(hours=2),
        is_automated=True
    )
    email1.save()
    print(f"   ✅ Email 1: Potwierdzenie dla {issue1.ticket_number}")
    
    # Email 2: Inbound - odpowiedź od zgłaszającego
    email2 = EmailMessage(
        ticket_id=str(issue1.id),
        direction='inbound',
        from_email='jan.nowak@example.com',
        to_email='system@pieski.pl',
        subject=f'Re: [{issue1.ticket_number}] Potwierdzenie przyjęcia zgłoszenia',
        body='Dziękuję za szybką reakcję! Pies nadal leży w tym samym miejscu. Czy ktoś już jedzie?',
        created_at=datetime.utcnow() - timedelta(hours=1, minutes=30),
        read_at=datetime.utcnow() - timedelta(hours=1, minutes=25)
    )
    email2.save()
    print(f"   ✅ Email 2: Odpowiedź dla {issue1.ticket_number}")
    
    # Email 3: Outbound - update o patrolu
    email3 = EmailMessage(
        ticket_id=str(issue1.id),
        direction='outbound',
        from_email='system@pieski.pl',
        to_email='jan.nowak@example.com',
        subject=f'[{issue1.ticket_number}] Patrol weterynaryjny w drodze',
        body='Patrol weterynaryjny WET-03 już jedzie na miejsce. Szacowany czas przyjazdu: 15 minut.\n\nZespół Animal Helper',
        created_at=datetime.utcnow() - timedelta(hours=1),
        is_automated=False
    )
    email3.save()
    print(f"   ✅ Email 3: Update dla {issue1.ticket_number}")

if issue2:
    # Email 4: Outbound - potwierdzenie dla issue 2
    email4 = EmailMessage(
        ticket_id=str(issue2.id),
        direction='outbound',
        from_email='system@pieski.pl',
        to_email='maria.zielinska@example.com',
        subject=f'[{issue2.ticket_number}] Potwierdzenie przyjęcia zgłoszenia',
        body='Dziękujemy za zgłoszenie sprawy kota zamkniętego na balkonie. Kontaktujemy się z właścicielem mieszkania.\n\nZespół Animal Helper',
        created_at=datetime.utcnow() - timedelta(days=1),
        is_automated=True
    )
    email4.save()
    print(f"   ✅ Email 4: Potwierdzenie dla {issue2.ticket_number}")
    
    # Email 5: Outbound - ponowna próba kontaktu
    email5 = EmailMessage(
        ticket_id=str(issue2.id),
        direction='outbound',
        from_email='system@pieski.pl',
        to_email='maria.zielinska@example.com',
        subject=f'[{issue2.ticket_number}] Aktualizacja sprawy',
        body='Nie udało się skontaktować z właścicielem mieszkania. Wysłano zawiadomienie do straży miejskiej.\n\nZespół Animal Helper',
        created_at=datetime.utcnow() - timedelta(hours=12),
        is_automated=False
    )
    email5.save()
    print(f"   ✅ Email 5: Aktualizacja dla {issue2.ticket_number}")

print()
print("=" * 70)
print("✅ TEST EMAILS CREATED!")
print("=" * 70)
print()
print("📧 Email count:")
if issue1:
    count1 = EmailMessage.objects(ticket_id=str(issue1.id)).count()
    print(f"   • {issue1.ticket_number}: {count1} emails")
if issue2:
    count2 = EmailMessage.objects(ticket_id=str(issue2.id)).count()
    print(f"   • {issue2.ticket_number}: {count2} emails")
print()
print("🧪 TEST NOW:")
print("-" * 70)
if issue1:
    print(f"curl http://localhost:5000/api/email/ticket/{issue1.ticket_number}/history")
print()
print("💡 Open frontend and check email history in ticket details!")
print()
