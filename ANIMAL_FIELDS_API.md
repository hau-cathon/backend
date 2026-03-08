# Przykłady wywołań API dla zgłoszeń zwierzęcych

## 1. Transkrypcja z analizą pól zwierzęcych

### Request:
```bash
curl -X POST http://localhost:5000/api/stt/transcribe \
  -F "audio=@recording.wav" \
  -F "language=pl" \
  -F "analyze=true"
```

### Response:
```json
{
  "status": "success",
  "transcription": "Widzę zbłąkanego psa przy ulicy Głównej 15. Wygląda na wychudzonego i kuleje.",
  "language": "pl",
  "segments": [...],
  
  "animal_fields": {
    "species": "pies",
    "species_label": "Pies",
    "location": "ulicy Głównej 15",
    "incident_types": ["zablakany", "ranny", "glodny"],
    "incident_types_labels": [
      "Zwierzę zbłąkane",
      "Zwierzę ranne",
      "Zwierzę głodne/zaniedbane"
    ],
    "description": "Widzę zbłąkanego psa. Wygląda na wychudzonego i kuleje."
  },
  
  "analysis": {
    "keywords": [...],
    "highlighted_text": [...],
    "priority_suggestion": {...},
    "entities": {...}
  }
}
```

## 2. Pełna analiza

### Request:
```bash
curl -X POST http://localhost:5000/api/stt/analyze-full \
  -F "audio=@recording.wav"
```

### Response:
```json
{
  "status": "success",
  "transcription": {...},
  
  "animal_fields": {
    "species": "pies",
    "species_label": "Pies",
    "location": "ulicy Głównej 15",
    "incident_types": ["zablakany", "ranny"],
    "incident_types_labels": ["Zwierzę zbłąkane", "Zwierzę ranne"],
    "description": "Widzę zbłąkanego psa. Wygląda na wychudzonego i kuleje."
  },
  
  "suggested_form": {
    "species": "pies",
    "species_label": "Pies",
    "location": "ulicy Głównej 15",
    "description": "Widzę zbłąkanego psa. Wygląda na wychudzonego i kuleje.",
    "incident_types": ["zablakany", "ranny"],
    "incident_types_labels": ["Zwierzę zbłąkane", "Zwierzę ranne"],
    "priority": "potencjalnie średni",
    "full_transcription": "Widzę zbłąkanego psa przy ulicy Głównej 15..."
  }
}
```

## 3. Analiza tekstu (bez audio)

### Request:
```bash
curl -X POST http://localhost:5000/api/stt/text-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Ranny kot w parku przy ul. Kwiatowej. Krwawi z łapy."
  }'
```

### Response:
```json
{
  "status": "success",
  "analysis": {...},
  
  "animal_fields": {
    "species": "kot",
    "species_label": "Kot",
    "location": "parku przy ul. Kwiatowej",
    "incident_types": ["ranny"],
    "incident_types_labels": ["Zwierzę ranne"],
    "description": "Ranny kot. Krwawi z łapy."
  }
}
```

## 4. Generowanie formularza

### Request:
```bash
curl -X POST http://localhost:5000/api/form/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Agresywny pies atakuje ludzi na placu Wolności"
  }'
```

### Response:
```json
{
  "status": "success",
  "form": {
    "fields": [
      {
        "name": "species",
        "label": "Gatunek zwierzęcia",
        "type": "select",
        "required": true,
        "value": "pies",
        "options": [
          {"value": "pies", "label": "Pies"},
          {"value": "kot", "label": "Kot"}
        ]
      },
      {
        "name": "location",
        "label": "Lokalizacja",
        "type": "text",
        "required": true,
        "value": "placu Wolności"
      },
      {
        "name": "description",
        "label": "Opis zdarzenia",
        "type": "textarea",
        "required": true,
        "value": "Agresywny pies atakuje ludzi."
      },
      {
        "name": "incident_type",
        "label": "Typ zdarzenia",
        "type": "multiselect",
        "required": false,
        "value": ["agresywny"],
        "options": [...]
      },
      {
        "name": "contact_phone",
        "label": "Telefon kontaktowy",
        "type": "tel",
        "required": false
      },
      {
        "name": "contact_email",
        "label": "Email kontaktowy",
        "type": "email",
        "required": false
      }
    ],
    "suggested_values": {
      "species": "pies",
      "location": "placu Wolności",
      "description": "Agresywny pies atakuje ludzi.",
      "incident_types": ["agresywny"]
    },
    "auto_filled": {
      "species": true,
      "location": true,
      "description": true,
      "incident_types": true
    }
  }
}
```

## 5. Szablon pustego formularza

### Request:
```bash
curl http://localhost:5000/api/form/template
```

### Response:
```json
{
  "status": "success",
  "template": {
    "fields": [
      {
        "name": "species",
        "label": "Gatunek zwierzęcia",
        "type": "select",
        "required": true,
        "options": [
          {"value": "pies", "label": "Pies"},
          {"value": "kot", "label": "Kot"}
        ]
      },
      ...
    ]
  }
}
```

## Rozpoznawane wzorce:

### Gatunki:
- **Pies**: pies, psa, psem, piesek, kundelek, szczeniak
- **Kot**: kot, kota, kotem, kotka, kotek, kocur, kociak

### Typy zdarzeń:
- **zbłąkany**: zbłąkany, zagubiony, bez właściciela, błąka się
- **ranny**: ranny, potrącony, rana, krwawi, kuleje, uraz
- **agresywny**: agresywny, atakuje, szczeka, gryzie, niebezpieczny
- **martwy**: martwy, nie żyje, padł, zwłoki
- **zamknięty**: zamknięty, uwięziony, w pułapce, nie może wyjść
- **głodny**: głodny, wychudzone, wyniszczony, bez jedzenia

### Lokalizacja:
- Ulice: "ul. Główna 15", "przy Głównej", "na ulicy Polnej"
- Miejsca: "w parku", "na placu", "na osiedlu"
- Adresy: rozpoznaje wzorce z nazwami ulic i numerami
