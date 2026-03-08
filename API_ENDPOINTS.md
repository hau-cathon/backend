# API Endpoints

## Aktywne endpointy (zarejestrowane w `app/__init__.py`)

### Duplicate routes (`/api/duplicates`)

- `GET /api/duplicates/check/<issue_id>`
Opis: Sprawdza potencjalne duplikaty dla wskazanego zgloszenia. Przyjmuje opcjonalnie `days` i `threshold` w query.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "issue_id": "65f1...",
  "duplicates_found": 2,
  "duplicates": [{"id": "65f2...", "similarity": 0.81}],
  "search_params": {"days_back": 7, "threshold": 0.7, "threshold_percent": 70.0}
}
```

- `POST /api/duplicates/compare`
Opis: Porownuje dwa zgloszenia na podstawie `issue_id_1` i `issue_id_2`.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "issue_1": {"id": "65f1...", "title": "..."},
  "issue_2": {"id": "65f2...", "title": "..."},
  "similarity": 0.74,
  "similarity_percent": 74.0,
  "is_duplicate": true
}
```

### Email routes (`/api/email`)

- `GET /api/email/check`
Opis: Pobiera nieprzeczytane maile i zwraca ich liste.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "count": 3,
  "emails": [{"id": "abc", "subject": "Nowe zgloszenie"}]
}
```

- `POST /api/email/mark-read/<email_id>`
Opis: Oznacza wskazany email jako przeczytany.
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Email oznaczony jako przeczytany"
}
```

### Model routes (`/api/model`)

- `POST /api/model/predict`
Opis: Przewiduje priorytet zgloszenia na podstawie pola `text`.
Przyklad odpowiedzi:
```json
{
  "prediction": 2,
  "priority": "potencjalnie krytyczny",
  "text": "Potracony pies na ulicy...",
  "status": "success"
}
```

### Issue routes (`/api/issues`)

- `GET /api/issues/`
Opis: Zwraca liste zgloszen, z opcjonalnym filtrowaniem (`event_type`, `species`, `status`, `urgency`, `user_id`).
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "count": 12,
  "issues": [{"id": "65f1...", "status": "open"}]
}
```

- `GET /api/issues/<issue_id>`
Opis: Pobiera pojedyncze zgloszenie po ID.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "issue": {"id": "65f1...", "event_type": "bezdomne_zwierze"}
}
```

- `POST /api/issues/`
Opis: Tworzy nowe zgloszenie (wymagane: `event_type`, `species`, `incident_address`).
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Issue created successfully",
  "issue": {"id": "65f1...", "status": "open"}
}
```

- `PUT /api/issues/<issue_id>`
Opis: Aktualizuje pola zgloszenia, w tym status i ewentualne przypisanie.
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Issue updated successfully",
  "issue": {"id": "65f1...", "status": "in_progress"}
}
```

- `DELETE /api/issues/<issue_id>`
Opis: Usuwa wskazane zgloszenie.
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Issue deleted successfully"
}
```

- `GET /api/issues/stats`
Opis: Zwraca statystyki zgloszen (lacznie, po statusach, po typie zdarzenia, pilne).
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "stats": {
    "total": 120,
    "by_status": {"open": 80, "resolved": 20},
    "by_event_type": {"bezdomne_zwierze": 75},
    "urgent": 10
  }
}
```

### Email case type routes (`/api/email-case-types`)

- `GET /api/email-case-types/`
Opis: Zwraca wszystkie typy spraw mailowych (opcjonalnie filtr `is_active`).
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "count": 4,
  "case_types": [{"id": "...", "code": "ANIMAL_RESCUE"}]
}
```

- `GET /api/email-case-types/<case_type_id>`
Opis: Pobiera jeden typ sprawy po ID.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "case_type": {"id": "...", "code": "ANIMAL_RESCUE"}
}
```

- `GET /api/email-case-types/code/<code>`
Opis: Pobiera typ sprawy po kodzie.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "case_type": {"id": "...", "code": "ANIMAL_RESCUE"}
}
```

- `POST /api/email-case-types/`
Opis: Tworzy nowy typ sprawy (`code`, `label` wymagane).
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Email case type created successfully",
  "case_type": {"id": "...", "code": "NEW_CODE"}
}
```

- `PUT /api/email-case-types/<case_type_id>`
Opis: Aktualizuje typ sprawy.
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Email case type updated successfully",
  "case_type": {"id": "...", "label": "Nowa etykieta"}
}
```

- `DELETE /api/email-case-types/<case_type_id>`
Opis: Usuwa typ sprawy.
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Email case type deleted successfully"
}
```

### Email template routes (`/api/email-templates`)

- `GET /api/email-templates/`
Opis: Zwraca szablony emaili z opcjonalnym filtrowaniem (`case_type_id`, `is_active`).
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "count": 5,
  "templates": [{"id": "...", "name": "Interwencja pies"}]
}
```

- `GET /api/email-templates/<template_id>`
Opis: Pobiera jeden szablon po ID.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "template": {"id": "...", "name": "Interwencja pies"}
}
```

