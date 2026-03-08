"""Email reader using IMAP"""
import imaplib
import email
from email.header import decode_header
import re
from flask import current_app


def connect_to_mailbox():
    """Łączy się ze skrzynką pocztową przez IMAP"""
    try:
        mail = imaplib.IMAP4_SSL(current_app.config['IMAP_SERVER'])
        mail.login(
            current_app.config['MAIL_USERNAME'],
            current_app.config['MAIL_PASSWORD']
        )
        return mail
    except Exception as e:
        current_app.logger.error(f"Błąd połączenia z IMAP: {str(e)}")
        return None


def extract_ticket_number(text):
    """
    Wyciąga numer zgłoszenia z tekstu
    Szuka wzorców typu: #123, ZGL-123, Ticket: 123, itp.
    """
    patterns = [
        r'#(\d+)',                      # #123
        r'ZGL-(\d+)',                   # ZGL-123
        r'Ticket[:\s]+(\d+)',           # Ticket: 123
        r'Zgłoszenie[:\s]+(\d+)',       # Zgłoszenie: 123
        r'ID[:\s]+(\d+)',               # ID: 123
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def decode_email_text(encoded_text):
    """Dekoduje tekst emaila"""
    if encoded_text is None:
        return ""
    
    decoded_parts = decode_header(encoded_text)
    decoded_text = ""
    
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_text += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            decoded_text += part
    
    return decoded_text


def get_email_body(msg):
    """Wyciąga treść z wiadomości email"""
    body = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body = part.get_payload()
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            body = msg.get_payload()
    
    return body


def read_unread_emails():
    """
    Czyta nieprzeczytane emaile i wyciąga numery zgłoszeń
    Returns: lista słowników z informacjami o emailach
    """
    mail = connect_to_mailbox()
    if not mail:
        return []
    
    try:
        # Wybierz skrzynkę odbiorczą
        mail.select('inbox')
        
        # Szukaj nieprzeczytanych wiadomości
        status, messages = mail.search(None, 'UNSEEN')
        
        if status != 'OK':
            return []
        
        email_ids = messages[0].split()
        emails_data = []
        
        for email_id in email_ids:
            # Pobierz email
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                continue
            
            # Parsuj wiadomość
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Wyciągnij dane
            subject = decode_email_text(msg['Subject'])
            sender = decode_email_text(msg['From'])
            date = msg['Date']
            body = get_email_body(msg)
            
            # Szukaj numeru zgłoszenia w temacie i treści
            ticket_number = extract_ticket_number(subject)
            if not ticket_number:
                ticket_number = extract_ticket_number(body)
            
            email_info = {
                'email_id': email_id.decode(),
                'sender': sender,
                'subject': subject,
                'date': date,
                'body': body[:500],  # Pierwsze 500 znaków
                'ticket_number': ticket_number,
                'full_body': body
            }
            
            emails_data.append(email_info)
            
            current_app.logger.info(f"Odczytano email od {sender}, numer zgłoszenia: {ticket_number}")
        
        mail.close()
        mail.logout()
        
        return emails_data
        
    except Exception as e:
        current_app.logger.error(f"Błąd odczytu emaili: {str(e)}")
        return []


def mark_as_read(email_id):
    """Oznacza email jako przeczytany"""
    mail = connect_to_mailbox()
    if not mail:
        return False
    
    try:
        mail.select('inbox')
        mail.store(email_id, '+FLAGS', '\\Seen')
        mail.close()
        mail.logout()
        return True
    except Exception as e:
        current_app.logger.error(f"Błąd oznaczania jako przeczytane: {str(e)}")
        return False