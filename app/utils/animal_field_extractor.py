"""Animal incident field extraction"""
import re


class AnimalFieldExtractor:
    """Extracts structured fields from animal incident descriptions"""
    
    def __init__(self):
        # Gatunki zwierząt
        self.animals = {
            'pies': ['pies', 'psa', 'psem', 'psu', 'pieska', 'piesku', 'piesek', 'kundelek', 'szczeniak', 'szczeniaka'],
            'kot': ['kot', 'kota', 'kotem', 'kotu', 'kotka', 'kotku', 'kotek', 'kocur', 'kociak', 'kociaka']
        }
        
        # Słowa kluczowe dla lokalizacji
        self.location_keywords = [
            'ulica', 'ul.', 'ulicy', 'przy', 'w', 'na', 'obok', 'koło', 'niedaleko',
            'przed', 'za', 'park', 'skwer', 'plac', 'osiedle', 'dzielnica',
            'adres', 'znajduje się', 'jest', 'widać'
        ]
        
        # Typy zdarzeń
        self.incident_types = {
            'zablakany': ['zbłąkany', 'zblakany', 'zagubiony', 'zgubił się', 'zgubiona', 'zgubiony', 'błąka się', 'błaka się', 'sam', 'sama', 'bez właściciela', 'bez opiekuna'],
            'ranny': ['ranny', 'ranna', 'ranne', 'potrącony', 'potrącona', 'kontuzja', 'rana', 'krwawi', 'kuleje', 'nie może chodzić', 'uraz'],
            'agresywny': ['agresywny', 'agresywna', 'atakuje', 'szczeka', 'gryzie', 'niebezpieczny', 'niebezpieczna', 'zagrożenie'],
            'martwy': ['martwy', 'martwa', 'martwe', 'nie żyje', 'nieżyje', 'padł', 'padła', 'zwłoki', 'nie oddycha'],
            'zamkniety': ['zamknięty', 'zamknieta', 'uwięziony', 'uwiezione', 'w pułapce', 'nie może wyjść', 'trzymany'],
            'glodny': ['głodny', 'głodna', 'głodne', 'wychudzone', 'wychudzony', 'wyniszczony', 'bez jedzenia', 'brak jedzenia']
        }
    
    def extract_animal_species(self, text):
        """
        Wykrywa gatunek zwierzęcia w tekście
        
        Returns:
            str: 'pies', 'kot' lub None
        """
        text_lower = text.lower()
        
        for species, keywords in self.animals.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    return species
        
        return None
    
    def extract_location(self, text):
        """
        Wyciąga lokalizację z tekstu
        
        Returns:
            str: wykryta lokalizacja lub None
        """
        text_lower = text.lower()
        sentences = text.split('.')
        
        # Szukaj zdań zawierających słowa kluczowe lokalizacji
        location_candidates = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            
            # Sprawdź czy zawiera słowa kluczowe lokalizacji
            if any(kw in sentence_lower for kw in self.location_keywords):
                # Wyciągnij fragment z lokalizacją
                location_candidates.append(sentence.strip())
        
        # Wzorce dla konkretnych formatów adresów
        patterns = [
            r'(?:ulica|ul\.|ulicy)\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+?)(?:\s+\d+)?(?:\.|,|$)',
            r'(?:przy|na|w)\s+(?:ulicy|ul\.)?\s*([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+?)(?:\s+\d+)?(?:\.|,|$)',
            r'(?:park|plac|osiedle)\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+?)(?:\.|,|$)',
            r'adres[:\s]+([^.,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Jeśli nie znaleziono konkretnego adresu, zwróć pierwsze zdanie z lokalizacją
        if location_candidates:
            return location_candidates[0][:100]  # Maksymalnie 100 znaków
        
        return None
    
    def extract_incident_type(self, text):
        """
        Określa typ zdarzenia
        
        Returns:
            list: lista typów zdarzeń ['zablakany', 'ranny', ...]
        """
        text_lower = text.lower()
        detected_types = []
        
        for incident_type, keywords in self.incident_types.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    if incident_type not in detected_types:
                        detected_types.append(incident_type)
                    break
        
        return detected_types
    
    def extract_description(self, text):
        """
        Ekstrachuje opis zdarzenia (bez lokalizacji)
        
        Returns:
            str: opis zdarzenia
        """
        # Usuń zdania z lokalizacją
        sentences = text.split('.')
        description_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            
            # Pomiń zdania które są głównie lokalizacją
            location_word_count = sum(1 for kw in self.location_keywords if kw in sentence_lower)
            total_words = len(sentence.split())
            
            # Jeśli mniej niż 30% słów to lokalizacja, dołącz do opisu
            if total_words == 0 or location_word_count / total_words < 0.3:
                if sentence.strip():
                    description_sentences.append(sentence.strip())
        
        description = '. '.join(description_sentences)
        if description and not description.endswith('.'):
            description += '.'
        
        return description if description else text
    
    def extract_all_fields(self, text):
        """
        Ekstrachuje wszystkie pola naraz
        
        Returns:
            dict: {
                'species': 'pies' | 'kot' | None,
                'location': str | None,
                'incident_types': list,
                'description': str,
                'full_text': str
            }
        """
        return {
            'species': self.extract_animal_species(text),
            'location': self.extract_location(text),
            'incident_types': self.extract_incident_type(text),
            'description': self.extract_description(text),
            'full_text': text
        }
    
    def get_species_label(self, species):
        """Zwraca label dla gatunku"""
        labels = {
            'pies': 'Pies',
            'kot': 'Kot'
        }
        return labels.get(species, 'Nieokreślony')
    
    def get_incident_type_label(self, incident_type):
        """Zwraca label dla typu zdarzenia"""
        labels = {
            'zablakany': 'Zwierzę zbłąkane',
            'ranny': 'Zwierzę ranne',
            'agresywny': 'Zwierzę agresywne',
            'martwy': 'Zwierzę martwe',
            'zamkniety': 'Zwierzę zamknięte/uwięzione',
            'glodny': 'Zwierzę głodne/zaniedbane'
        }
        return labels.get(incident_type, incident_type)
