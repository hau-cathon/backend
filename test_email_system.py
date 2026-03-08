"""Test script for email system"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("🧪 TEST SYSTEMU EMAILOWEGO")
print("=" * 60)
print()

# Test 1: Sprawdź połączenie z API
print("1️⃣  Test połączenia z API...")
try:
    response = requests.get(f"{BASE_URL}/api/email/check", timeout=5)
    print(f"   ✅ API działa! Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   📧 Znaleziono emaili: {data.get('total', 0)}")
        print(f"   ✓ Przetworzonych: {data.get('processed', 0)}")
        print(f"   ✗ Błędów: {data.get('errors', 0)}")
except Exception as e:
    print(f"   ❌ Błąd: {e}")

print()

# Test 2: Utwórz testowe zgłoszenie
print("2️⃣  Tworzenie testowego zgłoszenia...")
print("   ⚠️  UWAGA: To wymaga endpointu do tworzenia Issue")
print("   Możesz to zrobić ręcznie w MongoDB Compass:")
print()
print("   MongoDB Connection: mongodb://localhost:27017")
print("   Database: pieski_db")
print("   Collection: issues")
print()
print("   Przykładowy dokument:")
example_issue = {
    "_id": "test_issue_001",
    "title": "Pies bez opieki",
    "description": "Znaleziono psa na ulicy",
    "reporter_email": "test@example.com",
    "ticket_number": "ZGL-12345",
    "status": "open",
    "priority": "medium",
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat()
}
print(json.dumps(example_issue, indent=2, ensure_ascii=False))

print()
print("-" * 60)
print()

# Test 3: Test wysyłania emaila
print("3️⃣  Test wysyłania emaila (wymaga konfiguracji SMTP)...")
print("   📝 Najpierw skonfiguruj .env:")
print("      MAIL_USERNAME=twoj-email@gmail.com")
print("      MAIL_PASSWORD=haslo-aplikacji")
print()
print("   Następnie wywołaj:")
test_email_data = {
    "to_email": "odbiorca@example.com",
    "subject": "Test wiadomości",
    "body": "To jest testowa wiadomość z systemu"
}
print(f"   POST {BASE_URL}/api/email/ticket/test_issue_001/send")
print(f"   Body: {json.dumps(test_email_data, indent=2)}")

print()
print("-" * 60)
print()

# Test 4: Test historii emaili
print("4️⃣  Test pobierania historii emaili...")
try:
    # Użyj przykładowego ID
    response = requests.get(f"{BASE_URL}/api/email/ticket/test_issue_001/history", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Historia pobrana! Emaili: {data.get('count', 0)}")
        if data.get('emails'):
            for email in data['emails'][:3]:  # Pokaż pierwsze 3
                print(f"      📧 {email['direction']}: {email['subject']}")
    else:
        print(f"   ⚠️  Brak historii dla test_issue_001 (normalne dla nowej bazy)")
except Exception as e:
    print(f"   ❌ Błąd: {e}")

print()
print("=" * 60)
print("💡 DALSZE KROKI:")
print("=" * 60)
print()
print("1. Zainstaluj MongoDB Compass (GUI):")
print("   https://www.mongodb.com/try/download/compass")
print()
print("2. Połącz się: mongodb://localhost:27017")
print()
print("3. Utwórz testowe zgłoszenie w collection 'issues'")
print()
print("4. Skonfiguruj email w backend/.env:")
print("   - MAIL_USERNAME (Gmail)")
print("   - MAIL_PASSWORD (App Password)")
print("   - IMAP_SERVER=imap.gmail.com")
print()
print("5. Przetestuj w Postman lub curl:")
print()
print("   # Wyślij email")
print("   curl -X POST http://localhost:5000/api/email/ticket/TICKET_ID/send \\")
print('     -H "Content-Type: application/json" \\')
print('     -d \'{"to_email":"test@example.com","subject":"Test","body":"Hello"}\'')
print()
print("   # Sprawdź historię")
print("   curl http://localhost:5000/api/email/ticket/TICKET_ID/history")
print()
print("6. Odpal frontend: cd frontend/haucaton && npm run web")
print()
print("=" * 60)
