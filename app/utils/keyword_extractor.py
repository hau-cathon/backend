"""Keyword extraction and highlighting"""
import re
from collections import Counter


class KeywordExtractor:
    """Extracts and highlights keywords from text"""
    
    def __init__(self):
        # Słowa kluczowe kategorii
        self.keywords = {
            'priority_high': [
                'pilne', 'krytyczne', 'awaria', 'nie działa', 'błąd krytyczny',
                'przestał działać', 'totalna awaria', 'produkcja', 'klient', 
                'straty', 'blokuje', 'natychmiast'
            ],
            'priority_medium': [
                'problem', 'nie mogę', 'błąd', 'wolno', 'opóźnienie',
                'czasami', 'sporadycznie', 'należy naprawić'
            ],
            'priority_low': [
                'prośba', 'propozycja', 'pytanie', 'sugestia', 
                'gdy będzie czas', 'nie pilne', 'ulepszenie'
            ],
            'technical': [
                'serwer', 'baza danych', 'aplikacja', 'system', 'api',
                'backend', 'frontend', 'kod', 'deployment', 'hosting',
                'drukarka', 'komputer', 'laptop', 'sieć', 'wifi', 'internet'
            ],
            'user_action': [
                'zainstalować', 'naprawić', 'zaktualizować', 'sprawdzić',
                'zresetować', 'skonfigurować', 'dodać', 'usunąć', 'zmienić'
            ]
        }
        
        # Połącz wszystkie słowa kluczowe
        self.all_keywords = []
        for category, words in self.keywords.items():
            self.all_keywords.extend(words)
    
    def extract_keywords(self, text, top_n=10):
        """
        Wyciąga najważniejsze słowa kluczowe z tekstu
        
        Args:
            text: tekst do analizy
            top_n: ile słów kluczowych zwrócić
            
        Returns:
            lista słowników: [{'word': słowo, 'count': liczba wystąpień, 'category': kategoria}]
        """
        text_lower = text.lower()
        found_keywords = []
        
        # Szukaj każdego słowa kluczowego
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                # Użyj word boundary dla dokładnego dopasowania
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text_lower)
                
                if matches:
                    found_keywords.append({
                        'word': keyword,
                        'count': len(matches),
                        'category': category,
                        'positions': [m.start() for m in re.finditer(pattern, text_lower)]
                    })
        
        # Sortuj według liczby wystąpień
        found_keywords.sort(key=lambda x: x['count'], reverse=True)
        
        return found_keywords[:top_n]
    
    def highlight_keywords(self, text):
        """
        Generuje tekst z podświetlonymi słowami kluczowymi
        
        Args:
            text: tekst do podświetlenia
            
        Returns:
            lista słowników: [{'text': fragment, 'highlighted': bool, 'category': kategoria}]
        """
        text_lower = text.lower()
        highlights = []
        
        # Znajdź wszystkie pozycje słów kluczowych
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                for match in re.finditer(pattern, text_lower):
                    highlights.append({
                        'start': match.start(),
                        'end': match.end(),
                        'category': category,
                        'word': keyword
                    })
        
        # Sortuj według pozycji
        highlights.sort(key=lambda x: x['start'])
        
        # Usuń nakładające się highlighty
        filtered_highlights = []
        last_end = 0
        for h in highlights:
            if h['start'] >= last_end:
                filtered_highlights.append(h)
                last_end = h['end']
        
        # Buduj wynik
        result = []
        pos = 0
        
        for h in filtered_highlights:
            # Dodaj tekst przed highlightem
            if pos < h['start']:
                result.append({
                    'text': text[pos:h['start']],
                    'highlighted': False,
                    'category': None
                })
            
            # Dodaj highlight
            result.append({
                'text': text[h['start']:h['end']],
                'highlighted': True,
                'category': h['category']
            })
            
            pos = h['end']
        
        # Dodaj resztę tekstu
        if pos < len(text):
            result.append({
                'text': text[pos:],
                'highlighted': False,
                'category': None
            })
        
        return result
    
    def suggest_priority(self, text):
        """
        Sugeruje priorytet na podstawie słów kluczowych
        
        Returns:
            dict: {'priority': int (0-2), 'confidence': float, 'reason': str}
        """
        keywords = self.extract_keywords(text)
        
        priority_scores = {
            'priority_high': 0,
            'priority_medium': 0,
            'priority_low': 0
        }
        
        for kw in keywords:
            if kw['category'] in priority_scores:
                priority_scores[kw['category']] += kw['count']
        
        # Determine priority
        if priority_scores['priority_high'] > 0:
            priority = 2
            reason = "Wykryto słowa kluczowe wysokiego priorytetu"
            confidence = min(priority_scores['priority_high'] / 5, 1.0)
        elif priority_scores['priority_medium'] > priority_scores['priority_low']:
            priority = 1
            reason = "Wykryto słowa kluczowe średniego priorytetu"
            confidence = min(priority_scores['priority_medium'] / 3, 1.0)
        else:
            priority = 0
            reason = "Brak słów kluczowych wysokiego priorytetu"
            confidence = 0.5
        
        return {
            'priority': priority,
            'confidence': confidence,
            'reason': reason,
            'keyword_scores': priority_scores
        }
    
    def extract_entities(self, text):
        """
        Wyciąga encje z tekstu (numery, emaile, nazwy)
        
        Returns:
            dict: {'emails': [], 'phone_numbers': [], 'numbers': []}
        """
        # Email pattern
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        # Phone pattern (polski format)
        phones = re.findall(r'\b(?:\+48)?[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}\b', text)
        
        # Ticket numbers
        tickets = re.findall(r'#(\d+)|ZGL-(\d+)|Ticket[:\s]+(\d+)', text, re.IGNORECASE)
        ticket_numbers = [t for group in tickets for t in group if t]
        
        return {
            'emails': emails,
            'phone_numbers': phones,
            'ticket_numbers': ticket_numbers
        }
