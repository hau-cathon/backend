"""Form generation routes"""
from flask import Blueprint, jsonify, request
from app.utils.animal_field_extractor import AnimalFieldExtractor

form_bp = Blueprint('form', __name__)


@form_bp.route('/generate', methods=['POST'])
def generate_form():
    """
    Generuje dynamiczny formularz na podstawie transkrypcji i analizy
    
    Body:
        text: transkrypcja (WYMAGANE)
        species: gatunek zwierzęcia (opcjonalnie, automatycznie wykrywany)
        location: lokalizacja (opcjonalnie, automatycznie wykrywana)
        incident_types: typy zdarzeń (opcjonalnie, automatycznie wykrywane)
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Brak pola "text"'
            }), 400
        
        text = data['text']
        
        # Automatycznie wyciągnij pola lub użyj podanych
        animal_extractor = AnimalFieldExtractor()
        
        if 'species' in data or 'location' in data:
            # Użyj podanych wartości
            species = data.get('species')
            location = data.get('location')
            incident_types = data.get('incident_types', [])
            description = data.get('description', text)
            animal_count = data.get('animal_count', 1)
        else:
            # Automatyczna ekstrakcja
            animal_fields = animal_extractor.extract_all_fields(text)
            species = animal_fields['species']
            location = animal_fields['location']
            incident_types = animal_fields['incident_types']
            description = animal_fields['description']
            animal_count = animal_fields.get('animal_count', 1)
        
        # POLA FORMULARZA DLA ZGŁOSZEŃ ZWIERZĘCYCH
        form_fields = [
            {
                'name': 'species',
                'label': 'Gatunek zwierzęcia',
                'type': 'select',
                'required': True,  # OBOWIĄZKOWE
                'value': species,
                'options': [
                    {'value': 'pies', 'label': 'Pies'},
                    {'value': 'kot', 'label': 'Kot'}
                ],
                'placeholder': 'Wybierz gatunek'
            },
            {
                'name': 'animal_count',
                'label': 'Liczba zwierząt',
                'type': 'number',
                'required': True,
                'value': animal_count,
                'placeholder': 'np. 1, 2, 3',
                'min': 1,
                'max': 50
            },
            {
                'name': 'location',
                'label': 'Lokalizacja',
                'type': 'text',
                'required': True,
                'value': location or '',
                'placeholder': 'np. ul. Główna 15, Park Centralny'
            },
            {
                'name': 'description',
                'label': 'Opis zdarzenia',
                'type': 'textarea',
                'required': True,
                'value': description,
                'placeholder': 'Opisz szczegóły zdarzenia',
                'rows': 5
            },
            {
                'name': 'incident_type',
                'label': 'Typ zdarzenia',
                'type': 'multiselect',
                'required': False,
                'value': incident_types,
                'options': [
                    {'value': 'zablakany', 'label': 'Zwierzę zbłąkane'},
                    {'value': 'ranny', 'label': 'Zwierzę ranne'},
                    {'value': 'agresywny', 'label': 'Zwierzę agresywne'},
                    {'value': 'martwy', 'label': 'Zwierzę martwe'},
                    {'value': 'zamkniety', 'label': 'Zwierzę zamknięte/uwięzione'},
                    {'value': 'glodny', 'label': 'Zwierzę głodne/zaniedbane'}
                ],
                'placeholder': 'Wybierz typ (można wybrać więcej)'
            },
            {
                'name': 'contact_phone',
                'label': 'Telefon kontaktowy',
                'type': 'tel',
                'required': False,
                'value': '',
                'placeholder': '+48 123 456 789'
            },
            {
                'name': 'contact_email',
                'label': 'Email kontaktowy',
                'type': 'email',
                'required': False,
                'value': '',
                'placeholder': 'email@example.com'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'form': {
                'fields': form_fields,
                'suggested_values': {
                    'species': species,
                    'animal_count': animal_count,
                    'location': location,
                    'description': description,
                    'incident_types': incident_types
                },
                'auto_filled': {
                    'species': species is not None,
                    'animal_count': animal_count is not None,
                    'location': location is not None,
                    'description': True,
                    'incident_types': len(incident_types) > 0
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'Błąd generowania formularza: {str(e)}'
        }), 500


@form_bp.route('/template', methods=['GET'])
def get_form_template():
    """
    Zwraca szablon pustego formularza zgłoszenia zwierzęcia
    """
    template = {
        'fields': [
            {
                'name': 'species',
                'label': 'Gatunek zwierzęcia',
                'type': 'select',
                'required': True,
                'options': [
                    {'value': 'pies', 'label': 'Pies'},
                    {'value': 'kot', 'label': 'Kot'}
                ],
                'placeholder': 'Wybierz gatunek'
            },
            {
                'name': 'animal_count',
                'label': 'Liczba zwierząt',
                'type': 'number',
                'required': True,
                'placeholder': 'np. 1, 2, 3',
                'min': 1,
                'max': 50
            },
            {
                'name': 'location',
                'label': 'Lokalizacja',
                'type': 'text',
                'required': True,
                'placeholder': 'np. ul. Główna 15, Park Centralny'
            },
            {
                'name': 'description',
                'label': 'Opis zdarzenia',
                'type': 'textarea',
                'required': True,
                'placeholder': 'Opisz szczegóły zdarzenia',
                'rows': 5
            },
            {
                'name': 'incident_type',
                'label': 'Typ zdarzenia',
                'type': 'multiselect',
                'required': False,
                'options': [
                    {'value': 'zablakany', 'label': 'Zwierzę zbłąkane'},
                    {'value': 'ranny', 'label': 'Zwierzę ranne'},
                    {'value': 'agresywny', 'label': 'Zwierzę agresywne'},
                    {'value': 'martwy', 'label': 'Zwierzę martwe'},
                    {'value': 'zamkniety', 'label': 'Zwierzę zamknięte/uwięzione'},
                    {'value': 'glodny', 'label': 'Zwierzę głodne/zaniedbane'}
                ],
                'placeholder': 'Wybierz typ'
            },
            {
                'name': 'contact_phone',
                'label': 'Telefon kontaktowy',
                'type': 'tel',
                'required': False,
                'placeholder': '+48 123 456 789'
            },
            {
                'name': 'contact_email',
                'label': 'Email kontaktowy',
                'type': 'email',
                'required': False,
                'placeholder': 'email@example.com'
            }
        ]
    }
    
    return jsonify({
        'status': 'success',
        'template': template
    }), 200
    
    return jsonify({
        'status': 'success',
        'template': template
    }), 200
