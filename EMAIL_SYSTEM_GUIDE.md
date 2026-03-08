# Email System Implementation Guide

## System Overview

Ten system mailingowy umożliwia:
1. **Automatyczne odczytywanie emaili** z zewnętrznej skrzynki (IMAP)
2. **Przypisywanie emaili do zgłoszeń** na podstawie numeru zgłoszenia w temacie/treści
3. **Wysyłanie emaili** do zgłaszających z poziomu interfejsu
4. **Przechowywanie historii** wszystkich emaili powiązanych ze zgłoszeniem

## Backend Components

### 1. Models

#### EmailMessage (`app/models/email_message.py`)
Przechowuje wszystkie emaile powiązane ze zgłoszeniami:
- `direction`: 'inbound' (odebrane) lub 'outbound' (wysłane)
- `ticket_id`: ID zgłoszenia
- `from_email`, `to_email`: Adresy
- `subject`, `body`: Treść
- `created_at`: Data

#### Issue (`app/models/issue.py`)
Zaktualizowany model zgłoszenia:
- `reporter_email`: Email zgłaszającego
- `ticket_number`: Unikalny numer np. "ZGL-12345" (używany w tematach emaili)

### 2. Email Utilities

#### `app/utils/email_reader.py`
- `read_unread_emails()`: Odczytuje nieprzeczytane emaile z IMAP
- `extract_ticket_number()`: Wyciąga numer zgłoszenia z tekstu (regex)
- `mark_as_read()`: Oznacza email jako przeczytany

#### `app/utils/SMTP.py`
- `send_email()`: Wysyła email przez SMTP

#### `app/utils/email_helpers.py` (NEW)
- `generate_ticket_number()`: Generuje unikalny numer zgłoszenia
- `create_ticket_email_template()`: Tworzy szablon email z potwierdzeniem

### 3. API Endpoints (`app/routes/email_routes.py`)

#### `GET /api/email/check`
Sprawdza nowe emaile i automatycznie przypisuje do zgłoszeń:
```json
{
  "status": "success",
  "processed": 3,
  "errors": 1
}
```

#### `GET /api/email/ticket/<ticket_id>/history`
Pobiera historię emaili dla zgłoszenia:
```json
{
  "status": "success",
  "emails": [
    {
      "id": "...",
      "direction": "outbound",
      "from_email": "system@example.com",
      "subject": "[ZGL-12345] Potwierdzenie",
      "body": "...",
      "created_at": "2026-03-08T..."
    }
  ]
}
```

#### `POST /api/email/ticket/<ticket_id>/send`
Wysyła email w kontekście zgłoszenia:
```json
{
  "to_email": "user@example.com",
  "subject": "Aktualizacja statusu",
  "body": "Twoje zgłoszenie zostało zaktualizowane..."
}
```

## Frontend Components

### 1. Services (`services/email.service.ts`)
API client do komunikacji z backendem:
- `getTicketEmailHistory(ticketId)`
- `sendTicketEmail(ticketId, emailData)`
- `checkNewEmails()`

### 2. Components

#### `ComposeEmailModal.tsx`
Modal do wysyłania nowych emaili:
- Formularz z polami: Do, Temat, Treść
- Automatyczne dodawanie numeru zgłoszenia do tematu
- Walidacja i obsługa błędów

#### `EmailHistoryPanel.tsx`
Panel wyświetlający historię emaili:
- Lista emaili z oznaczeniem kierunku (przychodzący/wychodzący)
- Rozwijane karty z pełną treścią
- Pull-to-refresh
- Przycisk "Nowy" do wysyłania emaili

## Configuration

### Backend (.env file)
```bash
# SMTP (wysyłanie)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# IMAP (odbieranie)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
```

### Gmail Setup
1. Włącz 2-Factor Authentication
2. Wygeneruj App Password: https://myaccount.google.com/apppasswords
3. Użyj App Password zamiast zwykłego hasła

## Usage Flow

### 1. Utworzenie zgłoszenia
```python
from app.utils.email_helpers import generate_ticket_number, create_ticket_email_template
from app.utils.SMTP import send_email

# Generuj unikalny numer
ticket_number = generate_ticket_number()  # "ZGL-12345"

# Utwórz zgłoszenie
issue = Issue(
    title="Pies bez opieki",
    description="...",
    ticket_number=ticket_number,
    reporter_email="user@example.com"
)
issue.save()

# Wyślij potwierdzenie
subject, body, html = create_ticket_email_template(
    ticket_number, issue.title, issue.description
)
send_email(issue.reporter_email, subject, body, html)

# Zapisz w historii
EmailMessage(
    ticket_id=str(issue.id),
    direction='outbound',
    from_email='system@example.com',
    to_email=issue.reporter_email,
    subject=subject,
    body=body,
    is_automated=True
).save()
```

### 2. Odpowiedź użytkownika
Użytkownik odpowiada na email z numerem [ZGL-12345] w temacie:

```python
# Automatycznie przez cron/scheduler
from app.routes.email_routes import check_emails

# Lub ręcznie przez API
GET /api/email/check
```

System:
1. Odczytuje nieprzeczytane emaile
2. Wyciąga numer zgłoszenia z tematu/treści
3. Znajduje zgłoszenie w bazie
4. Zapisuje email jako 'inbound'
5. Oznacza jako przeczytany

### 3. Wyświetlanie historii
Frontend w widoku szczegółów zgłoszenia:
```typescript
import EmailHistoryPanel from '@/components/EmailHistoryPanel';

<EmailHistoryPanel 
  ticketId={ticketId}
  onComposeClick={() => setComposeVisible(true)}
/>
```

### 4. Wysłanie odpowiedzi
```typescript
import ComposeEmailModal from '@/components/ComposeEmailModal';

<ComposeEmailModal
  visible={composeVisible}
  ticketId={ticketId}
  recipientEmail="user@example.com"
  ticketNumber="ZGL-12345"
  onSuccess={() => {/* odśwież historię */}}
/>
```

## Automatic Email Checking (Cron Job)

### Option 1: Flask-APScheduler
```python
# app/__init__.py
from flask_apscheduler import APScheduler
from app.routes.email_routes import check_emails

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

@scheduler.task('interval', id='check_emails', minutes=5)
def scheduled_email_check():
    with app.app_context():
        check_emails()
```

### Option 2: External Cron
```bash
# crontab -e
*/5 * * * * curl http://localhost:5000/api/email/check
```

## Testing

### Test Email Reading
```bash
curl http://localhost:5000/api/email/check
```

### Test Email Sending
```bash
curl -X POST http://localhost:5000/api/email/ticket/TICKET_ID/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "subject": "Test",
    "body": "Test message"
  }'
```

### Test Email History
```bash
curl http://localhost:5000/api/email/ticket/TICKET_ID/history
```

## Security Considerations

1. **Email Validation**: Sprawdź że email pochodzi od zgłaszającego
2. **Rate Limiting**: Ogranicz liczbę emaili na zgłoszenie/użytkownika
3. **Spam Prevention**: Implementuj captcha dla nowych zgłoszeń
4. **Content Filtering**: Filtruj potencjalnie niebezpieczną treść
5. **Auth**: Sprawdź uprawnienia przed wysyłaniem emaili

## Future Enhancements

1. **Attachments**: Obsługa załączników
2. **Templates**: System szablonów emaili
3. **Auto-replies**: Automatyczne odpowiedzi
4. **Email Threading**: Grupowanie konwersacji
5. **Rich Text Editor**: WYSIWYG dla HTML emaili
6. **Notifications**: Powiadomienia o nowych emailach
7. **Search**: Wyszukiwanie w historii emaili
