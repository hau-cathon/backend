# System wykrywania duplikatów zgłoszeń

## Przegląd implementacji

System automatycznie wykrywa potencjalne duplikaty zgłoszeń używając algorytmu TF-IDF i podobieństwa cosinusowego.

## Backend

### Endpoint API
```
GET /api/duplicates/check/<issue_id>?days=7&threshold=0.7
```

**Parametry:**
- `issue_id` - ID zgłoszenia lub ticket_number
- `days` (opcjonalny) - ile dni wstecz sprawdzać (domyślnie: 7)
- `threshold` (opcjonalny) - próg podobieństwa 0-1 (domyślnie: 0.7)

**Przykładowa odpowiedź:**
```json
{
  "status": "success",
  "issue_id": "69ad58db177139cba8bf01fa",
  "ticket_number": "#AH-TEST-001",
  "duplicates_found": 1,
  "duplicates": [
    {
      "id": "69ad58db177139cba8bf01fb",
      "event_type": "bezdomne_zwierze",
      "species": "pies",
      "incident_address": "ul. Polna 18, Warszawa",
      "description": "Pies bez właściciela przy ruchliwej ulicy...",
      "status": "open",
      "urgency": true,
      "created_at": "2026-03-08T12:30:00",
      "similarity": 0.89,
      "similarity_percent": 89.5
    }
  ],
  "search_params": {
    "days_back": 7,
    "threshold": 0.7,
    "threshold_percent": 70
  }
}
```

### Pliki backendu
- `app/utils/duplicate_detector.py` - logika wykrywania duplikatów (TF-IDF + cosine similarity)
- `app/routes/duplicate_routes.py` - endpointy API
- `app/models/issue_duplicate.py` - model do śledzenia połączonych zgłoszeń
- `create_sample_issues.py` - skrypt do tworzenia testowych zgłoszeń

## Frontend

### Serwis
**Plik:** `services/duplicates.service.ts`

```typescript
// Sprawdzenie duplikatów dla zgłoszenia
const duplicates = await duplicatesService.checkDuplicates(issueId, 7, 0.7);

// Porównanie dwóch zgłoszeń
const result = await duplicatesService.compareIssues(issueId1, issueId2);
```

### Komponent szczegółów zgłoszenia
**Plik:** `app/(tabs)/tickets/[id].tsx`

#### Zmiany:
1. **Import serwisu duplikatów:**
   ```typescript
   import { duplicatesService } from '../../../services/duplicates.service';
   import { RelatedTicketPreview } from '../../../constants/constants';
   ```

2. **Nowe stany:**
   ```typescript
   const [duplicates, setDuplicates] = useState<RelatedTicketPreview[]>([]);
   const [duplicatesLoading, setDuplicatesLoading] = useState(false);
   ```

3. **Funkcja pobierania duplikatów:**
   ```typescript
   const loadDuplicates = useCallback(async () => {
     if (!ticket?.id) return;
     try {
       setDuplicatesLoading(true);
       const found = await duplicatesService.checkDuplicates(ticket.id, 7, 0.7);
       setDuplicates(found);
     } catch (err: any) {
       console.error('Failed to load duplicates:', err);
       setDuplicates([]);
     } finally {
       setDuplicatesLoading(false);
     }
   }, [ticket?.id]);
   ```

4. **useEffect do automatycznego pobierania:**
   ```typescript
   useEffect(() => { 
     if (ticket?.id) void loadDuplicates(); 
   }, [ticket?.id, loadDuplicates]);
   ```

5. **Sekcja UI z alertem o duplikatach:**
   - Wyświetla się między sekcją "Grafika i filmy" a "Historia komunikacji"
   - Pokazuje liczbę znalezionych duplikatów
   - Wyświetla podgląd pierwszych 3 duplikatów z:
     - Numerem zgłoszenia
     - Opisem
     - Procentem podobieństwa
     - Lokalizacją
   - Kliknięcie otwiera `MergeDuplicatesModal`

### Istniejące komponenty
- **MergeDuplicatesModal** - gotowy modal do przeglądania i scalania duplikatów
- **TicketCard** - karta zgłoszenia z alertem o duplikacie (już obsługuje `duplicateAlert`)