- `POST /api/email-templates/`
Opis: Tworzy nowy szablon (`name`, `case_type_id`, `title`, `body` wymagane).
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Email template created successfully",
  "template": {"id": "...", "name": "Nowy szablon"}
}
```

- `PUT /api/email-templates/<template_id>`
Opis: Aktualizuje istniejacy szablon.
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Email template updated successfully",
  "template": {"id": "...", "is_active": true}
}
```

- `DELETE /api/email-templates/<template_id>`
Opis: Usuwa szablon.
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Email template deleted successfully"
}
```

- `POST /api/email-templates/<template_id>/generate`
Opis: Generuje gotowy email na podstawie szablonu i `option_id`.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "template_id": "...",
  "template_name": "Interwencja pies",
  "option_id": "...",
  "final_email": {
    "title": "Temat",
    "body": "Uzupelniona tresc..."
  }
}
```

### Template option routes (`/api/template-options`)

- `GET /api/template-options/`
Opis: Zwraca opcje szablonow, opcjonalnie filtrowane po `animal_type` i `case_type`.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "count": 8,
  "options": [{"id": "...", "animal_type": "pies"}]
}
```

- `GET /api/template-options/<option_id>`
Opis: Pobiera jedna opcje po ID.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "option": {"id": "...", "case_type": "ranny"}
}
```

- `GET /api/template-options/animal-types`
Opis: Zwraca liste unikalnych gatunkow zwierzat z opcji.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "animal_types": ["pies", "kot"]
}
```

- `GET /api/template-options/animal/<animal_type>`
Opis: Zwraca opcje dla konkretnego gatunku.
Przyklad odpowiedzi:
```json
{
  "status": "success",
  "count": 3,
  "options": [{"id": "...", "animal_type": "pies"}]
}
```

- `POST /api/template-options/`
Opis: Tworzy nowa opcje (`animal_type`, `case_type`, `case_label` wymagane).
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Template option created successfully",
  "option": {"id": "...", "case_label": "Pies ranny"}
}
```

- `PUT /api/template-options/<option_id>`
Opis: Aktualizuje opcje szablonu.
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Template option updated successfully",
  "option": {"id": "...", "description": "Nowy opis"}
}
```

- `DELETE /api/template-options/<option_id>`
Opis: Usuwa opcje szablonu.
Przyklad efektu:
```json
{
  "status": "success",
  "message": "Template option deleted successfully"
}
```

## Endpointy obecne w kodzie, ale niepodpiete w `create_app`

Uwaga: ponizsze trasy sa zdefiniowane w plikach route, ale nie sa aktualnie zarejestrowane blueprintem w `app/__init__.py`. Dzialaja dopiero po dodaniu `app.register_blueprint(...)`.

### Form routes (`app/routes/form_routes.py`)

- `POST /generate`
Opis: Buduje dynamiczny formularz na podstawie transkrypcji (`text`) i ekstrakcji pol.
Przyklad efektu: odpowiedz zawiera `form.fields`, `suggested_values`, `auto_filled`.

- `GET /template`
Opis: Zwraca pusty szablon formularza z polami do zgloszenia zwierzecia.
Przyklad efektu: odpowiedz zawiera `template.fields`.

### STT routes (`app/routes/stt_routes.py`)

- `POST /transcribe`
Opis: Transkrybuje audio (`multipart/form-data`) i opcjonalnie analizuje tresc.
Przyklad efektu: odpowiedz zawiera `transcription`, `segments`, oraz opcjonalnie `analysis` i `animal_fields`.

- `POST /analyze-full`
Opis: Pelna analiza audio: transkrypcja + analiza slow kluczowych + formularz sugerowany.
Przyklad efektu: odpowiedz zawiera `transcription`, `keyword_analysis`, `animal_fields`, `ml_analysis`, `suggested_form`.

- `POST /text-analyze`
Opis: Analiza samego tekstu (bez audio).
Przyklad efektu: odpowiedz zawiera `analysis` oraz `animal_fields`.

### Issue duplicate routes (`app/routes/issue_duplicate_routes.py`)

- `POST /issues/<issue_id>/duplicates`
Opis: Oznacza inne zgloszenie jako duplikat (`duplicate_issue_id` w body).
Przyklad efektu: odpowiedz zawiera `message` i obiekt `duplicate`.

- `POST /duplicates/<duplicate_id>/merge`
Opis: Scala zgloszenia duplikatow z lista pol do mergowania.
Przyklad efektu: odpowiedz zawiera zaktualizowany rekord `duplicate`.

- `POST /duplicates/<duplicate_id>/reject`
Opis: Odrzuca relacje duplikatu, opcjonalnie z `reason`.
Przyklad efektu: odpowiedz zawiera `message` i rekord `duplicate` ze statusem odrzucenia.

- `GET /issues/<issue_id>/duplicates`
Opis: Pobiera liste duplikatow dla wskazanego zgloszenia.
Przyklad efektu: odpowiedz zawiera `issue_id` i tablice `duplicates`.

- `GET /duplicates/pending`
Opis: Zwraca duplikaty oczekujace na decyzje.
Przyklad efektu: odpowiedz zawiera `count` i tablice `duplicates`.
