"""Email utilities using SMTP"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def send_email(to_email, subject, body, html_body=None):
    """
    Wysyła email przez SMTP
    
    Args:
        to_email: adres odbiorcy
        subject: temat wiadomości
        body: treść tekstowa
        html_body: opcjonalna treść HTML
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = current_app.config['MAIL_USERNAME']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
            
            server.login(
                current_app.config['MAIL_USERNAME'],
                current_app.config['MAIL_PASSWORD']
            )
            server.send_message(msg)
        
        return True
    except Exception as e:
        current_app.logger.error(f"Błąd wysyłania email: {str(e)}")
        return False


def send_priority_notification(to_email, ticket_description, priority):
    """Wysyła powiadomienie o priorytecie zgłoszenia"""
    subject = f"Nowe zgłoszenie - Priorytet: {priority}"
    
    body = f"""
    Otrzymałeś nowe zgłoszenie:
    
    Opis: {ticket_description}
    Priorytet: {priority}
    
    Zaloguj się do systemu aby zobaczyć szczegóły.
    """
    
    html_body = f"""
    <html>
        <body>
            <h2>Nowe zgłoszenie</h2>
            <p><strong>Opis:</strong> {ticket_description}</p>
            <p><strong>Priorytet:</strong> <span style="color: {'red' if 'krytyczny' in priority else 'orange' if 'średni' in priority else 'green'}">{priority}</span></p>
            <p>Zaloguj się do systemu aby zobaczyć szczegóły.</p>
        </body>
    </html>
    """
    
    return send_email(to_email, subject, body, html_body)