## Użycie

### 1. Przygotowanie danych testowych

```bash
cd backend

# Stwórz przykładowe zgłoszenia (z duplikatami)
py -3.11 create_sample_issues.py --clear

# Lub dodaj bez czyszczenia
py -3.11 create_sample_issues.py
```

To utworzy 6 testowych zgłoszeń, w tym:
- #AH-TEST-001 i #AH-TEST-002 - podobne zgłoszenia o bezdomnym psie (~89% podobieństwa)
- #AH-TEST-003 i #AH-TEST-004 - podobne zgłoszenia o kocie na balkonie (~85% podobieństwa)
- #AH-TEST-005 - potrącony pies (brak duplikatów)
- #AH-TEST-006 - zaniedbany koń (brak duplikatów)

### 2. Testowanie API

```bash
# Sprawdź duplikaty dla zgłoszenia
curl http://localhost:5000/api/duplicates/check/<issue_id>

# Z parametrami
curl "http://localhost:5000/api/duplicates/check/<issue_id>?days=14&threshold=0.6"

# Porównaj dwa zgłoszenia
curl -X POST http://localhost:5000/api/duplicates/compare \
  -H "Content-Type: application/json" \
  -d '{"issue_id_1": "...", "issue_id_2": "..."}'
```

### 3. Testowanie na frontendzie

1. Uruchom backend (jeśli nie jest uruchomiony):
   ```bash
   cd backend
   py -3.11 run.py
   ```

2. Uruchom frontend:
   ```bash
   cd frontend/haucaton
   npm run web
   ```

3. Otwórz szczegóły zgłoszenia:
   - Przejdź do listy zgłoszeń (zakładka Tickets)
   - Kliknij na jedno ze zgłoszeń testowych (#AH-TEST-001 lub #AH-TEST-003)
   - Powinien pojawić się fioletowy alert z napisem "Wykryto X potencjalnych duplikatów"

4. Przejrzyj duplikaty:
   - Kliknij na alert
   - Otworzy się modal z listą potencjalnych duplikatów
   - Możesz oznaczyć je do scalenia lub odrzucenia

## Parametry konfiguracji

### Próg podobieństwa (threshold)
- **0.7 (70%)** - domyślna wartość, dobra równowaga
- **0.6-0.65** - więcej wyników, więcej false positives
- **0.75-0.8** - mniej wyników, bardziej restrykcyjne

### Okno czasowe (days)
- **7 dni** - domyślna wartość
- **14-30 dni** - dla długich spraw
- **1-3 dni** - dla pilnych zgłoszeń

## Algorytm wykrywania

System porównuje zgłoszenia na podstawie:
1. **event_type** - typ zdarzenia
2. **species** - gatunek zwierzęcia
3. **incident_address** - adres zdarzenia
4. **description** - opis zgłoszenia
5. **options** - dodatkowe opcje
6. **urgency** - pilność (tak/nie)

Używa algorytmu TF-IDF (Term Frequency-Inverse Document Frequency) do wektoryzacji tekstów i podobieństwa cosinusowego do obliczenia współczynnika podobieństwa.

## Rozszerzenia i ulepszenia (opcjonalne)

### Przyszłe możliwości:
1. **Automatyczne scalanie** - przy bardzo wysokim podobieństwie (>95%)
2. **Powiadomienia** - alert dla operatora o nowych duplikatach
3. **Machine Learning** - uczenie się z historii scalonych/odrzuconych duplikatów
4. **Geolokalizacja** - uwzględnienie odległości geograficznej
5. **Więcej języków** - polskie stopwords dla lepszych wyników

## Troubleshooting

### Backend nie znajduje duplikatów
- Sprawdź czy są zgłoszenia w bazie danych
- Obniż threshold (np. do 0.6)
- Zwiększ days (np. do 14 lub 30)

### Frontend nie wyświetla alertu
- Sprawdź console w przeglądarce (F12)
- Sprawdź czy backend odpowiada: `http://localhost:5000/api/duplicates/check/<issue_id>`
- Sprawdź czy CORS jest włączony na backendzie

### Błędy sklearn
- Upewnij się, że zainstalowane są pakiety:
  ```bash
  pip install scikit-learn numpy
  ```
