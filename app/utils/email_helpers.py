"""Email helper utilities"""
import random
import string
from app.models.issue import Issue


def generate_ticket_number():
    """
    Generuje unikalny numer zgłoszenia w formacie ZGL-XXXXX
    
    Returns:
        str: Unikalny numer zgłoszenia np. "ZGL-12345"
    """
    max_attempts = 100
    
    for _ in range(max_attempts):
        # Generate random 5-digit number
        number = ''.join(random.choices(string.digits, k=5))
        ticket_number = f"ZGL-{number}"
        
        # Check if exists
        existing = Issue.objects(ticket_number=ticket_number).first()
        if not existing:
            return ticket_number
    
    # Fallback: use timestamp
    import time
    timestamp = int(time.time() * 1000) % 99999
    return f"ZGL-{timestamp:05d}"


def format_email_for_ticket(ticket_number, subject):
    """
    Formatuje temat emaila z numerem zgłoszenia
    
    Args:
        ticket_number: numer zgłoszenia
        subject: oryginalny temat
        
    Returns:
        str: Sformatowany temat
    """
    if ticket_number and ticket_number not in subject:
        return f"[{ticket_number}] {subject}"
    return subject


def create_ticket_email_template(ticket_number, title, description, priority='medium'):
    """
    Tworzy szablon emaila potwierdzenia zgłoszenia
    
    Returns:
        tuple: (subject, body_text, body_html)
    """
    subject = f"Potwierdzenie zgłoszenia [{ticket_number}]"
    
    priority_text = {
        'low': 'niski',
        'medium': 'średni',
        'high': 'wysoki',
        'critical': 'krytyczny'
    }.get(priority, 'średni')
    
    body_text = f"""
Dziękujemy za zgłoszenie!

Numer zgłoszenia: {ticket_number}
Tytuł: {title}
Priorytet: {priority_text}

Opis:
{description}

Otrzymasz aktualizacje na ten adres email. 
Aby odpowiedzieć, wyślij email z numerem [{ticket_number}] w temacie.

---
Z poważaniem,
System Obsługi Zgłoszeń
    """.strip()
    
    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #4A90E2; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
        .ticket-box {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4A90E2; }}
        .footer {{ text-align: center; padding: 15px; color: #777; font-size: 12px; }}
        .priority {{ display: inline-block; padding: 4px 8px; border-radius: 3px; font-weight: bold; }}
        .priority-medium {{ background: #F0A500; color: white; }}
        .priority-low {{ background: #8E8E93; color: white; }}
        .priority-high {{ background: #FF6B35; color: white; }}
        .priority-critical {{ background: #FF3B30; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>✓ Zgłoszenie przyjęte</h2>
        </div>
        <div class="content">
            <div class="ticket-box">
                <p><strong>Numer zgłoszenia:</strong> <span style="color: #4A90E2; font-size: 18px;">{ticket_number}</span></p>
                <p><strong>Tytuł:</strong> {title}</p>
                <p><strong>Priorytet:</strong> <span class="priority priority-{priority}">{priority_text}</span></p>
            </div>
            
            <h3>Opis zgłoszenia:</h3>
            <p style="white-space: pre-wrap;">{description}</p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p>
                <strong>📧 Jak odpowiedzieć?</strong><br>
                Wyślij email z numerem <strong>[{ticket_number}]</strong> w temacie, aby kontynuować konwersację.
            </p>
        </div>
        <div class="footer">
            System Obsługi Zgłoszeń
        </div>
    </div>
</body>
</html>
    """.strip()
    
    return subject, body_text, body_html
