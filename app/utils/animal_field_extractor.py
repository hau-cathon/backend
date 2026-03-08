"""Animal incident field extraction"""
import re


class AnimalFieldExtractor:
    """Extracts structured fields from animal incident descriptions"""
    
    def __init__(self):
        # Gatunki zwierząt - rozszerzone o formy liczby mnogiej i bez polskich znaków
        self.animals = {
            'pies': [
                'pies', 'psa', 'psem', 'psu', 'pieska', 'piesku', 'piesek', 'kundelek', 
                'szczeniak', 'szczeniaka',
                # Liczba mnoga
                'psy', 'psów', 'psom', 'psami', 'psach',
                # Bez polskich znaków
                'psow', 'psami'
            ],
            'kot': [
                'kot', 'kota', 'kotem', 'kotu', 'kotka', 'kotku', 'kotek', 'kocur', 
                'kociak', 'kociaka',
                # Liczba mnoga
                'koty', 'kotów', 'kotom', 'kotami', 'kotach',
                # Bez polskich znaków
                'kotow', 'kotami'
            ]
        }
        
        # Keywords indicating caller information
        self.caller_intro_keywords = [
            'nazywam się', 'jestem', 'mówi', 'dzwoni', 'zgłasza',
            'moje imię', 'moje nazwisko', 'ja jestem', 'mam na imie', 'mam na nazwisko',
            'imię i nazwisko', 'to jest', 'z tej strony', 'przedstawiam się',
            'mam na imię', 'ze mną', 'ze strony', 'zgłoszenie od', 'dzwonię w sprawie',
            'nazywa się', 'telef', 'kontakt do mnie', 'jestem do kontaktu',
            'pod numerem', 'można się ze mną skontaktować', 'można mnie znaleźć'
        ]
        
        # Words that exclude location/name detection (should not be part of address/name)
        self.location_exclusion_words = [
            'uniwersytet', 'uniwersytetu', 'szkoła', 'szkoły', 'kościół', 'kościoła',
            'sklep', 'sklepu', 'bank', 'banku', 'ratusz', 'ratusza'
        ]
        
        # Phone keywords
        self.phone_keywords = [
            'telefon', 'numer', 'nr', 'kontakt', 'dodzwonić', 'oddzwonić',
            'zadzwonić', 'numer telefonu', 'mój numer', 'mój telefon',
            'nr telefonu', 'kontakt do mnie', 'jestem pod numerem', 'pod numerem',
            'proszę dzwonić', 'można dzwonić', 'numer kontaktowy', 'tel',
            'komórka', 'kom', 'tel.', 'telefon:', 'numer:', 'kontakt:', 'nr:',
            'proszę oddzwonić', 'proszę zadzwonić', 'można się ze mną skontaktować',
            'jestem dostępny', 'jestem dostępna', 'jestem do kontaktu'
        ]
        
        # Słowa kluczowe dla lokalizacji
        self.location_keywords = [
            'ulica', 'ul.', 'ulicy', 'przy', 'w', 'na', 'obok', 'koło', 'niedaleko',
            'przed', 'za', 'park', 'skwer', 'plac', 'osiedle', 'dzielnica',
            'adres', 'znajduje się', 'jest', 'widać', 'al.', 'aleja', 'alei',
            'ulicą', 'rondo', 'rondzie', 'most', 'mostem', 'moście',
            'parking', 'parkingu', 'chodnik', 'chodniku', 'jezdnia', 'jezdni',
            'skrzyżowanie', 'skrzyżowaniu', 'róg', 'rogu', 'naprzeciwko',
            'vis-à-vis', 'vis a vis', 'między', 'pomiędzy', 'tuż przy', 'tuż obok',
            'zaraz przy', 'zaraz obok', 'blisko', 'w pobliżu', 'w okolicy',
            'lokalizacja', 'miejsce', 'miejscu', 'tam gdzie', 'widać go', 'widać ją',
            'znajduje', 'przebywa', 'leży', 'siedzi', 'stoi', 'biegnie'
        ]

        self.strong_location_keywords = [
            'ulica', 'ul.', 'ulicy', 'ulicą', 'aleja', 'alei', 'al.',
            'adres', 'lokalizacja', 'róg', 'skrzyżowanie', 'między',
            'park', 'plac', 'osiedle', 'skwer', 'rondo', 'most',
            'parking', 'parkingu', 'chodnik', 'chodniku', 'jezdnia', 'jezdni',
            'obok', 'koło', 'kolo', 'niedaleko', 'naprzeciwko', 'vis-à-vis', 'vis a vis'
        ]
        
        # Typy zdarzeń
        self.incident_types = {
            'zablakany': ['zbłąkany', 'zblakany', 'zagubiony', 'zgubił się', 'zgubiona', 'zgubiony', 'błąka się', 'błaka się', 'sam', 'sama', 'bez właściciela', 'bez opiekuna', 'wolno biega', 'włóczy się'],
            'ranny': [
                'ranny', 'ranna', 'ranne',
                'potrącony', 'potrącona', 'potrącone', 'zostało potrącone', 'został potrącony', 'została potrącona',
                'kontuzja', 'rana', 'ranę', 'rany', 'raną', 'ran', 'ma ranę',
                'krwawi', 'krwawienie', 'krew',
                'kuleje', 'kulejący', 'kulejąca',
                'nie może chodzić', 'nie może się ruszyć', 'nie chodzi', 'nie rusza się',
                'uraz', 'urazu', 'uszkodzenie',
                'chory', 'chora', 'chore', 'choruje',
                'słaby', 'słaba', 'słabe', 'osłabiony', 'osłabiona',
                'ugryziony', 'ugryziona', 'ugryzione', 'został ugryziony', 'została ugryziona',
                'leży', 'leżący', 'leżąca', 'leży i nie wstaje',
                'potrzebuje pomocy', 'wymaga pomocy', 'pomocy',
                'wypadek', 'po wypadku', 'wypadek samochodowy', 'przejechany', 'przejechana',
                'zraniony', 'zraniona', 'zranione'
            ],
            'agresywny': ['agresywny', 'agresywna', 'agresywne', 'atakuje', 'szczeka', 'gryzie', 'niebezpieczny', 'niebezpieczna', 'zagrożenie', 'zagraża', 'warczy', 'warczący'],
            'martwy': ['martwy', 'martwa', 'martwe', 'nie żyje', 'nieżyje', 'padł', 'padła', 'zwłoki', 'nie oddycha', 'zdechł', 'zdechła', 'nieżywy'],
            'zamkniety': ['zamknięty', 'zamknieta', 'zamknięta', 'uwięziony', 'uwięziona', 'uwiezione', 'w pułapce', 'nie może wyjść', 'trzymany', 'zablokowany', 'zablokowana'],
            'glodny': ['głodny', 'głodna', 'głodne', 'wychudzone', 'wychudzony', 'wychudzony', 'wyniszczony', 'wyniszczona', 'bez jedzenia', 'brak jedzenia', 'zaniedbany', 'zaniedbana', 'zaniedbane']
        }

        self.polish_number_words = {
            'zero': 0,
            'jeden': 1, 'jedna': 1, 'jedno': 1, 'jednego': 1, 'jednej': 1, 'jednemu': 1, 'jednym': 1, 'jedną': 1,
            'dwa': 2, 'dwie': 2, 'dwóch': 2, 'dwoch': 2, 'dwóm': 2, 'dwom': 2, 'dwoma': 2,
            'trzy': 3, 'trzech': 3, 'trzem': 3,
            'cztery': 4, 'czterech': 4, 'czterem': 4,
            'pięć': 5, 'piec': 5, 'pięciu': 5, 'pieciu': 5,
            'sześć': 6, 'szesc': 6, 'sześciu': 6, 'szesciu': 6,
            'siedem': 7, 'siedmiu': 7,
            'osiem': 8, 'ośmiu': 8, 'osmiu': 8,
            'dziewięć': 9, 'dziewiec': 9, 'dziewięciu': 9, 'dziewieciu': 9,
            'dziesięć': 10, 'dziesiec': 10, 'dziesięciu': 10, 'dziesieciu': 10,
        }

    def _replace_spoken_digits(self, text):
        if not text:
            return text

        output = text
        for word, number in self.polish_number_words.items():
            output = re.sub(r'\b' + re.escape(word) + r'\b', str(number), output, flags=re.IGNORECASE)
        return output

    def _strip_caller_intro_segments(self, text):
        if not text:
            return text

        cleaned = text
        caller_name = self.extract_caller_name(text)

        intro_phrases = [
            'nazywam się', 'mam na imię', 'mam na imie', 'z tej strony',
            'przedstawiam się', 'to jest', 'mówi', 'dzwoni', 'zgłasza',
            'moje imię to', 'jestem'
        ]

        if caller_name:
            for phrase in intro_phrases:
                pattern = rf'\b{re.escape(phrase)}\s+{re.escape(caller_name)}\b[,.:;\s]*'
                cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)

        generic_intro_patterns = [
            r'\b(?:nazywam się|mam na imię|mam na imie|z tej strony|przedstawiam się|moje imię to)\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+){0,2}[,.:;\s]*',
            r'\btutaj\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż]+){0,2}[,.:;\s]*',
        ]

        for pattern in generic_intro_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)

        return re.sub(r'\s+', ' ', cleaned).strip()

    def _clean_location_value(self, value):
        if not value:
            return None

        location = value.strip(' ,.;:-')
        location = re.sub(r'\s+', ' ', location)
        location = re.sub(r'^(?:na|w|przy|obok|koło|kolo)\s+', '', location, flags=re.IGNORECASE)

        invalid_starts = [
            'mam na imię', 'mam na imie', 'nazywam się', 'jestem', 'mówi',
            'dzwoni', 'zgłasza', 'proszę', 'bardzo', 'dzień dobry', 'witam'
        ]
        location_lower = location.lower()
        if any(location_lower.startswith(bad) for bad in invalid_starts):
            return None

        if len(location) < 3:
            return None

        return location

    def _extract_phone_from_text(self, text):
        patterns = [
            r'\+48[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
            r'\+48[\s.-]?\d{9}',
            r'\(\+?48\)[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
            r'\b48[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}\b',
            r'\b\d{3}[\s.-]\d{3}[\s.-]\d{3}\b',
            r'\b\d{9}\b',
            r'0048[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
            r'tel[.:\s]+\+?48?[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
            r'tel[.:\s]+\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
            r'numer[:\s]+\+?48?[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
            r'numer[:\s]+\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
            r'nr[.:\s]+\+?48?[\s.-]?\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
            r'nr[.:\s]+\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
            r'telefon[:\s]+\d{3}[\s.-]?\d{3}[\s.-]?\d{3}',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if not match:
                continue

            phone = re.sub(r'(?:tel|numer|nr|telefon)[.:\s]+', '', match.group(0), flags=re.IGNORECASE)
            digits = ''.join(re.findall(r'\d', phone))

            if len(digits) == 9:
                return f"{digits[:3]} {digits[3:6]} {digits[6:]}"
            if len(digits) in [11, 12]:
                local = digits[-9:]
                return f"+48 {local[:3]} {local[3:6]} {local[6:]}"
            if len(digits) == 10 and digits[0] == '0':
                local = digits[1:]
                return f"{local[:3]} {local[3:6]} {local[6:]}"

        return None
    
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
    
    def calculate_species_confidence(self, text):
        """
        Calculates confidence for species detection
        
        Returns:
            float: confidence score 0.0-1.0
        """
        text_lower = text.lower()
        matches = 0
        
        for species, keywords in self.animals.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    matches += 1
        
        # High confidence if species keywords found
        if matches >= 2:
            return 0.99
        elif matches == 1:
            return 0.95
        else:
            return 0.0
    
    def extract_location(self, text):
        """
        Wyciąga lokalizację z tekstu
        
        Returns:
            str: wykryta lokalizacja lub None
        """
        sanitized_text = self._strip_caller_intro_segments(text)
        text_lower = sanitized_text.lower()
        sentences = sanitized_text.split('.')
        
        # Szukaj zdań zawierających słowa kluczowe lokalizacji
        location_candidates = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            
            # Sprawdź czy zawiera słowa kluczowe lokalizacji
            if any(kw in sentence_lower for kw in self.strong_location_keywords):
                # Wyciągnij fragment z lokalizacją
                location_candidates.append(sentence.strip())
        
        # Wzorce dla konkretnych formatów adresów - naprawione dla długich nazw i numerów
        patterns = [
            r'(?:ulica|ul\.?|ulicy|ulicą)\s+([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9\-]+){0,5}(?:\s+\d+[a-z]?)?)(?=\s*[,.]|\s+obok|\s+niedaleko|\s+przy|\s+w\b|$)',
            r'(?:aleja|alei|al\.?)\s+([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9\-]+){0,5}(?:\s+\d+[a-z]?)?)(?=\s*[,.]|\s+obok|\s+niedaleko|\s+przy|\s+w\b|$)',
            r'(?:przy|na)\s+(?:ulicy|ulicą|ul\.?|alei|aleja)\s+([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+){0,4})\s+(\d+[a-z]?)',
            r'(?:park|plac|osiedle|skwer|rondo)\s+([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9\-]+){0,4})(?=\s*[,.]|$)',
            r'(?:na|przy|obok|koło|kolo)\s+(parkingu?|chodniku|jezdni|rondzie|moście|skwerze|placu|parku)(?:\s+([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż0-9\-]+){0,3}))?(?=\s*[,.]|$)',
            r'adres[:\s]+([^.,]+)',
            r'lokalizacja[:\s]+([^.,]+)',
            r'róg\s+(?:ulicy|ulicą)?\s*([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+){0,3})\s+i\s+([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+){0,3})(?=\s*[,.]|$)',
            r'skrzyżowanie\s+(?:ulicy|ulic)?\s*([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+){0,3})\s+(?:i|oraz|z)\s+([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+){0,3})(?=\s*[,.]|$)',
            r'między\s+(?:ulicą)?\s*([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+){0,3})\s+a\s+([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż\-]+){0,3})(?=\s*[,.]|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sanitized_text, re.IGNORECASE)
            if match:
                if match.lastindex and match.lastindex >= 2:
                    location = f"{match.group(1).strip()} {match.group(2).strip()}"
                else:
                    location = match.group(1).strip()

                location = re.sub(r'\s+i\s+\d+$', '', location)  # Remove "i 303" at end
                location = self._clean_location_value(location)
                if location:
                    return location
        
        # Jeśli nie znaleziono konkretnego adresu, zwróć pierwsze zdanie z lokalizacją
        # ale upewnij się, że to faktycznie adres, a nie powitanie
        if location_candidates:
            for candidate in location_candidates:
                candidate_lower = candidate.lower()
                # Skip greetings and introductions
                if any(greeting in candidate_lower for greeting in ['dzień dobry', 'cześć', 'halo', 'witam']):
                    continue
                # Skip if it's just a name introduction ("tutaj Jan Kowalski")
                if any(intro in candidate_lower for intro in ['tutaj', 'nazywam', 'mam na imię', 'mam na imie', 'jestem', 'z tej strony']):
                    continue
                if not any(kw in candidate_lower for kw in self.strong_location_keywords):
                    continue

                fragment_match = re.search(
                    r'(?:adres[:\s]+|lokalizacja[:\s]+|(?:na|przy|obok|koło|kolo)\s+)([^.,]{3,80})',
                    candidate,
                    re.IGNORECASE
                )
                extracted_fragment = fragment_match.group(1).strip() if fragment_match else candidate[:100]

                cleaned_candidate = self._clean_location_value(extracted_fragment)
                if cleaned_candidate and re.search(r'\b(?:pies|psa|psy|kot|kota|koty|zwierzę|zwierze)\b', cleaned_candidate, re.IGNORECASE):
                    cleaned_candidate = None
                if cleaned_candidate and cleaned_candidate.lower() in ['ulicy', 'ulica', 'alei', 'aleja']:
                    cleaned_candidate = None
                if cleaned_candidate:
                    return cleaned_candidate
        
        return None
    
    def calculate_location_confidence(self, text):
        """
        Calculates confidence for location extraction
        
        Returns:
            float: confidence score 0.0-1.0
        """
        text_for_location = self._strip_caller_intro_segments(text)
        text_lower = text_for_location.lower()
        
        # Wzorce dla konkretnych formatów adresów - rozszerzone dla confidence
        patterns = [
            r'(?:ulica|ul\.|ulicy|ulicą)\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s\d]+)',
            r'(?:aleja|alei|al\.)\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s\d]+)',
            r'(?:przy|na)\s+(?:ulicy|ulicą|ul\.|alei)?\s*([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s\d]+)',
            r'(?:park|plac|osiedle|skwer|rondo)\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)',
            r'adres[:\s]+([^.,]+)',
            r'lokalizacja[:\s]+([^.,]+)',
            r'róg\s+(?:ulicy)?\s*([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)\s+i\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)',
            r'skrzyżowanie\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)\s+(?:i|z)\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż\s]+)',
        ]
        
        # High confidence for structured addresses
        for pattern in patterns:
            match = re.search(pattern, text_for_location, re.IGNORECASE)
            if match:
                # Check if it includes street number
                if re.search(r'\d+', match.group(0)):
                    return 0.98  # Very high confidence
                else:
                    return 0.93  # Good confidence
        
        # Moderate confidence for general location keywords
        keyword_count = sum(1 for kw in self.strong_location_keywords if kw in text_lower)
        if keyword_count >= 2:
            return 0.85
        elif keyword_count == 1:
            return 0.75
        else:
            return 0.0
    
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
    
    def calculate_incident_type_confidence(self, text):
        """
        Calculates confidence for incident type detection
        
        Returns:
            float: confidence score 0.0-1.0
        """
        text_lower = text.lower()
        matches = 0
        
        for incident_type, keywords in self.incident_types.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    matches += 1
        
        # Higher confidence with more specific matches
        if matches >= 3:
            return 0.98
        elif matches == 2:
            return 0.94
        elif matches == 1:
            return 0.90
        else:
            return 0.0
    
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
    
    def extract_caller_name(self, text):
        """
        Extracts caller name from Polish text
        
        Returns:
            str: caller name or None
        """
        text_lower = text.lower()
        
        # Patterns for name extraction in Polish (with better boundaries)
        patterns = [
            # "Nazywam się Jan Kowalski"
            r'nazywam się\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
            # "Jestem Jan Kowalski" (but not after location words)
            r'(?<!obok\s)(?<!koło\s)(?<!niedaleko\s)jestem\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
            # "Tutaj Jan Kowalski" (word boundary for "tu" vs "tutaj")
            r'\btutaj\b\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
            # "Mówi Jan Kowalski" / "Dzwoni Jan Kowalski"
            r'(?:mówi|dzwoni)\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
            # "Moje imię to Jan"
            r'moje imię to\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)',
            # "Mam na imię Jan" / "Mam na nazwisko Kowalski"
            r'mam na (?:imię|imie)\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
            r'mam na nazwisko\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)',
            # At start: "Jan Kowalski zgłasza"
            r'^([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)(?:\s+zgłasza|\s+dzwoni)',
            # "Z tej strony Jan Kowalski"
            r'z tej strony\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
            # "Przedstawiam się Jan Kowalski"
            r'przedstawiam się\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
            # "Imię i nazwisko Jan Kowalski"
            r'imię i nazwisko[:\s]+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
            # "To jest Jan Kowalski" (but not after location words)
            r'(?<!obok\s)(?<!koło\s)to jest\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
            # "Zgłoszenie od Jan Kowalski" / "Zgłasza Jan Kowalski"
            r'(?:zgłoszenie od|zgłasza)\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
            # "Kontakt: Jan Kowalski" / "Osoba zgłaszająca: Jan Kowalski"
            r'(?:kontakt|osoba|zgłaszający|zgłaszająca)[:\s]+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Validate: name should be 2-50 characters
                # Check if it's not a common word that could be misidentified
                if 2 <= len(name) <= 50 and not self._is_common_word(name.lower()):
                    return name.title()  # Capitalize properly
        
        return None
    
    def _is_common_word(self, word):
        """Check if word is a common Polish word that shouldn't be a name"""
        common_words = [
            'pies', 'kot', 'zwierze', 'ulica', 'park', 'telefon', 'numer',
            'adres', 'dzwoni', 'zgłasza', 'kontakt', 'sprawa', 'pomocy',
            'pan', 'pani', 'bardzo', 'proszę', 'dziękuję', 'uniwersytet',
            'uniwersytetu', 'gnaskiego', 'gdańskiego', 'szkoła', 'szkoły',
            'kościół', 'kościoła', 'sklep', 'sklepu'
        ]
        word_lower = word.lower()
        # Check exact match or if word starts with university/location name
        if word_lower in common_words:
            return True
        # Check if it's an institution name (contains specific keywords)
        if any(inst in word_lower for inst in ['uniwersytet', 'szkoł', 'kości', 'sklep']):
            return True
        return False
    
    def calculate_caller_name_confidence(self, text):
        """
        Calculate confidence for caller name extraction
        
        Returns:
            float: confidence 0.0-1.0
        """
        name = self.extract_caller_name(text)
        if not name:
            return 0.0
        
        text_lower = text.lower()
        
        # Very high confidence phrases
        very_high_conf_keywords = ['nazywam się', 'mam na imię', 'mam na nazwisko', 'imię i nazwisko']
        high_conf_keywords = ['jestem', 'tu', 'mówi', 'dzwoni', 'przedstawiam się', 'z tej strony']
        medium_conf_keywords = ['zgłasza', 'kontakt', 'zgłoszenie od']
        
        # Check if full name (name + surname)
        is_full_name = ' ' in name.strip() and len(name.split()) >= 2
        
        if any(kw in text_lower for kw in very_high_conf_keywords):
            return 0.98 if is_full_name else 0.90
        elif any(kw in text_lower for kw in high_conf_keywords):
            return 0.95 if is_full_name else 0.85
        elif any(kw in text_lower for kw in medium_conf_keywords):
            return 0.88 if is_full_name else 0.78
        
        return 0.70  # Lower confidence if inferred
    
    def extract_phone_number(self, text):
        """
        Extracts phone number from Polish text
        
        Returns:
            str: phone number or None
        """
        candidates = [text, self._replace_spoken_digits(text)]
        for candidate_text in candidates:
            phone = self._extract_phone_from_text(candidate_text)
            if phone:
                return phone

        spoken_digit_tokens = re.findall(r'\b\d\b', self._replace_spoken_digits(text))
        if len(spoken_digit_tokens) >= 9:
            maybe_phone = ''.join(spoken_digit_tokens[:9])
            return f"{maybe_phone[:3]} {maybe_phone[3:6]} {maybe_phone[6:]}"

        return None
    
    def calculate_phone_confidence(self, text):
        """
        Calculate confidence for phone number extraction
        
        Returns:
            float: confidence 0.0-1.0
        """
        phone = self.extract_phone_number(text)
        if not phone:
            return 0.0
        
        text_lower = text.lower()
        
        # Check for explicit phone keywords
        explicit_keywords = ['telefon', 'numer telefonu', 'mój numer', 'nr telefonu', 'kontakt', 'tel']
        has_explicit_keyword = any(kw in text_lower for kw in explicit_keywords)
        
        # Check for contextual phone keywords
        contextual_keywords = ['oddzwonić', 'zadzwonić', 'dodzwonić', 'proszę dzwonić', 'pod numerem']
        has_contextual_keyword = any(kw in text_lower for kw in contextual_keywords)
        
        # Check format quality
        has_country_code = '+48' in phone or (phone and phone.strip().startswith('48'))
        is_formatted = bool(re.search(r'\d{3}\s\d{3}\s\d{3}', phone))
        
        # Calculate confidence based on multiple factors
        if has_explicit_keyword:
            if has_country_code:
                return 0.98  # Very high confidence
            elif is_formatted:
                return 0.95  # High confidence with formatting
            else:
                return 0.92  # High confidence
        elif has_contextual_keyword:
            if has_country_code or is_formatted:
                return 0.90  # Good confidence
            else:
                return 0.85  # Decent confidence
        else:
            # Pattern matched but no keywords
            if has_country_code or is_formatted:
                return 0.80  # Moderate confidence
            else:
                return 0.70  # Lower confidence
        
        return 0.70
    
    def extract_all_fields(self, text):
        """
        Ekstrachuje wszystkie pola naraz
        
        Returns:
            dict: {
                'species': 'pies' | 'kot' | None,
                'location': str | None,
                'incident_types': list,
                'description': str,
                'animal_count': int,
                'full_text': str
            }
        """
        return {
            'species': self.extract_animal_species(text),
            'location': self.extract_location(text),
            'incident_types': self.extract_incident_type(text),
            'description': self.extract_description(text),
            'animal_count': self.extract_animal_count(text),
            'full_text': text
        }
    
    def extract_all_fields_with_confidence(self, text):
        """
        Ekstrachuje wszystkie pola wraz z confidence scores
        
        Returns:
            dict: {
                'fields': {
                    'species': {'value': str, 'confidence': float},
                    'location': {'value': str, 'confidence': float},
                    'incident_types': {'value': list, 'confidence': float},
                    'description': {'value': str, 'confidence': float},
                    'caller_name': {'value': str, 'confidence': float},
                    'caller_phone': {'value': str, 'confidence': float},
                    'animal_count': {'value': int, 'confidence': float}
                },
                'overall_confidence': float,
                'should_auto_fill': bool
            }
        """
        species = self.extract_animal_species(text)
        location = self.extract_location(text)
        incident_types = self.extract_incident_type(text)
        description = self.extract_description(text)
        caller_name = self.extract_caller_name(text)
        caller_phone = self.extract_phone_number(text)
        animal_count = self.extract_animal_count(text)
        
        species_conf = self.calculate_species_confidence(text) if species else 0.0
        location_conf = self.calculate_location_confidence(text) if location else 0.0
        incident_conf = self.calculate_incident_type_confidence(text) if incident_types else 0.0
        caller_name_conf = self.calculate_caller_name_confidence(text) if caller_name else 0.0
        caller_phone_conf = self.calculate_phone_confidence(text) if caller_phone else 0.0
        animal_count_conf = self.calculate_animal_count_confidence(text)
        
        # Description confidence is high if we have text
        description_conf = 0.98 if description and len(description.strip()) > 10 else 0.7
        
        # Calculate overall confidence (weighted average)
        # Species and incident type are more important for animal incidents
        # Location is less critical early in call (caller often provides it later)
        # Caller info doesn't affect animal incident confidence
        weights = {
            'species': 0.40,      # Increased from 0.35
            'location': 0.15,     # Decreased from 0.30 (location often comes later)
            'incident_types': 0.30,  # Increased from 0.25
            'description': 0.15   # Increased from 0.10
        }
        
        overall_confidence = (
            species_conf * weights['species'] +
            location_conf * weights['location'] +
            incident_conf * weights['incident_types'] +
            description_conf * weights['description']
        )
        
        return {
            'fields': {
                'species': {
                    'value': species,
                    'confidence': species_conf
                },
                'location': {
                    'value': location,
                    'confidence': location_conf
                },
                'incident_types': {
                    'value': incident_types,
                    'confidence': incident_conf
                },
                'description': {
                    'value': description,
                    'confidence': description_conf
                },
                'caller_name': {
                    'value': caller_name,
                    'confidence': caller_name_conf
                },
                'caller_phone': {
                    'value': caller_phone,
                    'confidence': caller_phone_conf
                },
                'animal_count': {
                    'value': animal_count,
                    'confidence': animal_count_conf
                }
            },
            'overall_confidence': overall_confidence,
            'should_auto_fill': overall_confidence >= 0.95,
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
    
    def extract_animal_count(self, text):
        """
        Wykrywa ilość zwierząt w opisie
        
        Returns:
            int: liczba zwierząt lub 1 (domyślnie)
        """
        text_lower = text.lower()
        text_with_digits = self._replace_spoken_digits(text_lower)

        explicit_number_patterns = [
            r'\b(\d{1,2})\s+(?:[a-ząćęłńóśźż\-]+\s+){0,2}(?:psy|pies|psów|psami|psach|koty|kot|kotów|kotami|kotach|zwierzęta|zwierzeta|zwierząt|zwierzat)\b',
            r'\b(?:grupa|stado|gromada)\s+(\d{1,2})\s+(?:psy|psów|koty|kotów|zwierząt|zwierzat)\b',
            r'\b(\d{1,2})\s+sztuk\b',
        ]

        for pattern in explicit_number_patterns:
            match = re.search(pattern, text_with_digits)
            if match:
                return max(1, int(match.group(1)))

        number_word_values = sorted(set(self.polish_number_words.values()), reverse=True)
        animal_context = r'(?:psy|pies|psów|psami|psach|koty|kot|kotów|kotami|kotach|zwierzęta|zwierzeta|zwierząt|zwierzat)'
        for value in number_word_values:
            if value == 0:
                continue
            if re.search(rf'\b{value}\s+(?:[a-ząćęłńóśźż\-]+\s+){{0,2}}{animal_context}\b', text_with_digits):
                return value

        if re.search(r'\b(?:para|parę|pare)\b', text_lower):
            return 2

        multiple_keywords = [
            'kilka', 'kilku', 'wiele', 'wielu',
            'dużo', 'duzo', 'mnóstwo', 'mnostwo', 'grupa', 'grupy', 'stado',
            'sporo', 'masa', 'masy', 'gromada', 'zatrzęsienie'
        ]

        if any(kw in text_lower for kw in multiple_keywords):
            return 3

        return 1
    
    def calculate_animal_count_confidence(self, text):
        """
        Calculates confidence for animal count detection
        
        Returns:
            float: confidence 0.0-1.0
        """
        text_lower = text.lower()
        text_with_digits = self._replace_spoken_digits(text_lower)

        if re.search(r'\b\d{1,2}\s+(?:[a-ząćęłńóśźż\-]+\s+){0,2}(?:psy|pies|psów|psami|koty|kot|kotów|kotami|zwierz)', text_with_digits):
            return 0.95

        if re.search(r'\b(?:1|2|3|4|5|6|7|8|9|10)\s+(?:psy|pies|psów|koty|kot|kotów|zwierzęta|zwierzeta|zwierząt|zwierzat)\b', text_with_digits):
            return 0.92

        if re.search(r'\b(?:para|parę|pare)\b', text_lower):
            return 0.90

        multiple_keywords = ['kilka', 'kilku', 'wiele', 'wielu', 'dużo', 'duzo', 'grupa', 'grupy', 'stado', 'sporo']
        if any(kw in text_lower for kw in multiple_keywords):
            return 0.85

        return 0.60
