# Speech-to-Text Backend API

Backend Flask z funkcjonalnością Speech-to-Text (Whisper), analizą NLP i detekcją duplikatów.

## Nowe funkcje

### 1. **Speech-to-Text (STT)**
- Transkrypcja audio używając Whisper (OpenAI)
- REST API dla uploadu plików
- WebSocket dla streamingu audio w czasie rzeczywistym
- Wsparcie formatów: WAV, MP3, OGG, WEBM, M4A, FLAC

### 2. **Analiza NLP**
- Wykrywanie słów kluczowych
- Podświetlanie ważnych fragmentów tekstu
- Sugerowanie priorytetu na podstawie treści
- Wyciąganie encji (email, telefon, numery zgłoszeń)

### 3. **Detekcja duplikatów**
- Cosine similarity między zgłoszeniami
- Analiza w zadanym okresie (domyślnie 7 dni)
- Konfigurowalne progi podobieństwa

### 4. **Dynamiczne formularze**
- Automatyczne generowanie pól formularza
- Uzupełnianie wartości na podstawie transkrypcji
- Integracja z analizą ML

## Instalacja

### Wymagania systemowe
- Python 3.8+
- FFmpeg (dla konwersji audio)

#### Instalacja FFmpeg:

**Windows:**
```powershell
# Chocolatey
choco install ffmpeg

# Lub pobierz z https://ffmpeg.org/download.html
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

### Instalacja pakietów Python

```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
python run.py
```

Aplikacja będzie dostępna na `http://localhost:5000`

## Endpointy API

### Speech-to-Text

#### 1. Upload pliku audio
```bash
POST /api/stt/transcribe
Content-Type: multipart/form-data

curl -X POST http://localhost:5000/api/stt/transcribe \
  -F "audio=@recording.wav" \
  -F "language=pl" \
  -F "analyze=true"
```

**Odpowiedź:**
```json
{
  "status": "success",
  "transcription": "Mam problem z drukarką, nie drukuje dokumentów...",
  "language": "pl",
  "segments": [...],
  "analysis": {
    "keywords": [
      {"word": "problem", "count": 1, "category": "priority_medium"},
      {"word": "drukarka", "count": 1, "category": "technical"}
    ],
    "highlighted_text": [...],
    "priority_suggestion": {
      "priority": 1,
      "confidence": 0.7,
      "reason": "Wykryto słowa kluczowe średniego priorytetu"
    },
    "entities": {
      "emails": [],
      "phone_numbers": [],
      "ticket_numbers": []
    }
  }
}
```

#### 2. Pełna analiza
```bash
POST /api/stt/analyze-full
Content-Type: multipart/form-data

curl -X POST http://localhost:5000/api/stt/analyze-full \
  -F "audio=@recording.wav" \
  -F "language=pl"
```

**Zwraca:** transkrypcję + analizę NLP + priorytet ML + sugerowany formularz

#### 3. Analiza tekstu (bez audio)
```bash
POST /api/stt/text-analyze
Content-Type: application/json

curl -X POST http://localhost:5000/api/stt/text-analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Pilny problem z serwerem produkcyjnym"}'
```

### WebSocket (Streaming Audio)

```javascript
// Frontend - przykład
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected');
  
  // Rozpocznij nagrywanie
  socket.emit('start_recording');
  
  // Wysyłaj chunki audio
  socket.emit('audio_chunk', {
    audio: audioDataBase64,
    format: 'wav',
    final: false
  });
  
  // Ostatni chunk
  socket.emit('audio_chunk', {
    audio: audioDataBase64,
    format: 'wav',
    final: true
  });
});

socket.on('transcription_complete', (data) => {
  console.log('Transkrypcja:', data.transcription);
  console.log('Analiza:', data.analysis);
});

socket.on('error', (data) => {
  console.error('Błąd:', data.error);
});
```

### Detekcja duplikatów

```bash
# Sprawdź duplikaty dla zgłoszenia
GET /api/duplicates/check/<issue_id>?days=7&threshold=0.7

curl "http://localhost:5000/api/duplicates/check/507f1f77bcf86cd799439011?threshold=0.7"
```

### Dynamiczne formularze

```bash
# Wygeneruj formularz na podstawie transkrypcji
POST /api/form/generate

curl -X POST http://localhost:5000/api/form/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mam problem z drukarką...",
    "priority": "medium",
    "keywords": ["problem", "drukarka"]
  }'
```

**Odpowiedź:**
```json
{
  "status": "success",
  "form": {
    "fields": [
      {
        "name": "title",
        "label": "Tytuł zgłoszenia",
        "type": "text",
        "required": true,
        "value": "Mam problem z drukarką"
      },
      {
        "name": "description",
        "label": "Opis",
        "type": "textarea",
        "required": true,
        "value": "Mam problem z drukarką..."
      },
      ...
    ]
  }
}
```

### Priorytet ML

```bash
POST /api/model/predict

curl -X POST http://localhost:5000/api/model/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Awaria systemu produkcyjnego"}'
```

## Konfiguracja

Utwórz plik `.env` w głównym katalogu:

```env
# Flask
SECRET_KEY=your-secret-key
DEBUG=True
HOST=0.0.0.0
PORT=5000

# MongoDB
MONGODB_SETTINGS=mongodb://localhost:27017/your_db

# JWT
JWT_SECRET_KEY=your-jwt-secret

# CORS
CORS_ORIGINS=*

# STT Model (tiny, base, small, medium, large)
WHISPER_MODEL_SIZE=base
```

## Modele Whisper

Dostępne rozmiary modeli:
- `tiny` - najszybszy, najmniej dokładny (~1GB RAM)
- `base` - szybki, dobry do demo (~1GB RAM) **← DOMYŚLNY**
- `small` - wolniejszy, bardziej dokładny (~2GB RAM)
- `medium` - jeszcze wolniejszy, bardzo dokładny (~5GB RAM)
- `large` - najwolniejszy, najbardziej dokładny (~10GB RAM)

## Struktura projektu

```
backend/
├── app/
│   ├── models/           # Modele MongoDB
│   ├── routes/           # Endpointy API
│   │   ├── stt_routes.py      # STT endpoints
│   │   ├── form_routes.py     # Formularze
│   │   ├── duplicate_routes.py # Duplikaty
│   │   └── model_routes.py    # ML priorytet
│   ├── utils/           # Narzędzia
│   │   ├── speech_to_text.py    # Whisper STT
│   │   ├── keyword_extractor.py # NLP
│   │   ├── duplicate_detector.py # Cosine similarity
│   │   ├── websocket_handler.py # WebSocket
│   │   └── model/              # Modele ML
│   └── __init__.py
├── requirements.txt
├── run.py
└── README_STT.md
```

## Testowanie

### Test transkrypcji

```bash
# Nagraj audio w przeglądarce lub użyj narzędzi
# Windows: Sound Recorder
# Mac: QuickTime
# Linux: arecord

# Wyślij do API
curl -X POST http://localhost:5000/api/stt/transcribe \
  -F "audio=@test_recording.wav" \
  -F "language=pl"
```

### Frontend - nagrywanie w przeglądarce

```javascript
// Przykład prostego recordera
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const mediaRecorder = new MediaRecorder(stream);
    const chunks = [];
    
    mediaRecorder.ondataavailable = (e) => {
      chunks.push(e.data);
    };
    
    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: 'audio/wav' });
      
      const formData = new FormData();
      formData.append('audio', blob, 'recording.wav');
      formData.append('language', 'pl');
      formData.append('analyze', 'true');
      
      const response = await fetch('http://localhost:5000/api/stt/transcribe', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      console.log(result);
    };
    
    mediaRecorder.start();
    
    // Zatrzymaj po 5 sekundach
    setTimeout(() => mediaRecorder.stop(), 5000);
  });
```

## Troubleshooting

### Błąd: "No module named 'whisper'"
```bash
pip install openai-whisper
```

### Błąd: "FFmpeg not found"
Zainstaluj FFmpeg (zobacz sekcję Instalacja)

### Wolna transkrypcja
- Użyj mniejszego modelu (`tiny` lub `base`)
- Rozważ użycie GPU (CUDA)

### WebSocket nie działa
- Sprawdź CORS
- Upewnij się że klient używa poprawnego URL
- Sprawdź czy port 5000 nie jest zablokowany

## Produkcja

### Z Gunicorn + eventlet (dla WebSocket)

```bash
pip install eventlet gunicorn

gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 run:app
```

### Docker

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:5000", "run:app"]
```
